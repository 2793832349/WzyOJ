from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from oj_user.models import User
from oj_problem.models import Problem


class Class(models.Model):
    """班级模型"""
    title = models.CharField(_('title'), max_length=100)
    description = models.TextField(_('description'), null=True, blank=True)
    teacher = models.ForeignKey(
        User,
        verbose_name=_('teacher'),
        related_name='teaching_classes',
        on_delete=models.CASCADE,
    )
    is_hidden = models.BooleanField(_('hide'), default=False)
    is_disbanded = models.BooleanField(_('disbanded'), default=False, 
                                       help_text=_('解散后的班级不可见'))
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    students = models.ManyToManyField(User, through='ClassStudent', related_name='joined_classes')

    class Meta:
        verbose_name = _('class')
        verbose_name_plural = _('classes')
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ClassStudent(models.Model):
    """班级成员模型"""
    ROLE_CHOICES = [
        ('teacher', _('Teacher')),
        ('student', _('Student')),
    ]

    class_obj = models.ForeignKey(
        Class,
        verbose_name=_('class'),
        on_delete=models.CASCADE,
        related_name='members',
    )
    user = models.ForeignKey(
        User,
        verbose_name=_('user'),
        on_delete=models.CASCADE,
        related_name='class_memberships',
    )
    role = models.CharField(
        _('role'),
        max_length=10,
        choices=ROLE_CHOICES,
        default='student',
    )
    joined_at = models.DateTimeField(_('joined at'), default=timezone.now)

    class Meta:
        verbose_name = _('class student')
        verbose_name_plural = _('class students')
        unique_together = ['class_obj', 'user']

    def __str__(self):
        return f'{self.class_obj.title} - {self.user.username} ({self.role})'


class ClassProblem(models.Model):
    """班级题目模型 - 可以引用主题库题目或创建班级专属题目"""
    class_obj = models.ForeignKey(
        Class,
        verbose_name=_('class'),
        on_delete=models.CASCADE,
        related_name='problems',
    )
    # 如果是引用主题库题目，这个字段不为空
    reference_problem = models.ForeignKey(
        Problem,
        verbose_name=_('reference problem'),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='class_references',
    )
    # 如果是班级专属题目，以下字段会被填充
    title = models.CharField(_('title'), max_length=100, blank=True)
    description = models.TextField(_('description'), blank=True)
    input_format = models.TextField(_('input format'), blank=True)
    output_format = models.TextField(_('output format'), blank=True)
    hint = models.TextField(_('hint'), blank=True)
    time_limit = models.IntegerField(_('time limit'), default=1000)  # ms
    memory_limit = models.IntegerField(_('memory limit'), default=128)  # MB
    difficulty = models.CharField(_('difficulty'), max_length=20, blank=True)
    
    # 题目数据（测试点等）
    test_case_config = models.JSONField(_('test case config'), default=list)
    samples = models.JSONField(_('samples'), default=list)
    
    is_reference = models.BooleanField(_('is reference'), default=False)
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    order = models.IntegerField(_('order'), default=0)

    class Meta:
        verbose_name = _('class problem')
        verbose_name_plural = _('class problems')
        ordering = ['order', 'created_at']

    def __str__(self):
        if self.is_reference:
            return f'{self.class_obj.title} - {self.reference_problem.title} (引用)'
        return f'{self.class_obj.title} - {self.title}'

    def get_title(self):
        """获取题目标题"""
        return self.reference_problem.title if self.is_reference else self.title

    def get_problem_data(self):
        """获取题目数据（用于提交判题）"""
        if self.is_reference:
            return {
                'title': self.reference_problem.title,
                'description': self.reference_problem.description,
                'time_limit': self.reference_problem.time_limit,
                'memory_limit': self.reference_problem.memory_limit,
                'test_case_config': self.reference_problem.test_case_config,
            }
        return {
            'title': self.title,
            'description': self.description,
            'time_limit': self.time_limit,
            'memory_limit': self.memory_limit,
            'test_case_config': self.test_case_config,
        }


class Assignment(models.Model):
    """作业模型"""
    class_obj = models.ForeignKey(
        Class,
        verbose_name=_('class'),
        on_delete=models.CASCADE,
        related_name='assignments',
    )
    title = models.CharField(_('title'), max_length=100)
    description = models.TextField(_('description'), null=True, blank=True)
    deadline = models.DateTimeField(_('deadline'), null=True, blank=True)
    is_hidden = models.BooleanField(_('hide'), default=False)
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    problems = models.ManyToManyField(ClassProblem, through='AssignmentProblem', related_name='assignments')

    class Meta:
        verbose_name = _('assignment')
        verbose_name_plural = _('assignments')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.class_obj.title} - {self.title}'

    @property
    def is_expired(self):
        """是否已过期"""
        if self.deadline:
            return timezone.now() > self.deadline
        return False


class AssignmentProblem(models.Model):
    """作业题目关联模型"""
    assignment = models.ForeignKey(
        Assignment,
        verbose_name=_('assignment'),
        on_delete=models.CASCADE,
    )
    problem = models.ForeignKey(
        ClassProblem,
        verbose_name=_('problem'),
        on_delete=models.CASCADE,
    )
    order = models.IntegerField(_('order'), default=0)

    class Meta:
        verbose_name = _('assignment problem')
        verbose_name_plural = _('assignment problems')
        ordering = ['order']
        unique_together = ['assignment', 'problem']

    def __str__(self):
        return f'{self.assignment.title} - {self.problem.get_title()}'
