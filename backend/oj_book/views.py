from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from django.shortcuts import get_object_or_404

from .models import Book, Chapter, Section, UserBookProgress
from .serializers import (
    BookListSerializer, BookDetailSerializer, BookEditSerializer,
    ChapterSerializer, ChapterEditSerializer,
    SectionDetailSerializer, SectionBriefSerializer, SectionEditSerializer,
    UserBookProgressSerializer
)


class IsBookAdmin(IsAuthenticated):
    """检查用户是否有电子书管理权限"""
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        # 检查用户是否有 class 权限（复用班级管理权限）
        return request.user.is_staff or 'class' in getattr(request.user, 'permissions', [])


class BookViewSet(viewsets.ModelViewSet):
    """电子书视图集"""
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsBookAdmin()]
        return [IsAuthenticatedOrReadOnly()]
    
    def get_queryset(self):
        # 管理员可以看到所有书籍
        if self.request.user.is_authenticated and (
            self.request.user.is_staff or 'class' in getattr(self.request.user, 'permissions', [])
        ):
            queryset = Book.objects.all()
        else:
            queryset = Book.objects.filter(is_published=True)
        
        # 按难度筛选
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        # 按标签筛选
        tag = self.request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(tags__contains=[tag])
        
        return queryset
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BookEditSerializer
        if self.action == 'retrieve':
            return BookDetailSerializer
        return BookListSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def start_reading(self, request, pk=None):
        """开始阅读书籍"""
        book = self.get_object()
        progress, created = UserBookProgress.objects.get_or_create(
            user=request.user,
            book=book
        )
        
        if created:
            # 增加阅读人数
            book.reader_count += 1
            book.save(update_fields=['reader_count'])
        
        # 获取第一个小节
        first_section = Section.objects.filter(chapter__book=book).order_by('chapter__order', 'order').first()
        
        return Response({
            'progress': UserBookProgressSerializer(progress, context={'request': request}).data,
            'first_section_id': first_section.id if first_section else None
        })
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def my_progress(self, request, pk=None):
        """获取我的阅读进度"""
        book = self.get_object()
        try:
            progress = UserBookProgress.objects.get(user=request.user, book=book)
            return Response(UserBookProgressSerializer(progress, context={'request': request}).data)
        except UserBookProgress.DoesNotExist:
            return Response({'detail': '尚未开始阅读'}, status=404)


class ChapterViewSet(viewsets.ModelViewSet):
    """章节视图集"""
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsBookAdmin()]
        return [IsAuthenticatedOrReadOnly()]
    
    def get_queryset(self):
        book_id = self.request.query_params.get('book_id')
        queryset = Chapter.objects.all()
        if book_id:
            queryset = queryset.filter(book_id=book_id)
        return queryset.order_by('order', 'id')
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ChapterEditSerializer
        return ChapterSerializer


class SectionViewSet(viewsets.ModelViewSet):
    """小节视图集"""
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsBookAdmin()]
        return [IsAuthenticatedOrReadOnly()]
    
    def get_queryset(self):
        chapter_id = self.request.query_params.get('chapter_id')
        book_id = self.request.query_params.get('book_id')
        queryset = Section.objects.all()
        if chapter_id:
            queryset = queryset.filter(chapter_id=chapter_id)
        if book_id:
            queryset = queryset.filter(chapter__book_id=book_id)
        return queryset.order_by('chapter__order', 'order', 'id')
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SectionEditSerializer
        return SectionDetailSerializer
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def complete(self, request, pk=None):
        """标记小节为已完成"""
        section = self.get_object()
        book = section.chapter.book
        
        # 获取或创建进度
        progress, created = UserBookProgress.objects.get_or_create(
            user=request.user,
            book=book
        )
        
        if created:
            book.reader_count += 1
            book.save(update_fields=['reader_count'])
        
        # 添加到已完成列表
        progress.completed_sections.add(section)
        progress.last_section = section
        progress.save()
        
        return Response({
            'completed': True,
            'completed_count': progress.completed_count,
            'total_count': progress.total_count,
            'progress_percent': progress.progress_percent
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def uncomplete(self, request, pk=None):
        """取消标记小节为已完成"""
        section = self.get_object()
        book = section.chapter.book
        
        try:
            progress = UserBookProgress.objects.get(user=request.user, book=book)
            progress.completed_sections.remove(section)
            
            return Response({
                'completed': False,
                'completed_count': progress.completed_count,
                'total_count': progress.total_count,
                'progress_percent': progress.progress_percent
            })
        except UserBookProgress.DoesNotExist:
            return Response({'detail': '尚未开始阅读'}, status=404)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def record_read(self, request, pk=None):
        """记录阅读（更新最后阅读位置）"""
        section = self.get_object()
        book = section.chapter.book
        
        progress, created = UserBookProgress.objects.get_or_create(
            user=request.user,
            book=book
        )
        
        if created:
            book.reader_count += 1
            book.save(update_fields=['reader_count'])
        
        progress.last_section = section
        progress.save()
        
        return Response({'recorded': True})


class MyBooksViewSet(viewsets.ReadOnlyModelViewSet):
    """我的书籍（阅读中的书籍）"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserBookProgressSerializer
    
    def get_queryset(self):
        return UserBookProgress.objects.filter(user=self.request.user).select_related('book')
