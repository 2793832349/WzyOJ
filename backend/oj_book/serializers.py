from rest_framework import serializers
from .models import Book, Chapter, Section, UserBookProgress
from oj_problem.serializers import ProblemBriefSerializer


class SectionBriefSerializer(serializers.ModelSerializer):
    """小节简要信息"""
    is_completed = serializers.SerializerMethodField()
    
    class Meta:
        model = Section
        fields = ['id', 'title', 'content_type', 'estimated_time', 'order', 'is_completed']
    
    def get_is_completed(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        progress = self.context.get('user_progress')
        if progress:
            return obj in progress.completed_sections.all()
        return False


class SectionDetailSerializer(serializers.ModelSerializer):
    """小节详细信息"""
    problems = ProblemBriefSerializer(many=True, read_only=True)
    chapter_title = serializers.CharField(source='chapter.title', read_only=True)
    book_title = serializers.CharField(source='chapter.book.title', read_only=True)
    book_id = serializers.IntegerField(source='chapter.book.id', read_only=True)
    prev_section = serializers.SerializerMethodField()
    next_section = serializers.SerializerMethodField()
    
    class Meta:
        model = Section
        fields = [
            'id', 'title', 'content_type', 'content', 'video_url', 
            'problems', 'estimated_time', 'order',
            'chapter_title', 'book_title', 'book_id',
            'prev_section', 'next_section',
            'created_at', 'updated_at'
        ]
    
    def get_prev_section(self, obj):
        # 获取同章节的上一个小节
        prev = Section.objects.filter(
            chapter=obj.chapter, order__lt=obj.order
        ).order_by('-order').first()
        
        if not prev:
            # 获取上一章节的最后一个小节
            prev_chapter = Chapter.objects.filter(
                book=obj.chapter.book, order__lt=obj.chapter.order
            ).order_by('-order').first()
            if prev_chapter:
                prev = prev_chapter.sections.order_by('-order').first()
        
        if prev:
            return {'id': prev.id, 'title': prev.title}
        return None
    
    def get_next_section(self, obj):
        # 获取同章节的下一个小节
        next_sec = Section.objects.filter(
            chapter=obj.chapter, order__gt=obj.order
        ).order_by('order').first()
        
        if not next_sec:
            # 获取下一章节的第一个小节
            next_chapter = Chapter.objects.filter(
                book=obj.chapter.book, order__gt=obj.chapter.order
            ).order_by('order').first()
            if next_chapter:
                next_sec = next_chapter.sections.order_by('order').first()
        
        if next_sec:
            return {'id': next_sec.id, 'title': next_sec.title}
        return None


class ChapterSerializer(serializers.ModelSerializer):
    """章节信息"""
    sections = SectionBriefSerializer(many=True, read_only=True)
    section_count = serializers.IntegerField(read_only=True)
    completed_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Chapter
        fields = ['id', 'title', 'description', 'order', 'sections', 'section_count', 'completed_count']
    
    def get_completed_count(self, obj):
        progress = self.context.get('user_progress')
        if progress:
            return progress.completed_sections.filter(chapter=obj).count()
        return 0


class BookListSerializer(serializers.ModelSerializer):
    """书籍列表"""
    chapter_count = serializers.IntegerField(read_only=True)
    section_count = serializers.IntegerField(read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True, default='')
    user_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'description', 'cover', 'difficulty', 'tags',
            'author_name', 'reader_count', 'is_free',
            'chapter_count', 'section_count', 'user_progress',
            'created_at', 'updated_at'
        ]
    
    def get_user_progress(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        try:
            progress = UserBookProgress.objects.get(user=request.user, book=obj)
            return {
                'completed_count': progress.completed_count,
                'total_count': progress.total_count,
                'progress_percent': progress.progress_percent,
                'last_section_id': progress.last_section_id,
            }
        except UserBookProgress.DoesNotExist:
            return None


class BookDetailSerializer(serializers.ModelSerializer):
    """书籍详情"""
    chapters = serializers.SerializerMethodField()
    chapter_count = serializers.IntegerField(read_only=True)
    section_count = serializers.IntegerField(read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True, default='')
    user_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'description', 'cover', 'difficulty', 'tags',
            'author_name', 'reader_count', 'is_free',
            'chapter_count', 'section_count', 'chapters', 'user_progress',
            'created_at', 'updated_at'
        ]
    
    def get_chapters(self, obj):
        request = self.context.get('request')
        user_progress = None
        if request and request.user.is_authenticated:
            try:
                user_progress = UserBookProgress.objects.get(user=request.user, book=obj)
            except UserBookProgress.DoesNotExist:
                pass
        
        return ChapterSerializer(
            obj.chapters.all(), 
            many=True, 
            context={'request': request, 'user_progress': user_progress}
        ).data
    
    def get_user_progress(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        try:
            progress = UserBookProgress.objects.get(user=request.user, book=obj)
            return {
                'completed_count': progress.completed_count,
                'total_count': progress.total_count,
                'progress_percent': progress.progress_percent,
                'last_section_id': progress.last_section_id,
            }
        except UserBookProgress.DoesNotExist:
            return None


class UserBookProgressSerializer(serializers.ModelSerializer):
    """用户阅读进度"""
    book = BookListSerializer(read_only=True)
    completed_count = serializers.IntegerField(read_only=True)
    total_count = serializers.IntegerField(read_only=True)
    progress_percent = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = UserBookProgress
        fields = [
            'id', 'book', 'completed_count', 'total_count', 'progress_percent',
            'last_section', 'started_at', 'last_read_at'
        ]


class BookEditSerializer(serializers.ModelSerializer):
    """书籍编辑序列化器"""
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'description', 'cover', 'difficulty', 'tags',
            'is_published', 'is_free', 'order'
        ]


class ChapterEditSerializer(serializers.ModelSerializer):
    """章节编辑序列化器"""
    class Meta:
        model = Chapter
        fields = ['id', 'book', 'title', 'description', 'order']


class SectionEditSerializer(serializers.ModelSerializer):
    """小节编辑序列化器"""
    problem_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Section
        fields = [
            'id', 'chapter', 'title', 'content_type', 'content',
            'video_url', 'estimated_time', 'order', 'problem_ids'
        ]
    
    def create(self, validated_data):
        problem_ids = validated_data.pop('problem_ids', [])
        section = super().create(validated_data)
        if problem_ids:
            from oj_problem.models import Problem
            problems = Problem.objects.filter(id__in=problem_ids)
            section.problems.set(problems)
        return section
    
    def update(self, instance, validated_data):
        problem_ids = validated_data.pop('problem_ids', None)
        section = super().update(instance, validated_data)
        if problem_ids is not None:
            from oj_problem.models import Problem
            problems = Problem.objects.filter(id__in=problem_ids)
            section.problems.set(problems)
        return section
