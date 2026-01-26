"""
独立的录播课序列化器
与直播课 API 完全分离
"""

from rest_framework import serializers
from .models import VideoCourse, VideoCourseChapter, VideoCourseProgress


class VideoCourseChapterSerializer(serializers.ModelSerializer):
    """视频课程章节序列化器"""
    
    class Meta:
        model = VideoCourseChapter
        fields = [
            'id', 'title', 'description', 'order',
            'video_status', 'm3u8_playlist', 'duration',
            'resolution', 'bitrate', 'error_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class VideoCourseDetailSerializer(serializers.ModelSerializer):
    """视频课程详情序列化器"""
    
    chapters = VideoCourseChapterSerializer(many=True, read_only=True)
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = VideoCourse
        fields = [
            'id', 'title', 'description', 'cover_image',
            'creator', 'creator_name', 'is_hidden',
            'chapters', 'student_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'creator', 'created_at', 'updated_at']
    
    def get_student_count(self, obj):
        return obj.students.count()


class VideoCourseListSerializer(serializers.ModelSerializer):
    """视频课程列表序列化器"""
    
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    chapter_count = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = VideoCourse
        fields = [
            'id', 'title', 'description', 'cover_image',
            'creator_name', 'is_hidden',
            'chapter_count', 'student_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_chapter_count(self, obj):
        return obj.chapters.count()
    
    def get_student_count(self, obj):
        return obj.students.count()


class VideoCourseProgressSerializer(serializers.ModelSerializer):
    """视频课程学习进度序列化器"""
    
    chapter_title = serializers.CharField(source='chapter.title', read_only=True)
    
    class Meta:
        model = VideoCourseProgress
        fields = [
            'id', 'videocourse', 'chapter', 'chapter_title',
            'user', 'watched_seconds', 'is_completed', 'last_watched_at'
        ]
        read_only_fields = ['id', 'user', 'last_watched_at']


class VideoCourseCreateUpdateSerializer(serializers.ModelSerializer):
    """视频课程创建/更新序列化器"""
    
    class Meta:
        model = VideoCourse
        fields = [
            'title', 'description', 'cover_image', 'is_hidden'
        ]
