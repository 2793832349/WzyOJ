from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from oj_problem.models import Problem
from oj_user.models import User


class Course(models.Model):
    title = models.CharField(_('title'), max_length=100)
    description = models.TextField(_('description'), blank=True, default='')
    teacher = models.ForeignKey(
        User,
        verbose_name=_('teacher'),
        related_name='teaching_courses',
        on_delete=models.CASCADE,
    )
    is_hidden = models.BooleanField(_('hide'), default=False)
    is_free = models.BooleanField(_('is free'), default=True)
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('course')
        verbose_name_plural = _('courses')
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class CourseEnrollment(models.Model):
    course = models.ForeignKey(
        Course,
        verbose_name=_('course'),
        related_name='enrollments',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name=_('user'),
        related_name='course_enrollments',
        on_delete=models.CASCADE,
    )
    joined_at = models.DateTimeField(_('joined at'), default=timezone.now)

    class Meta:
        verbose_name = _('course enrollment')
        verbose_name_plural = _('course enrollments')
        unique_together = ['course', 'user']

    def __str__(self):
        return f'{self.course.title} - {self.user.username}'


class CourseChapter(models.Model):
    course = models.ForeignKey(
        Course,
        verbose_name=_('course'),
        related_name='chapters',
        on_delete=models.CASCADE,
    )
    title = models.CharField(_('title'), max_length=100)
    description = models.TextField(_('description'), blank=True, default='')
    order = models.IntegerField(_('order'), default=0)
    video = models.FileField(upload_to='course_videos/%Y/%m/', null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('course chapter')
        verbose_name_plural = _('course chapters')
        ordering = ['order', 'created_at']

    def __str__(self):
        return f'{self.course.title} - {self.title}'


class ChapterProblem(models.Model):
    chapter = models.ForeignKey(
        CourseChapter,
        verbose_name=_('chapter'),
        related_name='chapter_problems',
        on_delete=models.CASCADE,
    )
    problem = models.ForeignKey(
        Problem,
        verbose_name=_('problem'),
        related_name='course_chapter_refs',
        on_delete=models.CASCADE,
    )
    order = models.IntegerField(_('order'), default=0)

    class Meta:
        verbose_name = _('chapter problem')
        verbose_name_plural = _('chapter problems')
        ordering = ['order']
        unique_together = ['chapter', 'problem']

    def __str__(self):
        return f'{self.chapter.title} - {self.problem.title}'


class CourseRedeemCode(models.Model):
    """课程兑换码"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='redeem_codes')
    code = models.CharField(_('code'), max_length=32, unique=True)
    
    # 使用限制（固定为1次）
    max_uses = models.IntegerField(_('max uses'), default=1)
    used_count = models.IntegerField(_('used count'), default=0)
    
    # 有效期
    expires_at = models.DateTimeField(_('expires at'), null=True, blank=True)
    
    # 状态
    is_active = models.BooleanField(_('is active'), default=True)
    
    # 创建信息
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_course_redeem_codes')
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    
    # 备注
    note = models.CharField(_('note'), max_length=200, blank=True, default='')

    class Meta:
        verbose_name = _('course redeem code')
        verbose_name_plural = _('course redeem codes')

    def __str__(self):
        return f"{self.course.title} - {self.code}"
    
    @property
    def is_valid(self):
        if not self.is_active:
            return False
        if self.max_uses > 0 and self.used_count >= self.max_uses:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True


class UserCoursePurchase(models.Model):
    """用户课程购买/兑换记录"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_purchases')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='purchases')
    
    # 兑换码（可选）
    redeem_code = models.ForeignKey(CourseRedeemCode, on_delete=models.SET_NULL, null=True, blank=True)
    
    # 购买时间
    purchased_at = models.DateTimeField(_('purchased at'), default=timezone.now)

    class Meta:
        unique_together = ['user', 'course']
        verbose_name = _('user course purchase')
        verbose_name_plural = _('user course purchases')

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"
