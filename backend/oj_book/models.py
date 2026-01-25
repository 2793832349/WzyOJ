from django.db import models
from django.utils.translation import gettext_lazy as _
from oj_user.models import User
from oj_problem.models import Problem


class Book(models.Model):
    """电子书"""
    title = models.CharField(_('title'), max_length=200)
    description = models.TextField(_('description'), blank=True, default='')
    cover = models.FileField(_('cover'), upload_to='book_covers/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='authored_books')
    
    # 难度和标签
    DIFFICULTY_CHOICES = [
        ('beginner', '入门'),
        ('easy', '简单'),
        ('medium', '中等'),
        ('hard', '困难'),
    ]
    difficulty = models.CharField(_('difficulty'), max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    tags = models.JSONField(_('tags'), default=list, blank=True)
    
    # 统计信息
    reader_count = models.IntegerField(_('reader count'), default=0)
    
    # 状态
    is_published = models.BooleanField(_('is published'), default=False)
    is_free = models.BooleanField(_('is free'), default=True)
    
    # 时间
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    # 排序
    order = models.IntegerField(_('order'), default=0)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = _('book')
        verbose_name_plural = _('books')

    def __str__(self):
        return self.title
    
    @property
    def chapter_count(self):
        return self.chapters.count()
    
    @property
    def section_count(self):
        return Section.objects.filter(chapter__book=self).count()


class Chapter(models.Model):
    """章节"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(_('title'), max_length=200)
    description = models.TextField(_('description'), blank=True, default='')
    order = models.IntegerField(_('order'), default=0)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = _('chapter')
        verbose_name_plural = _('chapters')

    def __str__(self):
        return f"{self.book.title} - {self.title}"
    
    @property
    def section_count(self):
        return self.sections.count()


class Section(models.Model):
    """小节（具体内容页）"""
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(_('title'), max_length=200)
    
    # 内容类型
    CONTENT_TYPE_CHOICES = [
        ('article', '文章'),
        ('video', '视频'),
        ('problem', '题目'),
    ]
    content_type = models.CharField(_('content type'), max_length=20, choices=CONTENT_TYPE_CHOICES, default='article')
    
    # Markdown 内容
    content = models.TextField(_('content'), blank=True, default='')
    
    # 视频链接（如果是视频类型）
    video_url = models.URLField(_('video url'), blank=True, default='')
    
    # 关联题目（可选）
    problems = models.ManyToManyField(Problem, blank=True, related_name='book_sections')
    
    # 预计阅读时间（分钟）
    estimated_time = models.IntegerField(_('estimated time'), default=5)
    
    order = models.IntegerField(_('order'), default=0)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = _('section')
        verbose_name_plural = _('sections')

    def __str__(self):
        return f"{self.chapter.book.title} - {self.chapter.title} - {self.title}"


class UserBookProgress(models.Model):
    """用户阅读进度"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_progress')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='user_progress')
    
    # 已完成的小节
    completed_sections = models.ManyToManyField(Section, blank=True, related_name='completed_by')
    
    # 最后阅读的小节
    last_section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    
    # 时间
    started_at = models.DateTimeField(_('started at'), auto_now_add=True)
    last_read_at = models.DateTimeField(_('last read at'), auto_now=True)

    class Meta:
        unique_together = ['user', 'book']
        verbose_name = _('user book progress')
        verbose_name_plural = _('user book progress')

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
    
    @property
    def completed_count(self):
        return self.completed_sections.count()
    
    @property
    def total_count(self):
        return Section.objects.filter(chapter__book=self.book).count()
    
    @property
    def progress_percent(self):
        total = self.total_count
        if total == 0:
            return 0
        return int(self.completed_count * 100 / total)
