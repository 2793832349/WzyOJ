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
