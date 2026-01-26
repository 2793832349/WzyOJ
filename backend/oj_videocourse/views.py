"""
独立的录播课 API 视图
与直播课 API 完全分离
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from .models import VideoCourse, VideoCourseChapter, VideoCourseProgress
from .serializers import (
    VideoCourseDetailSerializer,
    VideoCourseListSerializer,
    VideoCourseChapterSerializer,
    VideoCourseProgressSerializer,
    VideoCourseCreateUpdateSerializer
)
from .tasks import process_videocourse_video


class VideoCourseViewSet(viewsets.ModelViewSet):
    """视频课程视图集 - 完全独立"""
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = VideoCourse.objects.all()
        
        # 按标题搜索
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(title__icontains=search)
        
        # 隐藏课程只对创建者和学生可见
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                models.Q(is_hidden=False) |
                models.Q(creator=self.request.user) |
                models.Q(students=self.request.user)
            ).distinct()
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return VideoCourseListSerializer
        elif self.action == 'retrieve':
            return VideoCourseDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return VideoCourseCreateUpdateSerializer
        return VideoCourseDetailSerializer
    
    def perform_create(self, serializer):
        """创建时自动设置创建者"""
        serializer.save(creator=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def join(self, request, pk=None):
        """加入课程"""
        videocourse = self.get_object()
        videocourse.students.add(request.user)
        return Response({'status': 'joined'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def leave(self, request, pk=None):
        """离开课程"""
        videocourse = self.get_object()
        videocourse.students.remove(request.user)
        return Response({'status': 'left'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def upload_chapter_video(self, request, pk=None):
        """上传章节视频"""
        videocourse = self.get_object()
        chapter_id = request.data.get('chapter_id')
        video_file = request.FILES.get('video')
        
        if not chapter_id or not video_file:
            return Response(
                {'error': '缺少 chapter_id 或 video 文件'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            chapter = VideoCourseChapter.objects.get(
                id=chapter_id,
                videocourse=videocourse
            )
        except VideoCourseChapter.DoesNotExist:
            return Response(
                {'error': '章节不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 保存视频文件
        chapter.video_file = video_file
        chapter.video_status = 'processing'
        chapter.save()
        
        # 启动异步处理任务
        process_videocourse_video.delay(chapter_id=chapter.id)
        
        return Response({
            'status': 'success',
            'message': '视频上传成功，处理中...',
            'chapter_id': chapter.id
        })


class VideoCourseChapterViewSet(viewsets.ModelViewSet):
    """视频课程章节视图集"""
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = VideoCourseChapterSerializer
    
    def get_queryset(self):
        videocourse_id = self.kwargs.get('videocourse_pk')
        return VideoCourseChapter.objects.filter(
            videocourse_id=videocourse_id
        ).order_by('order')
    
    def perform_create(self, serializer):
        """创建章节时自动设置所属课程"""
        videocourse_id = self.kwargs.get('videocourse_pk')
        videocourse = get_object_or_404(VideoCourse, id=videocourse_id)
        serializer.save(videocourse=videocourse)
    
    @action(detail=True, methods=['get'])
    def video_status(self, request, *args, **kwargs):
        """获取视频处理状态"""
        chapter = self.get_object()
        return Response({
            'id': chapter.id,
            'video_status': chapter.video_status,
            'm3u8_playlist': chapter.m3u8_playlist,
            'duration': chapter.duration,
            'resolution': chapter.resolution,
            'bitrate': chapter.bitrate,
            'error_message': chapter.error_message
        })
    
    @action(detail=True, methods=['get'])
    def video_playlist(self, request, *args, **kwargs):
        """获取 m3u8 播放列表"""
        chapter = self.get_object()
        if chapter.video_status != 'completed':
            return Response(
                {'error': '视频未处理完成'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response({
            'm3u8_url': chapter.m3u8_playlist
        })
    
    @action(detail=True, methods=['post'])
    def reprocess_video(self, request, *args, **kwargs):
        """重新处理视频"""
        chapter = self.get_object()
        if not chapter.video_file:
            return Response(
                {'error': '没有视频文件'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        chapter.video_status = 'processing'
        chapter.error_message = ''
        chapter.save()
        
        # 启动异步处理任务
        process_videocourse_video.delay(chapter_id=chapter.id)
        
        return Response({
            'status': 'success',
            'message': '视频重新处理中...'
        })


class VideoCourseProgressViewSet(viewsets.ModelViewSet):
    """视频课程学习进度视图集"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = VideoCourseProgressSerializer
    
    def get_queryset(self):
        return VideoCourseProgress.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def update_progress(self, request):
        """更新学习进度"""
        videocourse_id = request.data.get('videocourse_id')
        chapter_id = request.data.get('chapter_id')
        watched_seconds = request.data.get('watched_seconds', 0)
        is_completed = request.data.get('is_completed', False)
        
        try:
            progress, created = VideoCourseProgress.objects.get_or_create(
                videocourse_id=videocourse_id,
                chapter_id=chapter_id,
                user=request.user
            )
            progress.watched_seconds = watched_seconds
            progress.is_completed = is_completed
            progress.save()
            
            return Response({
                'status': 'success',
                'progress': VideoCourseProgressSerializer(progress).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
