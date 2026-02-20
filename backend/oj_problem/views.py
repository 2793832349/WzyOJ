import hashlib
import re
import uuid
import shutil
import io
import os
import json
import html
import tempfile
from pathlib import Path
from requests import post as http_post
from zipfile import ZipFile

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, StreamingHttpResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from oj_backend.permissions import (Granted, IsAuthenticatedAndReadOnly,
                                    IsAuthenticatedAndReadCreate)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import (GenericViewSet, ModelViewSet,
                                     ReadOnlyModelViewSet)

from .filters import ProblemFilter
from .models import Problem, Tags, TestCase
from .serializers import (ProblemDetailSerializer, ProblemSerializer,
                          TagsSerializer, TestCaseDetailSerializer,
                          TestCaseUpdateSerializer)
from oj_contest.models import Contest

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


def partly_read(file, length, file_size):
    with open(str(file), 'r', encoding='utf-8') as f:
        content = f.read(length)
        if 0 <= length < file_size:
            content += '...'
    return content


def file_iterator(file, chunk_size=512):
    with open(file, 'rb') as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break


def get_problem_queryset(request):
    if 'problem' in request.user.permissions:
        queryset = Problem.objects
    else:
        processing_contest = Contest.objects.filter(
            start_time__lt=timezone.now(),
            end_time__gt=timezone.now()).filter(users=request.user.id)
        queryset = Problem.objects.exclude(
            Q(_is_hidden=True)) | Problem.objects.filter(
                Q(_is_hidden=True) & Q(contest__in=processing_contest))
        queryset = queryset.distinct()
    return queryset



HYDRO_MANIFEST_FILE_CANDIDATES = (
    'problem.yaml',
    'problem.yml',
    'problem.json',
    'config.yaml',
    'config.yml',
    'config.json',
)
HYDRO_STATEMENT_FILE_CANDIDATES = (
    'problem_zh.md',
    'problem.zh.md',
    'problem_cn.md',
    'problem.zh-cn.md',
    'problem_zh-cn.md',
    'problem_en.md',
    'problem.en.md',
    'statement.md',
    'statement_zh.md',
    'statement_en.md',
    'problem.md',
    'description.md',
    'readme.md',
    'README.md',
)
HYDRO_TESTDATA_DIR_CANDIDATES = (
    'testdata',
    'test_data',
    'tests',
    'testcases',
    'data',
)


def _read_text_with_fallback(path: Path):
    for encoding in ('utf-8', 'utf-8-sig', 'gb18030', 'gbk', 'latin-1'):
        try:
            return path.read_text(encoding=encoding)
        except Exception:
            continue
    return ''


def _safe_zip_member_name(name: str):
    name = str(name or '').replace('\\', '/').strip()
    if not name:
        return ''
    while name.startswith('/'):
        name = name[1:]
    if name.endswith('/'):
        return ''
    normalized = Path(name)
    if '..' in normalized.parts:
        return ''
    return str(normalized)


def _extract_zip_safely(zip_file: ZipFile, target_dir: Path):
    for member in zip_file.infolist():
        safe_name = _safe_zip_member_name(member.filename)
        if not safe_name:
            continue
        dst = target_dir / safe_name
        dst.parent.mkdir(parents=True, exist_ok=True)
        with zip_file.open(member, 'r') as src, dst.open('wb') as out:
            shutil.copyfileobj(src, out)


def _load_manifest(problem_root: Path):
    for candidate in HYDRO_MANIFEST_FILE_CANDIDATES:
        path = problem_root / candidate
        if not path.is_file():
            continue
        raw = _read_text_with_fallback(path).strip()
        if not raw:
            return {}
        suffix = path.suffix.lower()
        try:
            if suffix == '.json':
                data = json.loads(raw)
            else:
                if yaml is None:
                    return {}
                data = yaml.safe_load(raw)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}
    return {}


def _clean_inline_html_text(raw: str):
    text = html.unescape(str(raw or ''))
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _html_to_markdown(raw_text: str):
    if not raw_text:
        return ''

    text = str(raw_text).replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', text, flags=re.IGNORECASE | re.DOTALL)

    def replace_pre_code(match):
        code = html.unescape(match.group(1) or '')
        code = code.strip('\n')
        if not code:
            return '\n\n'
        return f"\n\n```\n{code}\n```\n\n"

    text = re.sub(
        r'<pre[^>]*>\s*<code[^>]*>(.*?)</code>\s*</pre>',
        replace_pre_code,
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    text = re.sub(r'<pre[^>]*>(.*?)</pre>', replace_pre_code, text, flags=re.IGNORECASE | re.DOTALL)

    def replace_heading(match):
        level = int(match.group(1))
        title = _clean_inline_html_text(match.group(2))
        if not title:
            return '\n\n'
        return f"\n\n{'#' * min(max(level, 1), 6)} {title}\n\n"

    text = re.sub(r'<h([1-6])[^>]*>(.*?)</h\1>', replace_heading, text, flags=re.IGNORECASE | re.DOTALL)

    def replace_inline_code(match):
        content = _clean_inline_html_text(match.group(1))
        if not content:
            return ''
        content = content.replace('`', '\\`')
        return f'`{content}`'

    text = re.sub(r'<code[^>]*>(.*?)</code>', replace_inline_code, text, flags=re.IGNORECASE | re.DOTALL)

    def replace_li(match):
        item = _clean_inline_html_text(match.group(1))
        if not item:
            return ''
        return f'- {item}\n'

    text = re.sub(r'<li[^>]*>(.*?)</li>', replace_li, text, flags=re.IGNORECASE | re.DOTALL)

    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</(p|div|section|article|ul|ol|table|thead|tbody|tr)\s*>', '\n', text, flags=re.IGNORECASE)

    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)

    text = '\n'.join(line.rstrip() for line in text.split('\n'))
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def _normalize_statement_text(raw_text: str):
    text = str(raw_text or '').strip()
    if not text:
        return ''
    if re.search(r'<\s*(h[1-6]|p|pre|code|div|br|li|ul|ol|table|section|article)\b', text, flags=re.IGNORECASE):
        converted = _html_to_markdown(text)
        if converted:
            return converted
    return text


def _map_heading_to_section(title: str):
    compact = re.sub(r'[\s:：`~\-—_\|【】\[\]（）()]+', '', str(title or '').strip().lower())
    if not compact:
        return 'description'

    if any(key in compact for key in ('背景', 'background')):
        return 'background'
    if any(key in compact for key in ('输入格式', '输入描述', 'inputformat', 'inputdescription', '输入')):
        return 'input_format'
    if any(key in compact for key in ('输出格式', '输出描述', 'outputformat', 'outputdescription', '输出')):
        return 'output_format'
    if any(key in compact for key in ('提示', 'hint', '数据范围', '约束', 'constraints')):
        return 'hint'
    if any(key in compact for key in ('样例', '示例', 'sample', 'example')):
        return 'samples'
    if any(key in compact for key in ('说明', '描述', '题意', 'problemstatement')):
        return 'description'
    return 'description'


def _extract_markdown_sections(raw_text: str):
    sections = {}
    current = 'description'
    bucket = []

    def flush(section_name: str, lines):
        content = '\n'.join(lines).strip()
        if content:
            sections[section_name] = content

    for line in (raw_text or '').splitlines():
        stripped = line.strip()
        heading_match = re.match(r'^#{1,6}\s*(.+?)\s*$', stripped)
        if heading_match:
            flush(current, bucket)
            bucket = []
            current = _map_heading_to_section(heading_match.group(1))
            continue
        bucket.append(line)
    flush(current, bucket)
    return sections


def _extract_samples_from_text(sample_text: str):
    if not sample_text:
        return []

    pairs = []

    code_blocks = [
        block.strip('\n')
        for block in re.findall(r'```[^\n]*\n(.*?)```', sample_text, flags=re.DOTALL)
        if block.strip()
    ]
    if len(code_blocks) >= 2:
        for idx in range(0, len(code_blocks) - 1, 2):
            pairs.append((code_blocks[idx], code_blocks[idx + 1]))
            if len(pairs) >= 3:
                break
        if pairs:
            return pairs

    lines = sample_text.splitlines()
    current_input = None
    current_output = None

    for line in lines:
        stripped = line.strip().lower()
        if re.match(r'^(样例\s*输入|输入样例|sample\s*input|input)', stripped):
            if current_input is not None and current_output is not None:
                pairs.append((current_input.strip(), current_output.strip()))
            current_input = ''
            current_output = None
            continue
        if re.match(r'^(样例\s*输出|输出样例|sample\s*output|output)', stripped):
            if current_input is None:
                current_input = ''
            current_output = ''
            continue

        if current_output is None:
            if current_input is None:
                continue
            current_input += line + '\n'
        else:
            current_output += line + '\n'

    if current_input is not None and current_output is not None:
        pairs.append((current_input.strip(), current_output.strip()))
    return pairs[:3]


def _parse_time_limit_ms(value):
    if value is None:
        return 1000
    if isinstance(value, (int, float)):
        num = float(value)
        return int(num * 1000) if num <= 20 else int(num)
    text = str(value).strip().lower()
    match = re.search(r'([0-9]+(?:\.[0-9]+)?)', text)
    if not match:
        return 1000
    num = float(match.group(1))
    if 'ms' in text or '毫秒' in text:
        return int(num)
    if 's' in text or '秒' in text:
        return int(num * 1000)
    return int(num * 1000) if num <= 20 else int(num)


def _parse_memory_limit_mb(value):
    if value is None:
        return 128
    if isinstance(value, (int, float)):
        num = float(value)
        if num > 1024 * 1024:
            return max(1, int(num / 1024 / 1024))
        return max(1, int(num))
    text = str(value).strip().lower()
    match = re.search(r'([0-9]+(?:\.[0-9]+)?)', text)
    if not match:
        return 128
    num = float(match.group(1))
    if 'gb' in text or 'gib' in text or text.endswith('g'):
        return max(1, int(num * 1024))
    if 'mb' in text or 'mib' in text or text.endswith('m'):
        return max(1, int(num))
    if 'kb' in text or 'kib' in text or text.endswith('k'):
        return max(1, int(num / 1024))
    if 'byte' in text or re.fullmatch(r'\s*[0-9]+(?:\.[0-9]+)?\s*b\s*', text):
        return max(1, int(num / 1024 / 1024))
    return max(1, int(num))


def _normalize_difficulty(value):
    mapping = {
        'unset': 0,
        'unknown': 0,
        '黑铁': 1,
        'iron': 1,
        'bronze': 2,
        'silver': 3,
        'gold': 4,
        'platinum': 5,
        'diamond': 6,
        'master': 7,
        'king': 8,
    }
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return max(0, min(10, int(value)))
    text = str(value).strip().lower()
    if text in mapping:
        return mapping[text]
    for key, mapped in mapping.items():
        if key in text:
            return mapped
    return 0


def _sanitize_case_name(raw_name: str, used_names: set):
    base = re.sub(r'[^0-9a-zA-Z_.-]+', '_', raw_name.strip().replace('/', '__').replace('\\', '__'))
    base = base.strip('_.') or 'case'
    candidate = base
    index = 2
    while candidate in used_names:
        candidate = f'{base}_{index}'
        index += 1
    used_names.add(candidate)
    return candidate


def _build_case_score(total_case: int, index: int):
    if total_case <= 0:
        return 0
    base = 100 // total_case
    remainder = 100 % total_case
    return base + (1 if index < remainder else 0)


def _resolve_test_data_dir(problem_root: Path, manifest: dict):
    for key in ('testdata', 'test_data', 'tests', 'testcases', 'data'):
        value = manifest.get(key)
        if isinstance(value, str):
            candidate = (problem_root / value).resolve()
            if candidate.is_dir() and str(candidate).startswith(str(problem_root.resolve())):
                if any(f.suffix.lower() == '.in' for f in candidate.rglob('*') if f.is_file()):
                    return candidate

    for dirname in HYDRO_TESTDATA_DIR_CANDIDATES:
        candidate = problem_root / dirname
        if candidate.is_dir() and any(f.suffix.lower() == '.in' for f in candidate.rglob('*') if f.is_file()):
            return candidate

    if any(f.suffix.lower() == '.in' for f in problem_root.iterdir() if f.is_file()):
        return problem_root

    nested = []
    for item in problem_root.rglob('*'):
        if item.is_dir() and any(f.suffix.lower() == '.in' for f in item.iterdir() if f.is_file()):
            nested.append(item)
    if nested:
        nested.sort(key=lambda x: len(x.parts))
        return nested[0]
    return None


def _resolve_manifest_statement_candidates(problem_root: Path, manifest: dict):
    raw_candidates = []

    for key in (
        'statement',
        'statement_file',
        'problem_file',
        'description_file',
        'content_file',
        'markdown',
        'md',
    ):
        value = manifest.get(key)
        if isinstance(value, str) and value.strip():
            raw_candidates.append(value.strip())

    statements = manifest.get('statements')
    if isinstance(statements, dict):
        preferred_locales = ('zh', 'zh-cn', 'zh_hans', 'cn', 'en')
        for locale in preferred_locales:
            value = statements.get(locale)
            if isinstance(value, str) and value.strip():
                raw_candidates.append(value.strip())
        for value in statements.values():
            if isinstance(value, str) and value.strip():
                raw_candidates.append(value.strip())

    normalized = []
    seen = set()
    root = problem_root.resolve()
    for rel in raw_candidates:
        safe_rel = _safe_zip_member_name(rel)
        if not safe_rel:
            continue
        candidate = (problem_root / safe_rel).resolve()
        if not str(candidate).startswith(str(root)):
            continue
        if not candidate.is_file():
            continue
        if candidate.suffix.lower() != '.md':
            continue
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        normalized.append(candidate)
    return normalized


def _resolve_statement_file(problem_root: Path, manifest: dict):
    manifest_candidates = _resolve_manifest_statement_candidates(problem_root, manifest)
    if manifest_candidates:
        return manifest_candidates[0]

    for candidate in HYDRO_STATEMENT_FILE_CANDIDATES:
        path = problem_root / candidate
        if path.is_file():
            return path

    markdown_files = [item for item in problem_root.iterdir() if item.is_file() and item.suffix.lower() == '.md']
    if not markdown_files:
        return None

    keyword_priority = ('problem', 'statement', 'description', '题面', '题目', 'readme')

    def score(path: Path):
        name = path.name.lower()
        for index, key in enumerate(keyword_priority):
            if key in name:
                return (index, len(name), name)
        return (len(keyword_priority), len(name), name)

    markdown_files.sort(key=score)
    return markdown_files[0]


def _collect_case_pairs(test_data_dir: Path):
    case_pairs = []
    for in_file in sorted(test_data_dir.rglob('*.in')):
        rel = in_file.relative_to(test_data_dir)
        base_rel = rel.with_suffix('')
        ans_file = test_data_dir / base_rel.with_suffix('.ans')
        out_file = test_data_dir / base_rel.with_suffix('.out')
        output = ans_file if ans_file.is_file() else out_file if out_file.is_file() else None
        if output is None:
            continue
        case_pairs.append((base_rel.as_posix(), in_file, output))
    return case_pairs


def _is_problem_root(path: Path):
    file_names = {i.name.lower() for i in path.iterdir() if i.is_file()}
    dir_names = {i.name.lower() for i in path.iterdir() if i.is_dir()}

    if any(i in file_names for i in HYDRO_MANIFEST_FILE_CANDIDATES):
        return True
    if any(i in file_names for i in (name.lower() for name in HYDRO_STATEMENT_FILE_CANDIDATES)):
        return True
    if any(i in dir_names for i in HYDRO_TESTDATA_DIR_CANDIDATES):
        return True
    if any(i.suffix.lower() == '.in' for i in path.iterdir() if i.is_file()):
        return True
    return False


def _find_problem_roots(work_root: Path):
    candidates = []
    if _is_problem_root(work_root):
        candidates.append(work_root)

    for item in work_root.iterdir():
        if item.is_dir() and _is_problem_root(item):
            candidates.append(item)

    if not candidates:
        for item in work_root.rglob('*'):
            if item.is_dir() and _is_problem_root(item):
                candidates.append(item)

    candidates = sorted(set(candidates), key=lambda p: (len(p.parts), str(p)))
    selected = []
    for candidate in candidates:
        if any(str(candidate).startswith(str(parent) + os.sep) for parent in selected):
            continue
        selected.append(candidate)
    return selected


def _import_hydro_problem_root(problem_root: Path):
    manifest = _load_manifest(problem_root)

    statement_text = ''
    statement_file = _resolve_statement_file(problem_root, manifest)
    if statement_file is not None:
        statement_text = _read_text_with_fallback(statement_file)

    statement_markdown = _normalize_statement_text(statement_text)
    sections = _extract_markdown_sections(statement_markdown)

    title = str(manifest.get('title') or manifest.get('name') or problem_root.name).strip()
    if not title:
        title = 'Hydro 导入题目'

    manifest_background = _normalize_statement_text(str(manifest.get('background') or ''))
    manifest_description = _normalize_statement_text(str(manifest.get('description') or manifest.get('desc') or ''))
    manifest_input = _normalize_statement_text(str(manifest.get('input') or manifest.get('input_format') or ''))
    manifest_output = _normalize_statement_text(str(manifest.get('output') or manifest.get('output_format') or ''))
    manifest_hint = _normalize_statement_text(str(manifest.get('hint') or manifest.get('tips') or ''))

    background = str(manifest_background or sections.get('background') or '').strip()
    description = str(manifest_description or sections.get('description') or statement_markdown or '').strip()
    input_format = str(manifest_input or sections.get('input_format') or '').strip()
    output_format = str(manifest_output or sections.get('output_format') or '').strip()
    hint = str(manifest_hint or sections.get('hint') or '').strip()

    sample_list = []
    manifest_samples = manifest.get('samples')
    if isinstance(manifest_samples, list):
        for item in manifest_samples:
            if isinstance(item, dict):
                sample_in = str(item.get('input') or item.get('in') or '').strip()
                sample_out = str(item.get('output') or item.get('out') or '').strip()
                if sample_in or sample_out:
                    sample_list.append((sample_in, sample_out))
            if len(sample_list) >= 3:
                break

    if not sample_list:
        sample_list = _extract_samples_from_text(sections.get('samples', ''))

    while len(sample_list) < 3:
        sample_list.append(('', ''))

    raw_tags = manifest.get('tag') or manifest.get('tags') or []
    if isinstance(raw_tags, str):
        raw_tags = [i.strip() for i in re.split(r'[;,，\s]+', raw_tags) if i.strip()]
    elif not isinstance(raw_tags, list):
        raw_tags = []
    tags = []
    for item in raw_tags:
        name = str(item).strip()
        if name:
            tags.append(name[:50])

    test_data_dir = _resolve_test_data_dir(problem_root, manifest)
    if test_data_dir is None:
        raise ValueError('未找到测试数据目录（需要 .in/.out 或 .in/.ans）')

    case_pairs = _collect_case_pairs(test_data_dir)
    if not case_pairs:
        raise ValueError('未找到有效测试点（需要成对 .in 和 .out/.ans）')

    problem = None
    test_case = None
    data_dir = None

    try:
        with transaction.atomic():
            problem = Problem.objects.create(
                title=title[:50],
                background=background,
                description=description,
                input_format=input_format,
                output_format=output_format,
                hint=hint,
                sample_1={'input': sample_list[0][0], 'output': sample_list[0][1]},
                sample_2={'input': sample_list[1][0], 'output': sample_list[1][1]},
                sample_3={'input': sample_list[2][0], 'output': sample_list[2][1]},
                time_limit=_parse_time_limit_ms(
                    manifest.get('time_limit_ms')
                    or manifest.get('time_limit')
                    or manifest.get('timeLimit')
                    or manifest.get('timelimit')
                    or manifest.get('time')
                ),
                memory_limit=_parse_memory_limit_mb(
                    manifest.get('memory_limit_mb')
                    or manifest.get('memory_limit')
                    or manifest.get('memoryLimit')
                    or manifest.get('memory')
                ),
                difficulty=_normalize_difficulty(manifest.get('difficulty')),
            )

            if tags:
                tag_instances = []
                for tag_name in tags:
                    tag_obj, _ = Tags.objects.get_or_create(name=tag_name)
                    tag_instances.append(tag_obj)
                problem.tags.set(tag_instances)

            test_case = TestCase.objects.create(problem=problem)
            data_dir = settings.TEST_DATA_ROOT / str(test_case.test_case_id)
            data_dir.mkdir(parents=True, exist_ok=True)

            config = []
            used_case_names = set()
            for index, (raw_case_name, in_file, out_file) in enumerate(case_pairs):
                case_name = _sanitize_case_name(raw_case_name, used_case_names)
                shutil.copyfile(in_file, data_dir / f'{case_name}.in')
                shutil.copyfile(out_file, data_dir / f'{case_name}.ans')

                file_data = out_file.read_bytes()
                normalized = b'\n'.join(map(bytes.rstrip, file_data.rstrip().splitlines()))
                file_hash = hashlib.md5(normalized).hexdigest()
                (data_dir / f'{case_name}.md5').write_text(file_hash, encoding='utf-8')

                config.append({
                    'name': case_name,
                    'score': _build_case_score(len(case_pairs), index),
                    'subcheck': None,
                })

            test_case.test_case_config = config
            test_case.save(update_fields=['test_case_config'])

    except Exception:
        if data_dir and data_dir.exists():
            shutil.rmtree(data_dir, ignore_errors=True)
        if problem and problem.id:
            problem.delete()
        raise

    return {
        'id': problem.id,
        'title': problem.title,
        'cases': len(case_pairs),
        'root': problem_root.name,
    }


class ProblemPagination(LimitOffsetPagination):
    default_limit = 50
    max_limit = 200


class ProblemViewSet(ModelViewSet):
    permission_classes = [Granted | IsAuthenticatedAndReadOnly]
    permission = 'problem'
    lookup_value_regex = r'\d+'
    pagination_class = ProblemPagination
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['id', 'title']
    ordering_fields = ['id', 'title']
    filterset_class = ProblemFilter

    def get_queryset(self):
        queryset = get_problem_queryset(self.request)
        return queryset.order_by('id')

    def get_serializer_class(self):
        if self.action == 'list':
            return ProblemSerializer
        return ProblemDetailSerializer

    @action(detail=False, methods=['post'], url_path='import-hydro')
    def import_hydro(self, request):
        archive = request.FILES.get('file') or request.FILES.get('archive')
        if not archive:
            return Response({'detail': '请上传 Hydro 导出 zip 文件。'}, status=status.HTTP_400_BAD_REQUEST)

        file_name = str(getattr(archive, 'name', '') or '').lower()
        if file_name and not file_name.endswith('.zip'):
            return Response({'detail': '仅支持 .zip 文件。'}, status=status.HTTP_400_BAD_REQUEST)

        imported = []
        failed = []

        try:
            with tempfile.TemporaryDirectory(prefix='hydro_import_') as tmp_dir:
                tmp_root = Path(tmp_dir)
                with ZipFile(archive, 'r') as zip_file:
                    _extract_zip_safely(zip_file, tmp_root)

                roots = _find_problem_roots(tmp_root)
                if not roots:
                    return Response(
                        {'detail': '压缩包中未识别到 Hydro 题目结构。'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                for root in roots:
                    try:
                        imported.append(_import_hydro_problem_root(root))
                    except Exception as exc:
                        try:
                            root_name = str(root.relative_to(tmp_root))
                        except Exception:
                            root_name = root.name
                        failed.append({'root': root_name, 'error': str(exc)})
        except Exception as exc:
            return Response({'detail': f'导入失败：{exc}'}, status=status.HTTP_400_BAD_REQUEST)

        payload = {
            'imported_count': len(imported),
            'failed_count': len(failed),
            'imported': imported,
            'failed': failed,
        }

        if imported and not failed:
            return Response(payload, status=status.HTTP_201_CREATED)
        if imported and failed:
            return Response(payload, status=status.HTTP_200_OK)
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='adjacent')
    def adjacent(self, request, pk=None):
        """
        获取当前题目的上一题和下一题 ID
        """
        queryset = self.get_queryset()
        current_id = int(pk)
        
        prev_problem = queryset.filter(id__lt=current_id).order_by('-id').first()
        next_problem = queryset.filter(id__gt=current_id).order_by('id').first()
        
        return Response({
            'prev': prev_problem.id if prev_problem else None,
            'next': next_problem.id if next_problem else None,
        })

    @action(detail=True,
            methods=['get', 'delete'],
            url_path='file/(?P<file_name>.+)')
    def problem_file_download(self, request, pk, file_name):
        file = settings.PROBLEM_FILE_ROOT / str(pk) / file_name
        if not file.is_file():
            raise NotFound(_('File not found.'))
        if request.method == 'DELETE':
            file.unlink(missing_ok=True)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return StreamingHttpResponse(
            file_iterator(file),
            content_type='application/octet-stream',
        )

    @action(detail=True, methods=['get'], url_path='download-all-data')
    def download_all_data(self, request, pk):
        """
        批量下载题目的所有测试数据，打包成 ZIP 文件
        """
        problem = self.get_object()
        
        # 测试数据存储在 TEST_DATA_ROOT 下，使用 test_case_id 作为目录名
        if not hasattr(problem, 'test_case') or not problem.test_case:
            raise NotFound(_('No test data found.'))
        
        data_dir = settings.TEST_DATA_ROOT / str(problem.test_case.test_case_id)
        
        if not data_dir.exists():
            raise NotFound(_('No test data found.'))
        
        # 创建内存中的 ZIP 文件
        zip_buffer = io.BytesIO()
        
        with ZipFile(zip_buffer, 'w') as zip_file:
            # 遍历数据目录，添加所有 .in 和 .ans 文件
            for file_path in data_dir.iterdir():
                if file_path.is_file() and (file_path.suffix == '.in' or file_path.suffix == '.ans'):
                    # 添加文件到 ZIP，使用相对路径作为文件名
                    zip_file.write(file_path, arcname=file_path.name)
        
        # 设置文件指针到开始位置
        zip_buffer.seek(0)
        
        # 返回 ZIP 文件
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="problem_{pk}_testdata.zip"'
        return response

    @action(detail=True, methods=['post'], url_path='file')
    def problem_file_upload(self, request, pk):
        file = request.FILES.get('file')
        if not file:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        path = settings.PROBLEM_FILE_ROOT / str(pk) / file.name
        if path.is_file():
            return Response(_('File already exists.'),
                            status=status.HTTP_400_BAD_REQUEST)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(file.read())
        return Response(
            'success',
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True,
            methods=['post'],
            permission_classes=[IsAuthenticatedAndReadCreate],
            url_path='tutor')
    def tutor(self, request, pk=None):
        if not settings.DEEPSEEK_API_KEY:
            return Response({'error': 'AI 服务未配置'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        user = request.user
        if not user.is_active:
            return Response({'error': '您的账号已被封禁，无法使用 AI 辅导'}, status=status.HTTP_403_FORBIDDEN)

        perms = getattr(request.user, 'permissions', []) if request.user.is_authenticated else []
        is_admin = ('problem' in perms) or ('contest' in perms)
        if not is_admin:
            now = timezone.now()
            in_contest = (
                Contest.objects
                .filter(
                    problems__id=pk,
                    problem_list_mode=False,
                )
                .filter(Q(start_time__isnull=True) | Q(start_time__lt=now))
                .filter(Q(end_time__isnull=True) | Q(end_time__gt=now))
                .exists()
            )
            if in_contest:
                return Response({'error': '比赛中无法使用 AI 助教'}, status=status.HTTP_403_FORBIDDEN)

        cache_key = f'ai_tutor_rate_limit_{user.id}'
        recent = cache.get(cache_key, 0)
        if recent >= 30:
            return Response({'error': '请求过于频繁，请稍后再试'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        cache.set(cache_key, recent + 1, 60)

        question = (request.data.get('question') or '').strip()
        if not question:
            return Response({'error': '问题不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        session_id = (request.data.get('session_id') or '').strip()
        reset_session = request.data.get('reset_session') is True
        if not session_id or len(session_id) > 64:
            session_id = uuid.uuid4().hex

        language = (request.data.get('language') or '').strip()
        code = request.data.get('code') or ''
        runtime_error = request.data.get('error') or ''

        instance = self.get_object()
        problem_context_parts = [
            f"题目标题：{instance.title}",
        ]
        if instance.description:
            problem_context_parts.append(f"题目描述：\n{instance.description}")
        if instance.input_format:
            problem_context_parts.append(f"输入格式：\n{instance.input_format}")
        if instance.output_format:
            problem_context_parts.append(f"输出格式：\n{instance.output_format}")
        if instance.hint:
            problem_context_parts.append(f"提示/数据范围：\n{instance.hint}")

        problem_context = "\n\n".join(problem_context_parts)

        code = str(code)
        if len(code) > 8000:
            code = code[:8000]

        runtime_error = str(runtime_error)
        if len(runtime_error) > 2000:
            runtime_error = runtime_error[:2000]

        system_prompt = (
            "你是在线评测平台的助教，只能进行启发式辅导。\n"
            "严格要求：\n"
            "1) 绝不直接给出可通过评测（AC）的完整解法或完整代码。\n"
            "2) 不输出完整函数/完整程序；不要给出可以直接复制提交的代码块；不要输出 ``` 代码围栏。\n"
            "3) 只给思路、关键步骤、必要的局部伪代码（最多 10 行，且必须是不完整的）。\n"
            "4) 先指出学生当前思路/代码可能的问题，再给逐步引导（用提问推动学生自己推导）。\n"
            "5) 若用户强行索要答案/AC 代码，必须拒绝，并改为提供思考方向。"
        )

        user_prompt = (
            f"{problem_context}\n\n"
            f"学生使用语言：{language or '未说明'}\n"
            f"学生代码（可能不完整）：\n{code}\n\n"
            f"报错/错误输出（如果有）：\n{runtime_error}\n\n"
            f"学生问题：{question}\n\n"
            "请按以下结构回复：\n"
            "- 你现在卡住的点（我从你的描述里推测）\n"
            "- 可能的错误原因（列 2-4 条）\n"
            "- 引导步骤（分 3-6 步，每步一句话 + 一个反问）\n"
            "- 一个小练习（让学生自行补全关键部分）"
        )

        session_cache_key = f'ai_tutor_session_{user.id}_{pk}_{session_id}'
        if reset_session:
            cache.delete(session_cache_key)

        history = cache.get(session_cache_key) or []
        if not isinstance(history, list):
            history = []

        def trim_history(items):
            items = [
                i for i in items
                if isinstance(i, dict) and i.get('role') in ('user', 'assistant')
                and isinstance(i.get('content'), str) and i.get('content')
            ]
            if len(items) > 20:
                items = items[-20:]
            total = 0
            trimmed = []
            for msg in reversed(items):
                total += len(msg.get('content', ''))
                trimmed.append(msg)
                if total >= 12000:
                    break
            return list(reversed(trimmed))

        history = trim_history(history)

        def looks_like_ac_code(text: str) -> bool:
            if not text:
                return False
            if '```' in text:
                return True
            if re.search(r"\b#include\b|\bint\s+main\b|\bpublic\s+static\s+void\s+main\b", text):
                return True
            if re.search(r"\bdef\s+\w+\s*\(|\bclass\s+\w+\s*:", text):
                return True
            lines = [i for i in text.splitlines() if i.strip()]
            if len(lines) >= 40 and sum(1 for i in lines if i.strip().endswith((';', '{', '}', ')'))) >= 15:
                return True
            return False

        def call_deepseek(messages):
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
                },
                timeout=45,
            )
            data = r.json() if r.content else {}
            if r.status_code >= 400:
                return None, data
            content = (((data.get('choices') or [{}])[0]).get('message') or {}).get('content')
            return content, data

        messages = [{'role': 'system', 'content': system_prompt}]
        messages.extend(history)
        messages.append({'role': 'user', 'content': user_prompt})

        content, raw = call_deepseek(messages)

        if not content:
            return Response({'error': 'AI 服务调用失败', 'detail': raw}, status=status.HTTP_502_BAD_GATEWAY)

        if looks_like_ac_code(content):
            rewrite_system = (
                "你是在线评测平台的助教，需要把上一条回复改写成只包含思路与引导。"
                "禁止输出任何可直接提交的完整代码；禁止 ``` 代码围栏；禁止输出完整函数/完整程序。"
            )
            rewrite_user = f"请改写下列内容：\n\n{content}"
            rewritten, _raw2 = call_deepseek([
                {'role': 'system', 'content': rewrite_system},
                {'role': 'user', 'content': rewrite_user},
            ])
            if rewritten and not looks_like_ac_code(rewritten):
                content = rewritten
            else:
                content = (
                    "我不能直接提供可通过评测的完整代码/完整解法。\n\n"
                    "你可以把你当前的思路（或关键几行代码）贴出来，并说明哪里不理解。"
                    "我会从：状态定义/转移、边界条件、复杂度、以及你代码的错误点，逐步引导你自己推导出解法。"
                )

        history.append({'role': 'user', 'content': question})
        history.append({'role': 'assistant', 'content': content})
        history = trim_history(history)
        cache.set(session_cache_key, history, 3600)

        return Response({'content': content, 'session_id': session_id})

    @action(
        detail=True,
        methods=['get', 'put', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='blockly-draft',
    )
    def blockly_draft(self, request, pk=None):
        base_dir = settings.MEDIA_ROOT / 'blockly_drafts' / str(request.user.id)
        base_dir.mkdir(parents=True, exist_ok=True)
        draft_path = base_dir / f'{pk}.xml'

        if request.method == 'GET':
            if not draft_path.is_file():
                return Response({'workspace_xml': ''})
            return Response({'workspace_xml': draft_path.read_text(encoding='utf-8')})

        if request.method == 'DELETE':
            draft_path.unlink(missing_ok=True)
            return Response(status=status.HTTP_204_NO_CONTENT)

        workspace_xml = request.data.get('workspace_xml')
        if workspace_xml is None:
            return Response({'error': 'workspace_xml is required'}, status=status.HTTP_400_BAD_REQUEST)
        workspace_xml = str(workspace_xml)
        if len(workspace_xml) > 300_000:
            return Response({'error': 'workspace_xml is too large'}, status=status.HTTP_400_BAD_REQUEST)
        draft_path.write_text(workspace_xml, encoding='utf-8')
        return Response({'workspace_xml': workspace_xml})


class DataViewSet(GenericViewSet, RetrieveModelMixin):
    queryset = TestCase.objects.all()
    permission_classes = [Granted]
    permission = 'problem'
    lookup_field = 'problem__id'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TestCaseDetailSerializer
        else:
            return TestCaseUpdateSerializer

    @action(methods=['get'], detail=True, url_path='file/(?P<file>.+)')
    def fetch_file(self, request, file, *args, **kwargs):
        instance = self.get_object()
        partly = request.query_params.get('partly') == 'true'
        length = 255 if partly else -1
        test_case_file = settings.TEST_DATA_ROOT / str(
            instance.test_case_id) / file
        if not test_case_file.is_file():
            raise NotFound(_('File not found.'))
        response = HttpResponse(
            partly_read(
                test_case_file,
                length,
                test_case_file.stat().st_size,
            ))
        response['Content-Type'] = 'text/plain'
        return response

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK:
            openapi.Response(
                description='',
                schema=TestCaseDetailSerializer,
            )
        })
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data_dir = settings.TEST_DATA_ROOT / str(instance.test_case_id)
        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        delete_cases = serializer.validated_data.get('delete_cases')
        if delete_cases:
            for case in delete_cases:
                (data_dir / f'{case}.in').unlink(missing_ok=True)
                (data_dir / f'{case}.ans').unlink(missing_ok=True)
                (data_dir / f'{case}.md5').unlink(missing_ok=True)
        test_cases_file = serializer.validated_data.get('test_cases')
        if test_cases_file and test_cases_file.size > 0:
            test_cases = ZipFile(test_cases_file, 'r')
            test_cases.extractall(data_dir)
            for file in test_cases.namelist():
                file_name, file_ext = file.rsplit('.', 1)
                if file_ext == 'ans':
                    file_data = test_cases.read(file)
                    file_data = b'\n'.join(
                        map(bytes.rstrip,
                            file_data.rstrip().splitlines()))
                    file_hash = hashlib.md5(file_data).hexdigest()
                    (data_dir / f'{file_name}.md5').write_text(
                        file_hash, encoding='utf-8')
        use_spj = serializer.validated_data.get('use_spj')
        if use_spj:
            spj_source = serializer.validated_data.get('spj_source')
            spj_dir = settings.SPJ_ROOT / str(instance.spj_id)
            spj_dir.mkdir(exist_ok=True)
            (spj_dir / 'checker').unlink(missing_ok=True)
            (spj_dir / 'checker.cpp').write_text(spj_source, encoding='utf-8')
            testlib_dst = settings.SPJ_ROOT / 'testlib.h'
            if not testlib_dst.exists():
                testlib_src = settings.BASE_DIR / 'judge_data/spj/testlib.h'
                if testlib_src.is_file():
                    shutil.copyfile(testlib_src, testlib_dst)
        serializer.save()
        serializer = TestCaseDetailSerializer(serializer.data)
        return Response(serializer.data)


class TagsViewSet(ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    permission_classes = [Granted | IsAuthenticatedAndReadOnly]
    permission = 'problem'
    serializer_class = TagsSerializer

    def create(self, request, *args, **kwargs):
        create = request.data.get('create')
        for i in create:
            Tags.objects.get_or_create(name=i)
        update = request.data.get('update')
        for i in update:
            Tags.objects.filter(id=i['id']).update(name=i['name'])
        delete = request.data.get('delete')
        for i in delete:
            Tags.objects.filter(id=i).delete()
        data = TagsSerializer(Tags.objects.order_by('id'), many=True).data
        cache.set('tags', data, None)
        return Response(data)

    def list(self, request, *args, **kwargs):
        data = cache.get('tags')
        if not data:
            data = TagsSerializer(Tags.objects.order_by('id'), many=True).data
            cache.set('tags', data, None)
        return Response(data)
