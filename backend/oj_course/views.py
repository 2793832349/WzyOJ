import logging

from django.db.models import Q
from django.db.utils import OperationalError, ProgrammingError
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from oj_backend.permissions import Granted, ReadOnly
from oj_problem.models import Problem

from .models import ChapterProblem, Course, CourseChapter, CourseEnrollment, CourseRedeemCode, UserCoursePurchase
from .serializers import CourseChapterSerializer, CourseDetailSerializer, CourseSerializer, CourseRedeemCodeSerializer


logger = logging.getLogger(__name__)


class CoursePagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [Granted | ReadOnly]
    permission = 'class'
    pagination_class = CoursePagination

    def get_serializer_class(self):
        if self.action in ['retrieve']:
            return CourseDetailSerializer
        return CourseSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Course.objects.all()

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(title__icontains=search)

        if not user.is_staff:
            try:
                if user and user.is_authenticated:
                    qs = qs.filter(
                        Q(is_hidden=False) |
                        Q(teacher=user) |
                        Q(enrollments__user=user)
                    ).distinct()
                else:
                    qs = qs.filter(is_hidden=False)
            except (ProgrammingError, OperationalError):
                logger.exception("Failed to build course queryset; falling back to public courses")
                qs = qs.filter(is_hidden=False)
        return qs.order_by('-created_at')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # 限制：付费课程未兑换前不能查看任何内容
        if not instance.is_free:
            user = request.user
            if not user.is_authenticated:
                return Response({'detail': '请先登录后兑换课程'}, status=status.HTTP_403_FORBIDDEN)
            # 管理员、老师、课程创建者可访问
            if not (user.is_staff or 'class' in getattr(user, 'permissions', []) or instance.teacher_id == user.id):
                # 检查是否已购买
                has_purchased = UserCoursePurchase.objects.filter(user=user, course=instance).exists()
                if not has_purchased:
                    return Response({'detail': '您尚未兑换此课程，请先兑换后再查看内容'}, status=status.HTTP_403_FORBIDDEN)
        context = self.get_serializer_context()
        if request.user.is_authenticated:
            course_problem_ids = ChapterProblem.objects.filter(
                chapter__course=instance
            ).values_list('problem_id', flat=True)
            context['solved_problem_ids'] = set(
                request.user.problem_solve.filter(problem_id__in=course_problem_ids)
                .values_list('problem_id', flat=True)
            )
        serializer = self.get_serializer(instance, context=context)
        return Response(serializer.data)

    def perform_create(self, serializer):
        user = self.request.user
        if not (user.is_superuser or user.is_staff or 'class' in user.permissions):
            raise PermissionDenied('只有教师可以创建课程')
        course = serializer.save(teacher=user)
        CourseEnrollment.objects.get_or_create(course=course, user=user)

    def update(self, request, *args, **kwargs):
        course = self.get_object()
        if not (request.user.is_staff or course.teacher_id == request.user.id):
            raise PermissionDenied('只有课程创建者可以编辑课程')
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        course = self.get_object()
        if not (request.user.is_staff or course.teacher_id == request.user.id):
            raise PermissionDenied('只有课程创建者可以编辑课程')
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        course = self.get_object()
        if not (request.user.is_staff or course.teacher_id == request.user.id):
            raise PermissionDenied('只有课程创建者可以删除课程')
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def join(self, request, pk=None):
        course = self.get_object()
        CourseEnrollment.objects.get_or_create(course=course, user=request.user)
        return Response({'message': '加入成功'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def leave(self, request, pk=None):
        course = self.get_object()
        if course.teacher_id == request.user.id:
            return Response({'error': '创建者不能退出课程'}, status=status.HTTP_400_BAD_REQUEST)
        CourseEnrollment.objects.filter(course=course, user=request.user).delete()
        return Response({'message': '退出成功'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def redeem(self, request, pk=None):
        """使用兑换码兑换课程"""
        course = self.get_object()
        code = request.data.get('code', '').strip()
        
        if not code:
            return Response({'detail': '请输入兑换码'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查是否已购买
        if UserCoursePurchase.objects.filter(user=request.user, course=course).exists():
            return Response({'detail': '您已拥有此课程'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 查找兑换码
        try:
            redeem_code = CourseRedeemCode.objects.get(code=code, course=course)
        except CourseRedeemCode.DoesNotExist:
            return Response({'detail': '兑换码无效'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查兑换码是否有效
        if not redeem_code.is_valid:
            return Response({'detail': '兑换码已失效或已用完'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建购买记录
        UserCoursePurchase.objects.create(
            user=request.user,
            course=course,
            redeem_code=redeem_code
        )
        
        # 更新兑换码使用次数
        redeem_code.used_count += 1
        redeem_code.save(update_fields=['used_count'])
        
        # 自动加入课程
        CourseEnrollment.objects.get_or_create(course=course, user=request.user)
        
        return Response({'detail': '兑换成功', 'purchased': True})

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def check_access(self, request, pk=None):
        """检查用户是否有权访问此课程"""
        course = self.get_object()
        
        # 免费课程直接可以访问
        if course.is_free:
            return Response({'has_access': True, 'is_free': True})
        
        # 管理员或老师可以访问
        if request.user.is_staff or 'class' in getattr(request.user, 'permissions', []):
            return Response({'has_access': True, 'is_admin': True})
        
        # 课程创建者可以访问
        if course.teacher_id == request.user.id:
            return Response({'has_access': True, 'is_teacher': True})
        
        # 检查是否已购买
        has_purchased = UserCoursePurchase.objects.filter(user=request.user, course=course).exists()
        return Response({'has_access': has_purchased, 'purchased': has_purchased})


class CourseChapterViewSet(viewsets.ModelViewSet):
    queryset = CourseChapter.objects.all()
    serializer_class = CourseChapterSerializer
    permission_classes = [Granted | ReadOnly]
    permission = 'class'

    logger = logging.getLogger(__name__)

    def check_course_access(self, course):
        """检查用户是否有权访问课程内容"""
        # 免费课程直接可以访问
        if course.is_free:
            return True
        
        # 未登录用户无法访问付费课程
        if not self.request.user.is_authenticated:
            return False
        
        # 管理员可以访问
        if self.request.user.is_staff or 'class' in getattr(self.request.user, 'permissions', []):
            return True
        
        # 课程创建者可以访问
        if course.teacher_id == self.request.user.id:
            return True
        
        # 检查是否已购买
        return UserCoursePurchase.objects.filter(user=self.request.user, course=course).exists()

    def retrieve(self, request, *args, **kwargs):
        """获取章节详情，需要检查付费权限"""
        instance = self.get_object()
        course = instance.course
        # 限制：付费课程未兑换前不能查看任何内容
        if not course.is_free:
            user = request.user
            if not user.is_authenticated:
                return Response({'detail': '请先登录后兑换课程'}, status=status.HTTP_403_FORBIDDEN)
            # 管理员、老师、课程创建者可访问
            if not (user.is_staff or 'class' in getattr(user, 'permissions', []) or course.teacher_id == user.id):
                # 检查是否已购买
                has_purchased = UserCoursePurchase.objects.filter(user=user, course=course).exists()
                if not has_purchased:
                    return Response({'detail': '您尚未兑换此课程，请先兑换后再观看'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self):
        user = self.request.user
        qs = CourseChapter.objects.select_related('course').all()
        course_id = self.request.query_params.get('course_id')
        if course_id:
            qs = qs.filter(course_id=course_id)

        if user.is_staff:
            return qs

        try:
            if user and user.is_authenticated:
                return qs.filter(
                    Q(course__is_hidden=False) |
                    Q(course__teacher=user) |
                    Q(course__enrollments__user=user)
                ).distinct()
            return qs.filter(course__is_hidden=False)
        except (ProgrammingError, OperationalError):
            self.logger.exception("Failed to build chapter queryset; falling back to public chapters")
            return qs.filter(course__is_hidden=False)

    def perform_create(self, serializer):
        course = serializer.validated_data.get('course')
        if not (self.request.user.is_staff or course.teacher_id == self.request.user.id):
            raise PermissionDenied('只有教师可以添加章节')
        serializer.save()
        self._sync_problems(serializer.instance)

    def perform_update(self, serializer):
        chapter = self.get_object()
        if not (self.request.user.is_staff or chapter.course.teacher_id == self.request.user.id):
            raise PermissionDenied('只有教师可以编辑章节')
        serializer.save()
        self._sync_problems(serializer.instance)

    def destroy(self, request, *args, **kwargs):
        chapter = self.get_object()
        if not (request.user.is_staff or chapter.course.teacher_id == request.user.id):
            raise PermissionDenied('只有教师可以删除章节')
        return super().destroy(request, *args, **kwargs)

    def _sync_problems(self, chapter: CourseChapter):
        problem_ids = self.request.data.get('problem_ids', None)
        if problem_ids is None:
            return

        ChapterProblem.objects.filter(chapter=chapter).delete()
        for order, pid in enumerate(problem_ids):
            problem = get_object_or_404(Problem, id=pid)
            ChapterProblem.objects.create(chapter=chapter, problem=problem, order=order)

    @action(detail=True, methods=['post'], url_path='upload-video')
    def upload_video(self, request, pk=None):
        chapter = self.get_object()
        if not (request.user.is_staff or chapter.course.teacher_id == request.user.id):
            raise PermissionDenied('只有教师可以上传视频')
        f = request.FILES.get('file')
        if not f:
            return Response({'error': '未上传文件'}, status=status.HTTP_400_BAD_REQUEST)
        chapter.video = f
        chapter.save(update_fields=['video'])
        serializer = self.get_serializer(chapter)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as exc:
            self.logger.exception('Failed to create course chapter')
            return Response(
                {'error': str(exc), 'type': exc.__class__.__name__},
                status=status.HTTP_400_BAD_REQUEST
            )


import secrets

class CourseRedeemCodeViewSet(viewsets.ModelViewSet):
    """课程兑换码管理视图集"""
    queryset = CourseRedeemCode.objects.all()
    serializer_class = CourseRedeemCodeSerializer
    permission_classes = [Granted]
    permission = 'class'
    
    def get_queryset(self):
        course_id = self.request.query_params.get('course_id')
        queryset = CourseRedeemCode.objects.all().select_related('course', 'created_by')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """批量生成兑换码"""
        course_id = request.data.get('course_id')
        count = int(request.data.get('count', 1))
        max_uses = 1  # 兑换码只能使用一次
        note = request.data.get('note', '')
        
        if not course_id:
            return Response({'detail': '请指定课程'}, status=status.HTTP_400_BAD_REQUEST)
        
        course = get_object_or_404(Course, id=course_id)
        
        codes = []
        for _ in range(min(count, 100)):  # 最多一次生成100个
            code = secrets.token_hex(8).upper()  # 16位随机码
            redeem_code = CourseRedeemCode.objects.create(
                course=course,
                code=code,
                max_uses=max_uses,
                note=note,
                created_by=request.user
            )
            codes.append({
                'id': redeem_code.id,
                'code': code,
                'max_uses': max_uses
            })
        
        return Response({'codes': codes, 'count': len(codes)})
