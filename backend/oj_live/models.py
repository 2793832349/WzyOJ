from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from oj_course.models import Course
from oj_user.models import User


class LiveSessionStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    ENDED = 'ended', 'Ended'


class LiveSession(models.Model):
    # 保留旧的 course 字段以向后兼容，但设为可空
    course = models.ForeignKey(Course, related_name='live_sessions', on_delete=models.CASCADE, null=True, blank=True)
    
    # 使用 GenericForeignKey 支持多种关联对象（课程/班级）
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')
    
    title = models.CharField(max_length=100, blank=True, default='')
    status = models.CharField(max_length=20, choices=LiveSessionStatus.choices, default=LiveSessionStatus.ACTIVE)

    started_by = models.ForeignKey(User, related_name='started_live_sessions', on_delete=models.CASCADE)

    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_time']
    
    def get_related_object(self):
        """获取关联的对象（课程或班级）"""
        if self.related_object:
            return self.related_object
        return self.course  # 向后兼容
    
    def get_teacher_id(self):
        """获取教师 ID"""
        obj = self.get_related_object()
        if obj:
            return obj.teacher_id if hasattr(obj, 'teacher_id') else obj.teacher.id
        return None
    
    def is_member(self, user):
        """检查用户是否是成员"""
        obj = self.get_related_object()
        if not obj:
            return False
        
        # 检查是否是教师
        teacher_id = self.get_teacher_id()
        if teacher_id == user.id:
            return True
        
        # 检查是否是课程成员
        if isinstance(obj, Course):
            from oj_course.models import CourseEnrollment
            return CourseEnrollment.objects.filter(course=obj, user=user).exists()
        
        # 检查是否是班级成员
        from oj_class.models import Class, ClassStudent
        if obj.__class__.__name__ == 'Class':
            return ClassStudent.objects.filter(class_obj=obj, user=user).exists()
        
        return False


class LiveParticipantRole(models.TextChoices):
    TEACHER = 'teacher', 'Teacher'
    STUDENT = 'student', 'Student'


class LiveParticipant(models.Model):
    session = models.ForeignKey(LiveSession, related_name='participants', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='live_participants', on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=LiveParticipantRole.choices, default=LiveParticipantRole.STUDENT)

    joined_at = models.DateTimeField(default=timezone.now)
    left_at = models.DateTimeField(null=True, blank=True)

    muted = models.BooleanField(default=False)
    hand_raised = models.BooleanField(default=False)

    class Meta:
        unique_together = ['session', 'user']
        ordering = ['joined_at']
