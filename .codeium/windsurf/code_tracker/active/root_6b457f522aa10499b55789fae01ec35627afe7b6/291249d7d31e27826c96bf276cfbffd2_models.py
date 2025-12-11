�from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from oj_user.models import User
from oj_problem.models import Problem


class Contest(models.Model):
    RULE_TYPE_CHOICES = [
        ('IOI', _('IOI (实时反馈+部分分)')),
        ('OI', _('OI (赛后反馈+部分分)')),
        ('ACM', _('ACM (实时反馈+罚时)')),
    ]
    
    title = models.CharField(_('title'), max_length=50)
    description = models.TextField(_('description'), null=True, blank=True)
    problem_list_mode = models.BooleanField(_('problem list mode'),
                                            default=False)
    rule_type = models.CharField(
        _('rule type'),
        max_length=10,
        choices=RULE_TYPE_CHOICES,
        default='IOI'
    )
    start_time = models.DateTimeField(_('start time'), null=True, blank=True)
    end_time = models.DateTimeField(_('end time'), null=True, blank=True)
    freeze_time = models.DateTimeField(_('freeze time'), null=True, blank=True, 
                                       help_text=_('封榜时间，ACM赛制使用'))
    is_hidden = models.BooleanField(_('hide'), default=False)
    allow_sign_up = models.BooleanField(_('allow sign up'), default=True)
    public_ranking = models.BooleanField(_('public ranking'), default=False,
                                         help_text=_('是否公开排行榜（未登录用户可见）'))

    problems = models.ManyToManyField(Problem, through='ContestProblem')
    users = models.ManyToManyField(User, through='ContestUser')

    @property
    def hide_discussions(self):
        return any([
            self.is_hidden,
            self.start_time < timezone.now()
            and self.end_time > timezone.now(),
        ])

    class Meta:
        verbose_name = _('contest')
        verbose_name_plural = _('contests')

    def __str__(self):
        return self.title


class ContestProblem(models.Model):
    contest = models.ForeignKey(
        Contest,
        verbose_name=_('contest'),
        on_delete=models.CASCADE,
    )
    problem = models.ForeignKey(
        Problem,
        verbose_name=_('problem'),
        related_name='contests',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _('contest problem')
        verbose_name_plural = _('contest problems')

    def __str__(self):
        return f'{self.contest.title} - {self.problem.title}'


class ContestUser(models.Model):
    contest = models.ForeignKey(
        Contest,
        verbose_name=_('contest'),
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name=_('user'),
        related_name='contests',
        on_delete=models.CASCADE,
    )
    is_admin = models.BooleanField(_('is admin'), default=False)

    class Meta:
        verbose_name = _('contest user')
        verbose_name_plural = _('contest users')

    def __str__(self):
        return f'{self.contest.title} - {self.user.username}'
� *cascade08��*cascade08��	 *cascade08�	�*cascade08�� *cascade08"(6b457f522aa10499b55789fae01ec35627afe7b62)file:///root/backend/oj_contest/models.py:file:///root