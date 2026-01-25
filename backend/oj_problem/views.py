import hashlib
import re
import uuid
import shutil
import io
import os
from requests import post as http_post
from zipfile import ZipFile

from django.conf import settings
from django.core.cache import cache
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
