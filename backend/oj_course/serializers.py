from rest_framework import serializers

from django.db.utils import OperationalError, ProgrammingError

from oj_problem.serializers import ProblemSerializer
from oj_user.models import User

from .models import Course, CourseChapter, CourseEnrollment, ChapterProblem, CourseRedeemCode, UserCoursePurchase


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


class CourseChapterSerializer(serializers.ModelSerializer):
    problems = CourseChapterProblemSerializer(source='chapter_problems', many=True, read_only=True)
    problem_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    video_url = serializers.SerializerMethodField()
    total_count = serializers.SerializerMethodField()
    solved_count = serializers.SerializerMethodField()

    class Meta:
        model = CourseChapter
        fields = [
            'id', 'course', 'title', 'description', 'order',
            'video', 'video_url',
            'created_at', 'updated_at',
            'problems', 'problem_ids',
            'total_count', 'solved_count',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_video_url(self, obj):
        if not obj.video:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.video.url)
        return obj.video.url

    def get_total_count(self, obj):
        return obj.chapter_problems.count()

    def get_solved_count(self, obj):
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
    purchased = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'teacher',
            'is_hidden', 'is_free', 'created_at', 'updated_at',
            'joined', 'member_count', 'purchased',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'teacher']

    def get_joined(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        try:
            return obj.enrollments.filter(user=request.user).exists() or obj.teacher_id == request.user.id
        except (ProgrammingError, OperationalError):
            return obj.teacher_id == request.user.id

    def get_member_count(self, obj):
        try:
            return obj.enrollments.count()
        except (ProgrammingError, OperationalError):
            return 0

    def get_purchased(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        if obj.is_free:
            return True
        try:
            return obj.purchases.filter(user=request.user).exists()
        except (ProgrammingError, OperationalError):
            return False


class CourseDetailSerializer(CourseSerializer):
    chapters = CourseChapterSerializer(many=True, read_only=True)

    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ['chapters']


class CourseRedeemCodeSerializer(serializers.ModelSerializer):
    """课程兑换码序列化器"""
    is_valid = serializers.BooleanField(read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, default='')

    class Meta:
        model = CourseRedeemCode
        fields = [
            'id', 'course', 'code', 'max_uses', 'used_count',
            'expires_at', 'is_active', 'is_valid',
            'created_by', 'created_by_name', 'created_at', 'note'
        ]
        read_only_fields = ['id', 'code', 'used_count', 'created_by', 'created_at']


class UserCoursePurchaseSerializer(serializers.ModelSerializer):
    """用户课程购买记录序列化器"""
    course = CourseSerializer(read_only=True)

    class Meta:
        model = UserCoursePurchase
        fields = ['id', 'course', 'purchased_at']
