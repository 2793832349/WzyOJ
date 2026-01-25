from rest_framework import serializers

from oj_problem.serializers import ProblemSerializer
from oj_user.models import User

from .models import Course, CourseChapter, CourseEnrollment, ChapterProblem, VideoProcessingStatus


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'real_name', 'student_id']


class CourseChapterProblemSerializer(serializers.ModelSerializer):
    problem = ProblemSerializer(read_only=True)
    problem_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ChapterProblem
        fields = ['id', 'problem', 'problem_id', 'order']
        read_only_fields = ['id']


class VideoPlaylistSerializer(serializers.Serializer):
    """视频播放列表序列化器"""
    m3u8_url = serializers.CharField()
    segments_url = serializers.CharField()
    duration = serializers.IntegerField()
    resolution = serializers.CharField()


class CourseChapterSerializer(serializers.ModelSerializer):
    problems = CourseChapterProblemSerializer(source='chapter_problems', many=True, read_only=True)
    problem_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    video_url = serializers.SerializerMethodField()
    m3u8_url = serializers.SerializerMethodField()
    segments_url = serializers.SerializerMethodField()
    total_count = serializers.SerializerMethodField()
    solved_count = serializers.SerializerMethodField()

    class Meta:
        model = CourseChapter
        fields = [
            'id', 'course', 'title', 'description', 'order',
            'video', 'video_url',
            'video_status', 'duration', 'resolution', 'bitrate',
            'm3u8_url', 'segments_url',
            'created_at', 'updated_at',
            'problems', 'problem_ids',
            'total_count', 'solved_count',
            'error_message',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'video_status', 'duration', 'resolution', 'bitrate',
            'm3u8_url', 'segments_url', 'error_message'
        ]

    def get_video_url(self, obj):
        if not obj.video:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.video.url)
        return obj.video.url

    def get_m3u8_url(self, obj):
        """获取 m3u8 播放列表 URL"""
        if obj.video_status != VideoProcessingStatus.COMPLETED or not obj.video_segments_dir:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/media/{obj.video_segments_dir}/index.m3u8')
        return f'/media/{obj.video_segments_dir}/index.m3u8'

    def get_segments_url(self, obj):
        """获取视频片段目录 URL"""
        if obj.video_status != VideoProcessingStatus.COMPLETED or not obj.video_segments_dir:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/media/{obj.video_segments_dir}/')
        return f'/media/{obj.video_segments_dir}/'
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        problem_ids = obj.chapter_problems.values_list('problem_id', flat=True)
        return request.user.problem_solve.filter(problem_id__in=problem_ids).count()

    def create(self, validated_data):
        """
        Drop write-only problem_ids so ModelSerializer won't pass it into CourseChapter.objects.create().
        """
        validated_data.pop('problem_ids', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Same as create: strip problem_ids before ModelSerializer.update().
        """
        validated_data.pop('problem_ids', None)
        return super().update(instance, validated_data)


class CourseSerializer(serializers.ModelSerializer):
    teacher = UserSimpleSerializer(read_only=True)
    joined = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'teacher',
            'is_hidden', 'created_at', 'updated_at',
            'joined', 'member_count',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'teacher']

    def get_joined(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.enrollments.filter(user=request.user).exists() or obj.teacher_id == request.user.id

    def get_member_count(self, obj):
        return obj.enrollments.count()


class CourseDetailSerializer(CourseSerializer):
    chapters = CourseChapterSerializer(many=True, read_only=True)

    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ['chapters']
