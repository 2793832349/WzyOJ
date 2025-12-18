from rest_framework import serializers
from django.utils import timezone
from django.db.models import Count, Q

from .models import Class, ClassStudent, ClassProblem, Assignment, AssignmentProblem
from oj_user.models import User
from oj_problem.models import Problem


class UserSimpleSerializer(serializers.ModelSerializer):
    """用户简单序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'real_name', 'student_id']


class ClassStudentSerializer(serializers.ModelSerializer):
    """班级成员序列化器"""
    user = UserSimpleSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ClassStudent
        fields = ['id', 'user', 'user_id', 'role', 'joined_at']
        read_only_fields = ['id', 'joined_at']


class ClassSerializer(serializers.ModelSerializer):
    """班级序列化器"""
    teacher = UserSimpleSerializer(read_only=True)
    student_count = serializers.SerializerMethodField()
    problem_count = serializers.SerializerMethodField()
    assignment_count = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()
    
    class Meta:
        model = Class
        fields = [
            'id', 'title', 'description', 'teacher', 
            'is_hidden', 'created_at', 'updated_at',
            'student_count', 'problem_count', 'assignment_count',
            'is_member', 'user_role'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'teacher']
    
    def get_student_count(self, obj):
        return obj.members.filter(role='student').count()
    
    def get_problem_count(self, obj):
        return obj.problems.count()
    
    def get_assignment_count(self, obj):
        return obj.assignments.count()
    
    def get_is_member(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.members.filter(user=request.user).exists()
        return False
    
    def get_user_role(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            membership = obj.members.filter(user=request.user).first()
            if membership:
                return membership.role
            if obj.teacher_id == request.user.id:
                return 'teacher'
        return None


class ClassProblemSerializer(serializers.ModelSerializer):
    """班级题目序列化器"""
    reference_problem_title = serializers.CharField(source='reference_problem.title', read_only=True)
    display_title = serializers.SerializerMethodField()
    submission_count = serializers.SerializerMethodField()
    accepted_count = serializers.SerializerMethodField()
    difficulty = serializers.SerializerMethodField()
    time_limit = serializers.SerializerMethodField()
    memory_limit = serializers.SerializerMethodField()
    
    class Meta:
        model = ClassProblem
        fields = [
            'id', 'class_obj', 'reference_problem', 'reference_problem_title',
            'title', 'description', 'input_format', 'output_format', 'hint',
            'time_limit', 'memory_limit', 'difficulty',
            'test_case_config', 'samples', 'is_reference',
            'created_at', 'order', 'display_title',
            'submission_count', 'accepted_count'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_display_title(self, obj):
        return obj.get_title()
    
    def get_difficulty(self, obj):
        """获取难度，引用题目从reference_problem获取"""
        if obj.is_reference and obj.reference_problem:
            return obj.reference_problem.difficulty
        return obj.difficulty
    
    def get_time_limit(self, obj):
        """获取时间限制，引用题目从reference_problem获取"""
        if obj.is_reference and obj.reference_problem:
            return obj.reference_problem.time_limit
        return obj.time_limit
    
    def get_memory_limit(self, obj):
        """获取内存限制，引用题目从reference_problem获取"""
        if obj.is_reference and obj.reference_problem:
            return obj.reference_problem.memory_limit
        return obj.memory_limit
    
    def get_submission_count(self, obj):
        # TODO: 实现提交统计
        return 0
    
    def get_accepted_count(self, obj):
        # TODO: 实现通过统计
        return 0
    
    def validate(self, data):
        """验证数据"""
        is_reference = data.get('is_reference', False)
        
        if is_reference and not data.get('reference_problem'):
            raise serializers.ValidationError('引用题目时必须指定 reference_problem')
        
        if not is_reference and not data.get('title'):
            raise serializers.ValidationError('班级专属题目必须填写标题')
        
        return data


class AssignmentProblemSerializer(serializers.ModelSerializer):
    """作业题目序列化器"""
    problem = ClassProblemSerializer(read_only=True)
    problem_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = AssignmentProblem
        fields = ['id', 'problem', 'problem_id', 'order']


class AssignmentSerializer(serializers.ModelSerializer):
    """作业序列化器"""
    problems = AssignmentProblemSerializer(source='assignmentproblem_set', many=True, read_only=True)
    problem_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    is_expired = serializers.BooleanField(read_only=True)
    completion_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'class_obj', 'title', 'description', 'deadline',
            'is_hidden', 'created_at', 'updated_at',
            'problems', 'problem_ids', 'is_expired', 'completion_rate'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_completion_rate(self, obj):
        """获取完成率"""
        # TODO: 实现完成率统计
        return 0
    
    def create(self, validated_data):
        # 移除 problem_ids，因为它在 ViewSet 的 perform_create 中处理
        validated_data.pop('problem_ids', None)
        assignment = Assignment.objects.create(**validated_data)
        return assignment
    
    def update(self, instance, validated_data):
        # 移除 problem_ids，因为它在 ViewSet 的 perform_update 中处理
        validated_data.pop('problem_ids', None)
        
        # 更新基本信息
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


class AssignmentStatSerializer(serializers.Serializer):
    """作业统计序列化器"""
    student = UserSimpleSerializer()
    total_problems = serializers.IntegerField()
    solved_problems = serializers.IntegerField()
    submission_count = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    last_submit_time = serializers.DateTimeField()
