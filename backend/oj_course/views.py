import logging

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from oj_backend.permissions import Granted, IsAuthenticatedAndReadOnly
from oj_problem.models import Problem

from .models import ChapterProblem, Course, CourseChapter, CourseEnrollment
from .serializers import CourseChapterSerializer, CourseDetailSerializer, CourseSerializer


class CoursePagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [Granted | IsAuthenticatedAndReadOnly]
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
            qs = qs.filter(
                Q(is_hidden=False) |
                Q(teacher=user) |
                Q(enrollments__user=user)
            ).distinct()
        return qs.order_by('-created_at')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
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


class CourseChapterViewSet(viewsets.ModelViewSet):
    queryset = CourseChapter.objects.all()
    serializer_class = CourseChapterSerializer
    permission_classes = [Granted | IsAuthenticatedAndReadOnly]
    permission = 'class'

    logger = logging.getLogger(__name__)

    def get_queryset(self):
        user = self.request.user
        qs = CourseChapter.objects.select_related('course').all()
        course_id = self.request.query_params.get('course_id')
        if course_id:
            qs = qs.filter(course_id=course_id)

        if user.is_staff:
            return qs

        return qs.filter(
            Q(course__is_hidden=False) |
            Q(course__teacher=user) |
            Q(course__enrollments__user=user)
        ).distinct()

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
