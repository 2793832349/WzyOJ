from django.db import models
from django.utils.translation import gettext_lazy as _

from oj_user.models import User


def get_default_options():
    return [
        {'key': 'A', 'text': ''},
        {'key': 'B', 'text': ''},
    ]


def get_default_answers():
    return []


def get_default_paper_answers():
    return {}


class ObjectiveQuestionTypeChoices(models.TextChoices):
    SINGLE = 'single', _('Single Choice')
    MULTIPLE = 'multiple', _('Multiple Choice')
    JUDGE = 'judge', _('True/False')


class ObjectiveQuestion(models.Model):
    title = models.CharField(_('title'), max_length=120)
    content = models.TextField(_('content'), blank=True, default='')
    question_type = models.CharField(
        _('question type'),
        max_length=20,
        choices=ObjectiveQuestionTypeChoices.choices,
        default=ObjectiveQuestionTypeChoices.SINGLE,
    )
    options = models.JSONField(_('options'), default=get_default_options)
    correct_answers = models.JSONField(_('correct answers'), default=get_default_answers)
    explanation = models.TextField(_('explanation'), blank=True, default='')
    difficulty = models.IntegerField(_('difficulty'), default=0)
    _is_hidden = models.BooleanField(_('hide'), default=False)
    create_time = models.DateTimeField(_('create time'), auto_now_add=True)
    update_time = models.DateTimeField(_('update time'), auto_now=True)
    submission_count = models.IntegerField(_('submission count'), default=0)
    accepted_count = models.IntegerField(_('accepted user count'), default=0)
    created_by = models.ForeignKey(
        User,
        verbose_name=_('created by'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_objective_questions',
    )
    updated_by = models.ForeignKey(
        User,
        verbose_name=_('updated by'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_objective_questions',
    )

    @property
    def is_hidden(self):
        return self._is_hidden

    class Meta:
        verbose_name = _('objective question')
        verbose_name_plural = _('objective questions')
        ordering = ['id']

    def __str__(self):
        return self.title


class ObjectiveSubmission(models.Model):
    question = models.ForeignKey(
        ObjectiveQuestion,
        verbose_name=_('question'),
        on_delete=models.CASCADE,
        related_name='submissions',
    )
    user = models.ForeignKey(
        User,
        verbose_name=_('user'),
        on_delete=models.CASCADE,
        related_name='objective_submissions',
    )
    selected_answers = models.JSONField(_('selected answers'), default=get_default_answers)
    is_correct = models.BooleanField(_('is correct'), default=False)
    create_time = models.DateTimeField(_('create time'), auto_now_add=True)

    class Meta:
        verbose_name = _('objective submission')
        verbose_name_plural = _('objective submissions')
        ordering = ['-create_time']


class ObjectivePaper(models.Model):
    title = models.CharField(_('title'), max_length=120)
    description = models.TextField(_('description'), blank=True, default='')
    pass_score = models.IntegerField(_('pass score'), default=60)
    _is_hidden = models.BooleanField(_('hide'), default=False)
    create_time = models.DateTimeField(_('create time'), auto_now_add=True)
    update_time = models.DateTimeField(_('update time'), auto_now=True)
    created_by = models.ForeignKey(
        User,
        verbose_name=_('created by'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_objective_papers',
    )
    updated_by = models.ForeignKey(
        User,
        verbose_name=_('updated by'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_objective_papers',
    )

    @property
    def is_hidden(self):
        return self._is_hidden

    class Meta:
        verbose_name = _('objective paper')
        verbose_name_plural = _('objective papers')
        ordering = ['-id']

    def __str__(self):
        return self.title


class ObjectivePaperItem(models.Model):
    paper = models.ForeignKey(
        ObjectivePaper,
        verbose_name=_('paper'),
        on_delete=models.CASCADE,
        related_name='items',
    )
    question = models.ForeignKey(
        ObjectiveQuestion,
        verbose_name=_('question'),
        on_delete=models.CASCADE,
        related_name='paper_items',
    )
    order = models.IntegerField(_('order'), default=1)
    score = models.IntegerField(_('score'), default=2)

    class Meta:
        verbose_name = _('objective paper item')
        verbose_name_plural = _('objective paper items')
        ordering = ['order', 'id']


class ObjectivePaperSubmission(models.Model):
    paper = models.ForeignKey(
        ObjectivePaper,
        verbose_name=_('paper'),
        on_delete=models.CASCADE,
        related_name='submissions',
    )
    user = models.ForeignKey(
        User,
        verbose_name=_('user'),
        on_delete=models.CASCADE,
        related_name='objective_paper_submissions',
    )
    answers = models.JSONField(_('answers'), default=get_default_paper_answers)
    total_score = models.IntegerField(_('total score'), default=0)
    max_score = models.IntegerField(_('max score'), default=0)
    is_pass = models.BooleanField(_('is pass'), default=False)
    create_time = models.DateTimeField(_('create time'), auto_now_add=True)

    class Meta:
        verbose_name = _('objective paper submission')
        verbose_name_plural = _('objective paper submissions')
        ordering = ['-create_time']
