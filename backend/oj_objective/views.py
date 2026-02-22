import base64
import io
import json
import mimetypes
import re

from requests import post as http_post
from requests.exceptions import RequestException

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.db.models import Count, Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from oj_backend.permissions import Granted, ReadOnly

from .models import (
    ObjectivePaper,
    ObjectivePaperItem,
    ObjectivePaperSubmission,
    ObjectiveQuestion,
    ObjectiveQuestionTypeChoices,
    ObjectiveSubmission,
)
from .serializers import (
    ObjectivePaperCreateWithQuestionsSerializer,
    ObjectivePaperDetailSerializer,
    ObjectivePaperListSerializer,
    ObjectivePaperSubmitSerializer,
    ObjectiveQuestionDetailSerializer,
    ObjectiveQuestionListSerializer,
    ObjectiveSubmitSerializer,
    build_question_title,
    normalize_answers,
    validate_question_payload,
)


def call_deepseek(messages, timeout=45):
    try:
        r = http_post(
            f"{settings.DEEPSEEK_BASE_URL.rstrip('/')}/chat/completions",
            headers={
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {settings.DEEPSEEK_API_KEY}",
            },
            json={
                'model': settings.DEEPSEEK_MODEL,
                'messages': messages,
                'stream': False,
                'temperature': 0.1,
                'response_format': {'type': 'json_object'},
                'max_tokens': 8192,
            },
            timeout=timeout,
        )
        data = r.json() if r.content else {}
    except RequestException as e:
        return None, {'error': f'AI 请求超时或网络异常: {e}'}
    except Exception as e:
        return None, {'error': f'AI 请求失败: {e}'}

    if r.status_code >= 400:
        err_msg = ''
        if isinstance(data, dict):
            err = data.get('error')
            if isinstance(err, dict):
                err_msg = str(err.get('message') or '')
                if not err_msg:
                    err_msg = json.dumps(err, ensure_ascii=False)
            elif err:
                err_msg = str(err)
        if not err_msg:
            err_msg = f'AI 接口返回状态码 {r.status_code}'
        return None, {'status_code': r.status_code, 'error': err_msg, 'raw': data}
    content = (((data.get('choices') or [{}])[0]).get('message') or {}).get('content')
    return content, data


def extract_first_json_object(raw_text):
    if not raw_text:
        return None

    text = str(raw_text).strip()
    try:
        return json.loads(text)
    except Exception:
        pass

    fence_match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text, re.IGNORECASE)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except Exception:
            pass

    decoder = json.JSONDecoder()
    for start in [m.start() for m in re.finditer(r"\{", text)]:
        try:
            obj, _idx = decoder.raw_decode(text[start:])
            if isinstance(obj, dict):
                return obj
        except Exception:
            continue
    return None


def _is_option_like_line(line, option_keys):
    text = str(line or '').strip()
    if not text:
        return False
    # Common OCR prefixes: checkbox, bullet, bracketed key
    text = re.sub(r'^\s*[□■▢◯○●•·\-]+\s*', '', text)
    for key in option_keys:
        key = str(key or '').strip().upper()
        if not key:
            continue
        pattern = rf'^(?:[\(（【\[]?\s*{re.escape(key)}\s*[\)）】\]]?|{re.escape(key)})\s*[\.、:：\)]?\s+.+$'
        if re.match(pattern, text, re.IGNORECASE):
            return True
    return False


def _contains_cjk(text):
    return bool(re.search(r'[\u4e00-\u9fff]', str(text or '')))


def _strip_code_line_prefix(line):
    text = str(line or '')
    # Remove OCR-style line-number prefixes such as "1 |", "2.", "3)"
    return re.sub(r'^\s*\d+\s*[\|:：.、)）\]】]?\s*', '', text).rstrip()


def _looks_like_cpp_line(line):
    text = _strip_code_line_prefix(line).strip()
    if not text:
        return False
    if len(text) > 180:
        return False
    if _contains_cjk(text):
        return False

    cpp_tokens = (
        '#include', 'using namespace', 'std::', 'cout', 'cin', 'printf', 'scanf',
        'int ', 'long long', 'double ', 'float ', 'char ', 'bool ', 'string ',
        'vector<', 'map<', 'unordered_', 'return ', 'for(', 'for (', 'while(', 'if(',
        'if (', 'else', 'switch(', 'class ', 'struct ', 'namespace ', 'main(', '->'
    )
    if any(tok in text for tok in cpp_tokens):
        return True

    # Assignment-like source lines (including tuple assignment)
    if re.match(r'^[A-Za-z_][A-Za-z0-9_]*(?:\s*,\s*[A-Za-z_][A-Za-z0-9_]*)*\s*=\s*.+$', text):
        return True

    # Fallback: symbol-heavy source style lines
    if any(sym in text for sym in (';', '{', '}', '<<', '>>', '::', '//')) and re.search(r'[A-Za-z_]', text):
        return True
    return False


def _looks_like_inline_code_snippet(text):
    raw = str(text or '').strip()
    if not raw:
        return False
    if len(raw) > 120:
        return False
    if '`' in raw or '```' in raw:
        return False
    if '\n' in raw:
        return False
    if _contains_cjk(raw):
        return False
    if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', raw):
        return False
    if re.fullmatch(r'\d+', raw):
        return False

    if re.search(r'(==|!=|<=|>=|&&|\|\||<<|>>|\+\+|--|->|::|[=+\-*/%(){}\[\],;:])', raw):
        if re.search(r'[A-Za-z0-9_]', raw):
            return True

    token_line = r'[A-Za-z0-9_+\-*/%<>=(){}\[\],.;:]+'
    if re.fullmatch(rf'{token_line}(?:\s+{token_line}){{1,6}}', raw):
        if re.search(r'\d', raw):
            return True

    if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*\s*\(.*\)\s*;?', raw):
        return True

    return False


def _wrap_inline_code_fragments(text):
    result = str(text or '')
    if not result:
        return result

    patterns = [
        r'(?<![`A-Za-z0-9_])(\d+(?:\s*[+\-*/%]\s*\d+){1,})(?![`A-Za-z0-9_])',
        r'(?<![`%A-Za-z0-9_])([A-Za-z_][A-Za-z0-9_]*(?:\s*(?:==|!=|<=|>=|=|\+|\-|\*|/|%|<<|>>|&&|\|\|)\s*[A-Za-z0-9_]+){1,})(?![`A-Za-z0-9_])',
    ]

    def _wrap_plain_segment(segment):
        wrapped = segment
        for pattern in patterns:
            wrapped = re.sub(pattern, lambda m: f"`{m.group(1).strip()}`", wrapped)
        return wrapped

    segments = re.split(r'(```[\s\S]*?```|`[^`\n]*`)', result)
    for i, seg in enumerate(segments):
        if i % 2 == 0:
            segments[i] = _wrap_plain_segment(seg)
    return ''.join(segments)


def _format_cpp_blocks(content):
    text = str(content or '').replace('\r\n', '\n').replace('\r', '\n').strip('\n')
    if not text:
        return text
    if '```' in text:
        return text

    lines = text.split('\n')
    out = []
    i = 0
    n = len(lines)
    while i < n:
        if not _looks_like_cpp_line(lines[i]):
            out.append(lines[i])
            i += 1
            continue

        j = i
        block = []
        while j < n and _looks_like_cpp_line(lines[j]):
            cleaned = _strip_code_line_prefix(lines[j]).strip()
            block.append(cleaned)
            j += 1

        if len(block) >= 2:
            out.append('```cpp')
            out.extend(block)
            out.append('```')
        else:
            only = block[0] if block else lines[i]
            if _looks_like_inline_code_snippet(only):
                out.append(f'`{only}`')
            else:
                out.append(lines[i])
        i = j

    return _wrap_inline_code_fragments('\n'.join(out).strip())


def cleanup_option_text(text):
    value = str(text or '').replace('\r\n', '\n').replace('\r', '\n').strip()
    if not value:
        return ''

    if '\n' in value:
        return _format_cpp_blocks(value)

    if _looks_like_inline_code_snippet(value):
        return f'`{value}`'

    return _wrap_inline_code_fragments(value)


def cleanup_question_content(content, options):
    text = str(content or '').replace('\r\n', '\n').replace('\r', '\n')
    lines = [ln.rstrip() for ln in text.split('\n')]
    option_keys = [str((opt or {}).get('key') or '').upper() for opt in (options or [])]
    option_keys = [k for k in option_keys if k]
    if option_keys:
        lines = [ln for ln in lines if not _is_option_like_line(ln, option_keys)]

    collapsed = '\n'.join(lines)
    collapsed = re.sub(r'\n{3,}', '\n\n', collapsed).strip()
    return _format_cpp_blocks(collapsed)


def _fallback_answers(q_type, options):
    if q_type == 'judge':
        return ['T']
    keys = [str((opt or {}).get('key') or '').strip().upper() for opt in (options or [])]
    keys = [k for k in keys if k]
    return [keys[0]] if keys else []


def infer_answer_with_ai(q_type, content, options):
    try:
        option_rows = []
        for opt in (options or []):
            key = str((opt or {}).get('key') or '').strip().upper()
            text = str((opt or {}).get('text') or '').strip()
            if key:
                option_rows.append({'key': key, 'text': text})

        if not option_rows:
            return []

        system_prompt = (
            '你是客观题答案推断助手。根据题干与选项，推断最可能正确答案。'
            '只输出严格 JSON，不要解释，不要 markdown。\n'
            '输出结构: {"correct_answers":["A"]}'
        )
        user_prompt = (
            f'题型: {q_type}\n'
            f'题干:\n{content or ""}\n\n'
            f'选项:\n{json.dumps(option_rows, ensure_ascii=False)}\n\n'
            '请返回 correct_answers（数组）。单选/判断仅返回 1 个，多选可返回多个。'
        )

        timeout = int(getattr(settings, 'OBJECTIVE_ANSWER_INFER_TIMEOUT', 20) or 20)
        timeout = max(8, min(timeout, 60))

        content_text, _raw = call_deepseek([
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ], timeout=timeout)
        parsed = extract_first_json_object(content_text)
        if not isinstance(parsed, dict):
            return []

        raw_answers = parsed.get('correct_answers')
        if raw_answers is None:
            raw_answers = parsed.get('answer')
        if raw_answers is None:
            return []
        if not isinstance(raw_answers, list):
            raw_answers = [raw_answers]

        valid_keys = {row['key'] for row in option_rows}
        answers = [str(i).strip().upper() for i in raw_answers if str(i).strip()]
        answers = [ans for ans in answers if ans in valid_keys]
        answers = normalize_answers(answers)

        if q_type in {'single', 'judge'} and len(answers) > 1:
            answers = [answers[0]]
        return answers
    except Exception:
        return []


def auto_fill_explanations_with_ai(questions):
    if not settings.DEEPSEEK_API_KEY:
        return
    if not isinstance(questions, list) or not questions:
        return

    pending = []
    for q in questions:
        if not isinstance(q, dict):
            continue
        if str(q.get('explanation') or '').strip():
            continue

        answers = normalize_answers(q.get('correct_answers') or [])
        if not answers:
            continue

        order = int(q.get('order') or 0)
        if order <= 0:
            continue

        options = []
        for opt in (q.get('options') or []):
            if not isinstance(opt, dict):
                continue
            key = str(opt.get('key') or '').strip().upper()
            text = str(opt.get('text') or '').strip()
            if key:
                options.append({'key': key, 'text': text[:220]})

        pending.append({
            'order': order,
            'question': q,
            'payload': {
                'order': order,
                'question_type': str(q.get('question_type') or '').strip(),
                'content': str(q.get('content') or '').strip()[:1000],
                'options': options,
                'correct_answers': answers,
            },
        })

    if not pending:
        return

    timeout = int(getattr(settings, 'OBJECTIVE_EXPLANATION_AI_TIMEOUT', 60) or 60)
    timeout = max(15, min(timeout, 180))
    chunk_size = 12

    system_prompt = (
        '你是客观题解析补全助手。请根据题干、选项和正确答案，生成简短解析。\n'
        '要求：\n'
        '1) 只输出严格 JSON，不要 markdown 外层代码块，不要解释。\n'
        '2) 解析控制在 1-3 句，重点说明为什么正确答案成立。\n'
        '3) 若涉及代码或表达式，使用 markdown 行内代码或 ```cpp 代码块。\n'
        '4) 输出结构：{"items":[{"order":1,"explanation":"..."}]}'
    )

    for i in range(0, len(pending), chunk_size):
        chunk = pending[i:i + chunk_size]
        user_prompt = (
            '请为以下题目补全解析，保持 order 对应：\n'
            f"{json.dumps([row['payload'] for row in chunk], ensure_ascii=False)}"
        )
        content, _raw = call_deepseek([
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ], timeout=timeout)
        parsed = extract_first_json_object(content)
        if not isinstance(parsed, dict):
            continue

        rows = parsed.get('items') or parsed.get('explanations') or []
        if not isinstance(rows, list):
            continue

        explanation_map = {}
        for row in rows:
            if not isinstance(row, dict):
                continue
            try:
                row_order = int(row.get('order') or 0)
            except Exception:
                continue
            if row_order <= 0:
                continue
            explanation = str(row.get('explanation') or row.get('analysis') or '').strip()
            if explanation:
                explanation_map[row_order] = _format_cpp_blocks(explanation)

        for row in chunk:
            if str(row['question'].get('explanation') or '').strip():
                continue
            filled = explanation_map.get(row['order'])
            if filled:
                row['question']['explanation'] = filled


def normalize_ai_question(raw_q, idx):
    if not isinstance(raw_q, dict):
        raise ValueError(f'第 {idx} 题格式无效')

    q_type = str(raw_q.get('question_type') or raw_q.get('type') or 'single').strip().lower()
    type_alias = {
        'single': 'single',
        'single_choice': 'single',
        'radio': 'single',
        '单选': 'single',
        'multiple': 'multiple',
        'multiple_choice': 'multiple',
        'checkbox': 'multiple',
        '多选': 'multiple',
        'judge': 'judge',
        'true_false': 'judge',
        'tf': 'judge',
        '判断': 'judge',
    }
    q_type = type_alias.get(q_type, q_type)
    if q_type not in {'single', 'multiple', 'judge'}:
        q_type = 'single'

    title = str(raw_q.get('title') or '').strip()
    content = str(raw_q.get('content') or raw_q.get('stem') or '').strip()
    explanation = str(raw_q.get('explanation') or raw_q.get('analysis') or '').strip()
    difficulty = int(raw_q.get('difficulty') or 0)
    score = int(raw_q.get('score') or 2)

    if not title:
        title = f'第 {idx} 题'

    options_raw = raw_q.get('options') or []
    normalized_options = []
    if q_type == 'judge':
        normalized_options = [
            {'key': 'T', 'text': '正确'},
            {'key': 'F', 'text': '错误'},
        ]
    else:
        if isinstance(options_raw, dict):
            for k, v in options_raw.items():
                key = str(k).strip().upper()
                if not key:
                    continue
                normalized_options.append({'key': key, 'text': str(v).strip()})
        elif isinstance(options_raw, list):
            for i, opt in enumerate(options_raw):
                if isinstance(opt, dict):
                    key = str(opt.get('key') or chr(ord('A') + i)).strip().upper()
                    text = str(opt.get('text') or opt.get('value') or '').strip()
                else:
                    key = chr(ord('A') + i)
                    text = str(opt).strip()
                normalized_options.append({'key': key, 'text': text})

        if len(normalized_options) < 2:
            normalized_options = [
                {'key': 'A', 'text': ''},
                {'key': 'B', 'text': ''},
            ]

    for opt in normalized_options:
        opt['text'] = cleanup_option_text(opt.get('text'))

    answers_raw = raw_q.get('correct_answers')
    if answers_raw is None:
        answers_raw = raw_q.get('answer')
    if answers_raw is None:
        answers_raw = []
    if not isinstance(answers_raw, list):
        answers_raw = [answers_raw]

    normalized_answers = [str(i).strip().upper() for i in answers_raw if str(i).strip()]

    content = cleanup_question_content(content, normalized_options)
    explanation = _format_cpp_blocks(explanation)

    if not normalized_answers:
        normalized_answers = infer_answer_with_ai(q_type, content, normalized_options)
    if not normalized_answers:
        normalized_answers = _fallback_answers(q_type, normalized_options)

    normalized = {
        'title': title,
        'content': content,
        'question_type': q_type,
        'options': normalized_options,
        'correct_answers': normalized_answers,
        'explanation': explanation,
        'difficulty': max(0, min(10, difficulty)),
        'score': max(1, score),
        'order': idx,
    }

    checked = validate_question_payload({
        'question_type': normalized['question_type'],
        'options': normalized['options'],
        'correct_answers': normalized['correct_answers'],
    })
    normalized['options'] = checked['options']
    normalized['correct_answers'] = checked['correct_answers']
    return normalized


def parse_pdf_text(uploaded_file):
    try:
        from pypdf import PdfReader
    except Exception:
        return None, '缺少 pypdf 依赖，请先安装并重启后端。'

    try:
        reader = PdfReader(uploaded_file)
    except Exception as e:
        return None, f'PDF 读取失败: {e}'

    pages = []
    max_pages = 25
    max_page_chars = 1600
    for i, page in enumerate(reader.pages[:max_pages]):
        try:
            text = page.extract_text() or ''
        except Exception:
            text = ''
        text = text.strip()
        if text:
            pages.append(f"[第{i + 1}页]\n{text[:max_page_chars]}")

    content = '\n\n'.join(pages).strip()
    if content:
        content = content[:35000]
    return content, None


def parse_image_text(uploaded_file):
    try:
        from PIL import Image, ImageOps
        import pytesseract
    except Exception:
        return None, '缺少图片 OCR 依赖，请联系管理员重建后端镜像。'

    try:
        image_bytes = uploaded_file.read()
    except Exception as e:
        return None, f'图片读取失败: {e}'

    if not image_bytes:
        return None, '图片内容为空'

    try:
        img = Image.open(io.BytesIO(image_bytes))
        img = img.convert('RGB')
    except Exception as e:
        return None, f'图片解析失败: {e}'

    gray = ImageOps.grayscale(img)
    bw = gray.point(lambda x: 0 if x < 180 else 255, '1')

    def _ocr(target):
        for lang in ('chi_sim+eng', 'eng'):
            try:
                text = pytesseract.image_to_string(target, lang=lang, config='--oem 3 --psm 6')
                if text and text.strip():
                    return text
            except pytesseract.TesseractNotFoundError:
                return None
            except Exception:
                continue
        return None

    text = _ocr(gray)
    if not text or len(text.strip()) < 30:
        text2 = _ocr(bw)
        if text2 and len(text2.strip()) > len((text or '').strip()):
            text = text2

    if not text or not text.strip():
        return None, 'OCR 未识别到有效文字，请换更清晰截图后重试'

    text = text.replace('\x0c', ' ').strip()
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text[:35000], None


class ObjectivePagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100


class ObjectiveQuestionViewSet(ModelViewSet):
    permission_classes = [Granted | ReadOnly]
    permission = 'problem'
    lookup_value_regex = r'\d+'
    pagination_class = ObjectivePagination
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['id', 'title', 'content']
    ordering_fields = ['id', 'difficulty', 'submission_count', 'accepted_count', 'update_time']
    filterset_fields = ['question_type', 'difficulty']

    def _is_manager(self):
        user = self.request.user
        perms = getattr(user, 'permissions', []) if user and user.is_authenticated else []
        return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser or self.permission in perms))

    def get_queryset(self):
        queryset = ObjectiveQuestion.objects.all().order_by('id')
        if self._is_manager():
            return queryset
        return queryset.filter(_is_hidden=False)

    def get_serializer_class(self):
        if self.action == 'list':
            return ObjectiveQuestionListSerializer
        return ObjectiveQuestionDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['show_answer'] = self._is_manager()
        return context

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path='submit')
    def submit(self, request, pk=None):
        question = self.get_object()
        if question.is_hidden and not self._is_manager():
            return Response({'detail': '题目不可见。'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ObjectiveSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        selected_answers = serializer.validated_data['answers']

        if question.question_type in {ObjectiveQuestionTypeChoices.SINGLE, ObjectiveQuestionTypeChoices.JUDGE} and len(selected_answers) != 1:
            return Response({'answers': ['该题型只能选择一个答案。']}, status=status.HTTP_400_BAD_REQUEST)

        correct_answers = [str(i).strip().upper() for i in (question.correct_answers or [])]
        selected_set = set(selected_answers)
        correct_set = set(correct_answers)
        is_correct = selected_set == correct_set

        already_correct = question.submissions.filter(user=request.user, is_correct=True).exists()

        ObjectiveSubmission.objects.create(
            question=question,
            user=request.user,
            selected_answers=selected_answers,
            is_correct=is_correct,
        )

        question.submission_count += 1
        if is_correct and not already_correct:
            question.accepted_count += 1
        question.save(update_fields=['submission_count', 'accepted_count'])

        return Response({
            'is_correct': is_correct,
            'selected_answers': selected_answers,
            'correct_answers': correct_answers,
            'explanation': question.explanation,
        })


class ObjectivePaperViewSet(ModelViewSet):
    permission_classes = [Granted | ReadOnly]
    permission = 'problem'
    lookup_value_regex = r'\d+'
    pagination_class = ObjectivePagination
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['id', 'title', 'description']
    ordering_fields = ['id', 'create_time', 'update_time', 'pass_score']

    def _is_manager(self):
        user = self.request.user
        perms = getattr(user, 'permissions', []) if user and user.is_authenticated else []
        return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser or self.permission in perms))

    def get_queryset(self):
        queryset = ObjectivePaper.objects.all().annotate(
            question_count=Count('items'),
            total_score=Sum('items__score'),
        ).order_by('-id')
        if self._is_manager():
            return queryset
        return queryset.filter(_is_hidden=False)

    def get_serializer_class(self):
        if self.action == 'list':
            return ObjectivePaperListSerializer
        if self.action == 'create_with_questions':
            return ObjectivePaperCreateWithQuestionsSerializer
        return ObjectivePaperDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['show_answer'] = self._is_manager()
        return context

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=False, methods=['post'], permission_classes=[Granted], url_path='create-with-questions')
    def create_with_questions(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        paper = serializer.save()
        data = ObjectivePaperDetailSerializer(paper, context={'request': request, 'show_answer': True}).data
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[Granted], url_path='update-with-questions')
    def update_with_questions(self, request, pk=None):
        paper = self.get_object()
        serializer = ObjectivePaperCreateWithQuestionsSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        validated = serializer.validated_data
        questions = validated.get('questions', [])

        with transaction.atomic():
            paper.title = validated.get('title', paper.title)
            paper.description = validated.get('description', '')
            paper.pass_score = validated.get('pass_score', paper.pass_score)
            paper._is_hidden = validated.get('_is_hidden', paper._is_hidden)
            paper.updated_by = request.user
            paper.save()

            old_question_ids = list(paper.items.values_list('question_id', flat=True))
            paper.items.all().delete()

            for idx, row in enumerate(questions):
                q_data = dict(row)
                score = q_data.pop('score', 2)
                order = q_data.pop('order', idx + 1)
                q_data['title'] = build_question_title(q_data.get('title'), q_data.get('content'), order)
                q = ObjectiveQuestion.objects.create(created_by=request.user, updated_by=request.user, **q_data)
                ObjectivePaperItem.objects.create(paper=paper, question=q, order=order, score=score)

            if old_question_ids:
                ObjectiveQuestion.objects.filter(id__in=old_question_ids, paper_items__isnull=True).delete()

        data = ObjectivePaperDetailSerializer(paper, context={'request': request, 'show_answer': True}).data
        return Response(data)

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[Granted],
        parser_classes=[MultiPartParser, FormParser],
        url_path="import-pdf",
    )
    def import_pdf(self, request):
        if not settings.DEEPSEEK_API_KEY:
            return Response({'error': 'AI 服务未配置'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        user = request.user
        cache_key = f'objective_pdf_import_rate_{user.id}'
        recent = cache.get(cache_key, 0)
        if recent >= 6:
            return Response({'error': '请求过于频繁，请稍后再试'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        cache.set(cache_key, recent + 1, 60)

        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({'error': '请上传 PDF 文件'}, status=status.HTTP_400_BAD_REQUEST)

        name = str(getattr(uploaded_file, 'name', '') or '').lower()
        if not name.endswith('.pdf'):
            return Response({'error': '仅支持 PDF 文件'}, status=status.HTTP_400_BAD_REQUEST)

        extracted_text, err = parse_pdf_text(uploaded_file)
        if err:
            return Response({'error': err}, status=status.HTTP_400_BAD_REQUEST)
        if not extracted_text or len(extracted_text) < 40:
            return Response({'error': 'PDF 未提取到有效文本，请检查是否为扫描件或图片型 PDF'}, status=status.HTTP_400_BAD_REQUEST)

        user_title = str(request.data.get('title') or '').strip()
        user_pass_score = request.data.get('pass_score')

        system_prompt = (
            '你是 OJ 平台出题助手。'
            '请从给定试卷文本中抽取客观题并返回严格 JSON（不要 markdown，不要解释，不要多余字段）。\n'
            '题型只允许 single/multiple/judge。最多输出 80 题。\n'
            '判断题选项必须是 T/F。\n'
            '重要：content 字段只能保留题干，不得包含 A/B/C/D 选项文本。\n'
            '尽量填写 explanation（1-3 句），用于说明正确答案依据。\n'
            '若题干中有代码，必须使用 Markdown 代码块包裹；C++ 代码块请使用 ```cpp。\n'
            'JSON结构：'
            '{"title":"","description":"","pass_score":60,'
            '"questions":[{"title":"","content":"","question_type":"single",'
            '"options":[{"key":"A","text":""}],"correct_answers":["A"],'
            '"explanation":"","difficulty":0,"score":2}]}'
        )

        user_prompt = (
            f"请抽取以下 PDF 文本中的客观题并转为 JSON。\n"
            f"若题目没有标准答案，correct_answers 置空数组。\n"
            f"content 仅保留题干，不要把选项写进 content。\n"
            f"题干内 C++ 代码请用 ```cpp 代码块包裹。\n"
            f"文本如下：\n\n{extracted_text}"
        )

        ai_timeout = int(getattr(settings, 'OBJECTIVE_PDF_AI_TIMEOUT', 45) or 45)
        ai_timeout = max(10, min(ai_timeout, 55))

        content, raw = call_deepseek([
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ], timeout=ai_timeout)

        if not content:
            retry_prompt = (
                f"请抽取以下 PDF 文本中的客观题并转为 JSON。\n"
                f"若题目没有标准答案，correct_answers 置空数组。\n"
                f"文本如下：\n\n{extracted_text[:12000]}"
            )
            content, retry_raw = call_deepseek([
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': retry_prompt},
            ], timeout=min(ai_timeout, 35))
            if not content:
                detail = ''
                if isinstance(retry_raw, dict):
                    detail = str(retry_raw.get('error') or '')
                if not detail and isinstance(raw, dict):
                    detail = str(raw.get('error') or '')
                return Response(
                    {'error': 'AI 解析失败，请减少 PDF 页数或稍后重试', 'detail': detail or raw},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        parsed = extract_first_json_object(content)
        if not isinstance(parsed, dict):
            repair_system = (
                '你是 JSON 清洗助手。将用户给你的文本转换为严格 JSON 对象输出。'
                '只输出 JSON，不要 markdown，不要解释。'
            )
            repair_user = (
                '请将下面内容整理成如下结构的严格 JSON：'
                '{"title":"","description":"","pass_score":60,"questions":[]}'
                f'\n\n内容：\n{str(content)[:12000]}'
            )
            repaired, repair_raw = call_deepseek([
                {'role': 'system', 'content': repair_system},
                {'role': 'user', 'content': repair_user},
            ], timeout=min(ai_timeout, 25))
            parsed = extract_first_json_object(repaired)
            if not isinstance(parsed, dict):
                detail = ''
                if isinstance(repair_raw, dict):
                    detail = str(repair_raw.get('error') or '')
                return Response(
                    {'error': 'AI 返回内容无法解析为 JSON，请更换更清晰的 PDF 后重试', 'detail': detail},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        raw_questions = parsed.get('questions') or []
        if not isinstance(raw_questions, list) or not raw_questions:
            return Response({'error': 'AI 未识别到题目，请检查 PDF 内容'}, status=status.HTTP_400_BAD_REQUEST)

        questions = []
        errors = []
        for idx, raw_q in enumerate(raw_questions, start=1):
            try:
                q = normalize_ai_question(raw_q, idx)
                questions.append(q)
            except Exception as e:
                errors.append(str(e))

        if not questions:
            return Response({'error': '题目识别失败', 'detail': errors[:10]}, status=status.HTTP_400_BAD_REQUEST)
        auto_fill_explanations_with_ai(questions)

        pass_score = parsed.get('pass_score')
        try:
            pass_score = int(pass_score)
        except Exception:
            pass_score = int(user_pass_score) if str(user_pass_score or '').isdigit() else 60

        draft = {
            'title': user_title or str(parsed.get('title') or '').strip() or 'AI 导入试卷',
            'description': str(parsed.get('description') or '').strip(),
            'pass_score': max(0, pass_score),
            '_is_hidden': False,
            'questions': questions,
        }

        return Response({
            'draft': draft,
            'meta': {
                'question_count': len(questions),
                'ignored_count': max(0, len(raw_questions) - len(questions)),
                'errors': errors[:10],
            },
        })


    @action(
        detail=False,
        methods=["post"],
        permission_classes=[Granted],
        parser_classes=[MultiPartParser, FormParser],
        url_path="import-image",
    )
    def import_image(self, request):
        if not settings.DEEPSEEK_API_KEY:
            return Response({'error': 'AI 服务未配置'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        user = request.user
        cache_key = f'objective_image_import_rate_{user.id}'
        recent = cache.get(cache_key, 0)
        if recent >= 8:
            return Response({'error': '请求过于频繁，请稍后再试'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        cache.set(cache_key, recent + 1, 60)

        uploaded_file = request.FILES.get('file') or request.FILES.get('image')
        if not uploaded_file:
            return Response({'error': '请上传图片文件（字段名 file 或 image）'}, status=status.HTTP_400_BAD_REQUEST)

        name = str(getattr(uploaded_file, 'name', '') or '').lower()
        content_type = str(getattr(uploaded_file, 'content_type', '') or '').lower()
        if not content_type.startswith('image/'):
            guessed, _ = mimetypes.guess_type(name)
            content_type = str(guessed or '').lower()
        if not content_type.startswith('image/'):
            return Response({'error': '仅支持图片文件（jpg/png/webp 等）'}, status=status.HTTP_400_BAD_REQUEST)

        max_size = 10 * 1024 * 1024
        if int(getattr(uploaded_file, 'size', 0) or 0) > max_size:
            return Response({'error': '图片过大，请控制在 10MB 以内'}, status=status.HTTP_400_BAD_REQUEST)

        extracted_text, ocr_err = parse_image_text(uploaded_file)
        if ocr_err:
            return Response({'error': ocr_err}, status=status.HTTP_400_BAD_REQUEST)
        if not extracted_text or len(extracted_text.strip()) < 8:
            return Response({'error': 'OCR 未提取到足够文字，请换清晰截图后重试'}, status=status.HTTP_400_BAD_REQUEST)

        user_title = str(request.data.get('title') or '').strip()
        user_pass_score = request.data.get('pass_score')

        system_prompt = (
            '你是 OJ 平台出题助手。'
            '请从给定试卷文本中抽取客观题并返回严格 JSON（不要 markdown，不要解释，不要多余字段）。\n'
            '题型只允许 single/multiple/judge。最多输出 80 题。\n'
            '判断题选项必须是 T/F。\n'
            '重要：content 字段只能保留题干，不得包含 A/B/C/D 选项文本。\n'
            '尽量填写 explanation（1-3 句），用于说明正确答案依据。\n'
            '若题干中有代码，必须使用 Markdown 代码块包裹；C++ 代码块请使用 ```cpp。\n'
            'JSON结构：'
            '{"title":"","description":"","pass_score":60,'
            '"questions":[{"title":"","content":"","question_type":"single",'
            '"options":[{"key":"A","text":""}],"correct_answers":["A"],'
            '"explanation":"","difficulty":0,"score":2}]}'
        )

        user_prompt = (
            '请抽取以下 OCR 文本中的客观题并转为 JSON。\n'
            '若题目没有标准答案，correct_answers 置空数组。\n'
            'content 仅保留题干，不要把选项写进 content。\n'
            '题干内 C++ 代码请用 ```cpp 代码块包裹。\n'
            f'文本如下：\n\n{extracted_text}'
        )

        ai_timeout = int(getattr(settings, 'OBJECTIVE_IMAGE_AI_TIMEOUT', 180) or 180)
        ai_timeout = max(20, min(ai_timeout, 600))

        content, raw = call_deepseek([
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ], timeout=ai_timeout)

        if not content:
            retry_prompt = (
                '请抽取以下 OCR 文本中的客观题并转为 JSON。\n'
                '若题目没有标准答案，correct_answers 置空数组。\n'
                f'文本如下：\n\n{extracted_text[:12000]}'
            )
            content, retry_raw = call_deepseek([
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': retry_prompt},
            ], timeout=min(ai_timeout, 240))
            if not content:
                detail = ''
                if isinstance(retry_raw, dict):
                    detail = str(retry_raw.get('error') or '')
                if not detail and isinstance(raw, dict):
                    detail = str(raw.get('error') or '')
                return Response(
                    {'error': 'AI 解析失败，请稍后重试', 'detail': detail or raw},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        parsed = extract_first_json_object(content)
        if not isinstance(parsed, dict):
            repair_system = (
                '你是 JSON 清洗助手。将用户给你的文本转换为严格 JSON 对象输出。'
                '只输出 JSON，不要 markdown，不要解释。'
            )
            repair_user = (
                '请将下面内容整理成如下结构的严格 JSON：'
                '{"title":"","description":"","pass_score":60,"questions":[]}'
                f'\n\n内容：\n{str(content)[:12000]}'
            )
            repaired, repair_raw = call_deepseek([
                {'role': 'system', 'content': repair_system},
                {'role': 'user', 'content': repair_user},
            ], timeout=min(ai_timeout, 120))
            parsed = extract_first_json_object(repaired)
            if not isinstance(parsed, dict):
                detail = ''
                if isinstance(repair_raw, dict):
                    detail = str(repair_raw.get('error') or '')
                return Response(
                    {'error': 'AI 返回内容无法解析为 JSON，请换图重试', 'detail': detail},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        raw_questions = parsed.get('questions') or []
        if not isinstance(raw_questions, list) or not raw_questions:
            return Response({'error': 'AI 未识别到题目，请检查图片内容'}, status=status.HTTP_400_BAD_REQUEST)

        questions = []
        errors = []
        for idx, raw_q in enumerate(raw_questions, start=1):
            try:
                q = normalize_ai_question(raw_q, idx)
                questions.append(q)
            except Exception as e:
                errors.append(str(e))

        if not questions:
            return Response({'error': '题目识别失败', 'detail': errors[:10]}, status=status.HTTP_400_BAD_REQUEST)
        auto_fill_explanations_with_ai(questions)

        pass_score = parsed.get('pass_score')
        try:
            pass_score = int(pass_score)
        except Exception:
            pass_score = int(user_pass_score) if str(user_pass_score or '').isdigit() else 60

        draft = {
            'title': user_title or str(parsed.get('title') or '').strip() or 'AI 导入试卷',
            'description': str(parsed.get('description') or '').strip(),
            'pass_score': max(0, pass_score),
            '_is_hidden': False,
            'questions': questions,
        }

        return Response({
            'draft': draft,
            'meta': {
                'question_count': len(questions),
                'ignored_count': max(0, len(raw_questions) - len(questions)),
                'errors': errors[:10],
            },
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path='submit')
    def submit(self, request, pk=None):
        paper = self.get_object()
        if paper.is_hidden and not self._is_manager():
            return Response({'detail': '套卷不可见。'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ObjectivePaperSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw_answers = serializer.validated_data.get('answers', {})

        items = list(paper.items.select_related('question').all())
        max_score = sum(i.score for i in items)
        total_score = 0
        result_detail = []

        normalized_payload = {}
        for k, v in raw_answers.items():
            normalized_payload[str(k)] = normalize_answers(v)

        for item in items:
            q = item.question
            selected = normalized_payload.get(str(q.id), [])
            if q.question_type in {ObjectiveQuestionTypeChoices.SINGLE, ObjectiveQuestionTypeChoices.JUDGE} and len(selected) > 1:
                selected = selected[:1]
            correct = normalize_answers(q.correct_answers)
            is_correct = set(selected) == set(correct)
            if is_correct:
                total_score += item.score
            result_detail.append({
                'question_id': q.id,
                'title': q.title,
                'selected_answers': selected,
                'correct_answers': correct,
                'is_correct': is_correct,
                'score': item.score,
                'earned_score': item.score if is_correct else 0,
            })

        is_pass = total_score >= paper.pass_score

        ObjectivePaperSubmission.objects.create(
            paper=paper,
            user=request.user,
            answers=normalized_payload,
            total_score=total_score,
            max_score=max_score,
            is_pass=is_pass,
        )

        return Response({
            'paper_id': paper.id,
            'total_score': total_score,
            'max_score': max_score,
            'pass_score': paper.pass_score,
            'is_pass': is_pass,
            'detail': result_detail,
        })