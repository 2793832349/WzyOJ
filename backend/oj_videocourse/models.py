"""
独立的录播课（视频课程）模型
完全与直播课系统分离
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class VideoCourse(models.Model):
    """视频课程模型 - 完全独立于 Course"""
    
    title = models.CharField(max_length=255, verbose_name='课程名称')
    description = models.TextField(blank=True, verbose_name='课程描述')
    cover_image = models.ImageField(
        upload_to='videocourse_covers/',
        blank=True,
        null=True,
        verbose_name='课程封面'
    )
    
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_videocourses',
        verbose_name='创建者'
    )
    
    is_hidden = models.BooleanField(
        default=False,
        verbose_name='隐藏课程'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    # 学生成员
    students = models.ManyToManyField(
        User,
        related_name='enrolled_videocourses',
        blank=True,
        verbose_name='学生成员'
    )
    
    class Meta:
        db_table = 'videocourse_videocourse'
        ordering = ['-created_at']
        verbose_name = '视频课程'
        verbose_name_plural = '视频课程'
    
    def __str__(self):
        return self.title


class VideoCourseChapter(models.Model):
    """视频课程章节模型 - 完全独立于 CourseChapter"""
    
    # 状态选择
    VIDEO_STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '处理失败'),
    ]
    
    videocourse = models.ForeignKey(
        VideoCourse,
        on_delete=models.CASCADE,
        related_name='chapters',
        verbose_name='所属课程'
    )
    
    title = models.CharField(max_length=255, verbose_name='章节标题')
    description = models.TextField(blank=True, verbose_name='章节描述')
    order = models.IntegerField(default=0, verbose_name='顺序')
    
    # 视频相关字段
    video_file = models.FileField(
        upload_to='videocourse_videos/',
        null=True,
        blank=True,
        verbose_name='原始视频文件'
    )
    
    video_status = models.CharField(
        max_length=20,
        choices=VIDEO_STATUS_CHOICES,
        default='pending',
        verbose_name='视频处理状态'
    )
    
    m3u8_playlist = models.TextField(
        blank=True,
        verbose_name='HLS 播放列表 URL'
    )
    
    duration = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='视频时长（秒）'
    )
    
    resolution = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='分辨率'
    )
    
    bitrate = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='比特率'
    )
    
    error_message = models.TextField(
        blank=True,
        verbose_name='处理错误信息'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    class Meta:
        db_table = 'videocourse_videocourseChapter'
        ordering = ['order', 'created_at']
        verbose_name = '视频课程章节'
        verbose_name_plural = '视频课程章节'
        unique_together = ['videocourse', 'order']
    
    def __str__(self):
        return f"{self.videocourse.title} - {self.title}"


class VideoCourseProgress(models.Model):
    """视频课程学习进度模型 - 完全独立"""
    
    videocourse = models.ForeignKey(
        VideoCourse,
        on_delete=models.CASCADE,
        related_name='progresses',
        verbose_name='课程'
    )
    
    chapter = models.ForeignKey(
        VideoCourseChapter,
        on_delete=models.CASCADE,
        related_name='progresses',
        verbose_name='章节'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='videocourse_progresses',
        verbose_name='用户'
    )
    
    watched_seconds = models.IntegerField(
        default=0,
        verbose_name='已观看时长（秒）'
    )
    
    is_completed = models.BooleanField(
        default=False,
        verbose_name='是否完成'
    )
    
    last_watched_at = models.DateTimeField(
        auto_now=True,
        verbose_name='最后观看时间'
    )
    
    class Meta:
        db_table = 'videocourse_progress'
        unique_together = ['videocourse', 'chapter', 'user']
        verbose_name = '视频课程学习进度'
        verbose_name_plural = '视频课程学习进度'
    
    def __str__(self):
        return f"{self.user.username} - {self.chapter.title}"
