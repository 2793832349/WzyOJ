import subprocess
import tempfile
import os

from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from django.http import HttpResponse, StreamingHttpResponse
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from oj_backend.permissions import (Captcha, Granted,
                                    IsAuthenticatedAndReadCreate,
                                    IsAuthenticatedAndReadOnly)
from oj_contest.models import Contest
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import StatusChoices, Submission
from .serializers import SubmissionDetailSerializer, SubmissionSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def debug_run(request):
    """
    自测运行代码
    """
    language = request.data.get('language', 'cpp')
    source = request.data.get('source', '')
    input_data = request.data.get('input', '')
    
    if not source:
        return Response({'error': '代码不能为空'}, status=400)
    
    # 限制代码长度
    if len(source) > 65536:
        return Response({'error': '代码过长'}, status=400)
    
    # 限制输入长度
    if len(input_data) > 65536:
        return Response({'error': '输入数据过长'}, status=400)
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # 根据语言确定文件名和编译/运行命令
            if language == 'cpp':
                src_file = os.path.join(tmpdir, 'main.cpp')
                exe_file = os.path.join(tmpdir, 'main')
                with open(src_file, 'w') as f:
                    f.write(source)
                # 编译
                compile_result = subprocess.run(
                    ['g++', '-o', exe_file, src_file, '-O2', '-std=c++17'],
                    capture_output=True, text=True, timeout=10
                )
                if compile_result.returncode != 0:
                    return Response({'error': f'编译错误:\n{compile_result.stderr}'})
                run_cmd = [exe_file]
            elif language == 'c':
                src_file = os.path.join(tmpdir, 'main.c')
                exe_file = os.path.join(tmpdir, 'main')
                with open(src_file, 'w') as f:
                    f.write(source)
                # 编译
                compile_result = subprocess.run(
                    ['gcc', '-o', exe_file, src_file, '-O2'],
                    capture_output=True, text=True, timeout=10
                )
                if compile_result.returncode != 0:
                    return Response({'error': f'编译错误:\n{compile_result.stderr}'})
                run_cmd = [exe_file]
            elif language == 'python3':
                src_file = os.path.join(tmpdir, 'main.py')
                with open(src_file, 'w') as f:
                    f.write(source)
                run_cmd = ['python3', src_file]
            else:
                return Response({'error': f'不支持的语言: {language}'}, status=400)
            
            # 运行
            run_result = subprocess.run(
                run_cmd,
                input=input_data,
                capture_output=True,
                text=True,
                timeout=5,
                cwd=tmpdir
            )
            
            output = run_result.stdout
            if run_result.returncode != 0 and run_result.stderr:
                output += f'\n[运行错误]\n{run_result.stderr}'
            
            return Response({'output': output})
    except subprocess.TimeoutExpired:
        return Response({'error': '运行超时 (5秒)'})
    except Exception as e:
        return Response({'error': f'运行失败: {str(e)}'}, status=500)


class SubmissionPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100


def partly_read(file, length, file_size):
    with open(str(file), 'r', encoding='utf-8') as f:
        content = f.read(length)
        if 0 <= length < file_size:
            content += '...'
    return content


def file_iterator(file, chunk_size=512):
    with open(file) as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break


class SubmissionViewSet(ReadOnlyModelViewSet, CreateModelMixin, DestroyModelMixin):
    permission_classes = [Granted | IsAuthenticatedAndReadCreate, Captcha]
    pagination_class = SubmissionPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['problem__id', 'user__username', 'language', 'status']
    ordering_fields = [
        'create_time', 'execute_time', 'execute_memory', 'score'
    ]
    permission = scene = 'submission'

    def get_queryset(self):
        site_settings = cache.get('site_settings')
        if self.permission in self.request.user.permissions:
            queryset = Submission.objects
        elif site_settings.get('forceHideSubmissions'):
            queryset = Submission.objects.filter(user=self.request.user)
        else:
            processing_contest = Contest.objects.filter(
                start_time__lt=timezone.now(), end_time__gt=timezone.now())
            queryset = Submission.objects.exclude(
                Q(_is_hidden=True) | Q(problem___is_hidden=True)
                | Q(problem___hide_submissions=True)
                | Q(problem__contests__contest__in=processing_contest)
            ) | Submission.objects.filter(Q(user=self.request.user))
            queryset = queryset.distinct()
        return queryset.order_by('-id')

    def get_serializer_class(self):
        if self.action == 'list':
            return SubmissionSerializer
        return SubmissionDetailSerializer

    def _oi_feedback_hidden(self, submission: Submission) -> bool:
        perms = getattr(self.request.user, 'permissions', []) if self.request.user.is_authenticated else []
        is_admin = any([
            self.request.user.is_staff,
            'submission' in perms,
            'contest' in perms,
            'problem' in perms,
        ])
        if is_admin:
            return False

        now = timezone.now()
        return (
            Contest.objects
            .filter(
                problems__id=submission.problem_id,
                problem_list_mode=False,
                rule_type='OI',
            )
            .filter(Q(start_time__isnull=True) | Q(start_time__lt=now))
            .filter(Q(end_time__isnull=True) | Q(end_time__gt=now))
            .exists()
        )
    
    def create(self, request, *args, **kwargs):
        """创建提交，带频率限制"""
        user = request.user
        
        # 检查用户是否被封禁
        if not user.is_active:
            raise ValidationError('您的账号已被封禁，无法提交')
        
        # 频率限制：检查最近1分钟内的提交次数
        cache_key = f'submission_rate_limit_{user.id}'
        recent_submissions = cache.get(cache_key, 0)
        
        # 管理员不受限制
        if 'submission' not in user.permissions:
            if recent_submissions >= 6:  # 1分钟内最多6次提交
                raise ValidationError('提交过于频繁，请稍后再试（1分钟内最多6次提交）')
        
        # 增加计数
        cache.set(cache_key, recent_submissions + 1, 60)  # 60秒过期
        
        return super().create(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """删除提交，仅管理员可用"""
        if self.permission not in request.user.permissions:
            return Response(
                {'error': '只有管理员可以删除提交'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True,
            methods=['post'],
            permission_classes=[IsAuthenticatedAndReadCreate],
            url_path='rejudge')
    def rejudge(self, request, pk=None):
        submission = self.get_object()
        if self.permission not in request.user.permissions:
            return Response(
                {'error': '只有管理员可以重新评测'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        submission.status = StatusChoices.PENDING
        submission.score = 0
        submission.execute_time = 0
        submission.execute_memory = 0
        submission.detail = []
        submission.log = ''
        submission.save()

        from .tasks import judge
        judge.delay(
            submission.id, submission.problem.test_case.test_case_id,
            submission.problem.test_case.spj_id
            if submission.problem.test_case.use_spj else None,
            submission.problem.test_case.test_case_config,
            submission.problem.test_case.subcheck_config
            if submission.problem.test_case.use_subcheck else None,
            submission.language, submission.source, {
                'max_cpu_time': submission.problem.time_limit,
                'max_memory': submission.problem.memory_limit * 1024 * 1024,
            })
        return Response({'status': 'rejudging'})

    @action(detail=True,
            methods=['get'],
            permission_classes=[IsAuthenticatedAndReadOnly],
            url_path='status')
    def get_status(self, request, pk=None):
        submission = self.get_object()
        if self._oi_feedback_hidden(submission):
            return Response({'status': StatusChoices.PENDING})
        return Response({'status': submission.status})

    @action(detail=True,
            methods=['get'],
            permission_classes=[IsAuthenticatedAndReadOnly],
            name='Get test point detail',
            url_path=r'test-point/(?P<name>.+)',
            url_name='Test Point Data')
    def test_point(self, request, name, *args, **kwargs):
        instance = self.get_object()

        if self._oi_feedback_hidden(instance):
            return HttpResponse(
                'OI CONTEST HIDES JUDGING FEEDBACK DURING CONTEST WINDOW',
                status=403,
            )

        if not instance.allow_download:
            return HttpResponse(
                'CURRENT SUBMISSION IS NOT ALLOWED TO DOWNLOAD CASE DATA',
                status=403)
        elif instance.status <= StatusChoices.COMPILE_ERROR:
            return HttpResponse(
                'SUBMISSION IN CURRENT STATUS IS NOT ALLOWED TO DOWNLOAD CASE DATA',
                status=403)

        mode = self.request.query_params.get('mode')
        ans_file = settings.TEST_DATA_ROOT / str(
            instance.problem.test_case.test_case_id) / f'{name}.ans'
        in_file = settings.TEST_DATA_ROOT / str(
            instance.problem.test_case.test_case_id) / f'{name}.in'
        out_file = settings.SUBMISSION_ROOT / str(instance.id) / f'{name}.out'

        if mode == 'fetch':
            length = -1
            file = self.request.query_params.get('file')
            file = {'in': in_file, 'out': out_file, 'ans': ans_file}.get(file)
            if file is None:
                return HttpResponse('FILE NOT FOUND', status=404)
            return StreamingHttpResponse(file_iterator(file))
        else:
            length = 255
            ans = _in = out = 'FILE NOT FOUND'
            if ans_file.exists():
                ans = partly_read(ans_file, length, ans_file.stat().st_size)
            if in_file.exists():
                _in = partly_read(in_file, length, in_file.stat().st_size)
            if out_file.exists():
                out = partly_read(out_file, length, out_file.stat().st_size)
            return Response({'ans': ans, 'in': _in, 'out': out})
