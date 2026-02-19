from django.db import models
from django.utils.translation import gettext_lazy as _
from oj_user.models import User


class Announcement(models.Model):
    title = models.CharField(_('title'), max_length=120)
    content = models.TextField(_('content'))
    is_published = models.BooleanField(_('is published'), default=True)
    is_pinned = models.BooleanField(_('is pinned'), default=False)
    start_time = models.DateTimeField(_('start time'), null=True, blank=True)
    end_time = models.DateTimeField(_('end time'), null=True, blank=True)
    order = models.IntegerField(_('order'), default=0)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_announcements',
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_announcements',
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        ordering = ['-is_pinned', 'order', '-id']
        verbose_name = _('announcement')
        verbose_name_plural = _('announcements')

    def __str__(self):
        return self.title
