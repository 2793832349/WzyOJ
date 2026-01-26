"""
录播课 Django Admin 配置
"""

from django.contrib import admin
from .models import VideoCourse, VideoCourseChapter, VideoCourseProgress


@admin.register(VideoCourse)
class VideoCourseAdmin(admin.ModelAdmin):
    """视频课程 Admin"""
    
    list_display = [
        'id', 'title', 'creator', 'student_count',
        'chapter_count', 'is_hidden', 'created_at'
    ]
    list_filter = ['is_hidden', 'created_at']
    search_fields = ['title', 'description', 'creator__username']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['students']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'description', 'cover_image')
        }),
        ('设置', {
            'fields': ('creator', 'is_hidden', 'students')
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def student_count(self, obj):
        return obj.students.count()
    student_count.short_description = '学生数'
    
    def chapter_count(self, obj):
        return obj.chapters.count()
    chapter_count.short_description = '章节数'


@admin.register(VideoCourseChapter)
class VideoCourseChapterAdmin(admin.ModelAdmin):
    """视频课程章节 Admin"""
    
    list_display = [
        'id', 'title', 'videocourse', 'order',
        'video_status', 'duration', 'resolution', 'created_at'
    ]
    list_filter = ['video_status', 'videocourse', 'created_at']
    search_fields = ['title', 'description', 'videocourse__title']
    readonly_fields = ['created_at', 'updated_at', 'duration', 'resolution', 'bitrate']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('videocourse', 'title', 'description', 'order')
        }),
        ('视频文件', {
            'fields': ('video_file', 'video_status')
        }),
        ('视频信息', {
            'fields': (
                'm3u8_playlist', 'duration',
                'resolution', 'bitrate', 'error_message'
            ),
            'classes': ('collapse',)
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VideoCourseProgress)
class VideoCourseProgressAdmin(admin.ModelAdmin):
    """视频课程学习进度 Admin"""
    
    list_display = [
        'id', 'user', 'videocourse', 'chapter',
        'watched_seconds', 'is_completed', 'last_watched_at'
    ]
    list_filter = ['is_completed', 'videocourse', 'last_watched_at']
    search_fields = ['user__username', 'videocourse__title', 'chapter__title']
    readonly_fields = ['last_watched_at']
    
    fieldsets = (
        ('课程信息', {
            'fields': ('videocourse', 'chapter', 'user')
        }),
        ('学习进度', {
            'fields': ('watched_seconds', 'is_completed', 'last_watched_at')
        }),
    )
