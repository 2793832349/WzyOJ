import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from oj_problem.models import Problem
from oj_submission.models import Submission, StatusChoices
from oj_user.models import User


class BattleRoomStatus(models.TextChoices):
    WAITING = 'waiting', _('Waiting')
    RUNNING = 'running', _('Running')
    FINISHED = 'finished', _('Finished')


class BattleRoomType(models.TextChoices):
    FRIEND = 'friend', _('Friend')
    MATCH = 'match', _('Match')


class BattleFinishReason(models.TextChoices):
    FIRST_AC = 'first_ac', _('First AC')
    TIMEOUT_DRAW = 'timeout_draw', _('Timeout Draw')
    TIMEOUT_BY_WA = 'timeout_by_wa', _('Timeout By Wrong Attempts')
    BOTH_GAVE_UP = 'both_gave_up', _('Both Gave Up')
    ONE_GAVE_UP = 'one_gave_up', _('One Gave Up')


class BattleRoom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_type = models.CharField(max_length=20, choices=BattleRoomType.choices, default=BattleRoomType.FRIEND)
    status = models.CharField(max_length=20, choices=BattleRoomStatus.choices, default=BattleRoomStatus.WAITING)

    created_by = models.ForeignKey(User, related_name='created_battle_rooms', on_delete=models.CASCADE)

    problem = models.ForeignKey(Problem, null=True, blank=True, related_name='battle_rooms', on_delete=models.SET_NULL)

    difficulty_min = models.IntegerField(null=True, blank=True)
    difficulty_max = models.IntegerField(null=True, blank=True)

    duration_seconds = models.IntegerField(default=1800)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    winner = models.ForeignKey(User, null=True, blank=True, related_name='won_battle_rooms', on_delete=models.SET_NULL)
    finish_reason = models.CharField(max_length=30, choices=BattleFinishReason.choices, null=True, blank=True)

    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('battle room')
        verbose_name_plural = _('battle rooms')


class BattleParticipantSide(models.TextChoices):
    A = 'A', 'A'
    B = 'B', 'B'


class BattleParticipant(models.Model):
    room = models.ForeignKey(BattleRoom, related_name='participants', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='battle_participations', on_delete=models.CASCADE)
    side = models.CharField(max_length=1, choices=BattleParticipantSide.choices)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('battle participant')
        verbose_name_plural = _('battle participants')
        unique_together = (('room', 'user'), ('room', 'side'))


class BattleSubmissionLink(models.Model):
    room = models.ForeignKey(BattleRoom, related_name='battle_submissions', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='battle_submissions', on_delete=models.CASCADE)
    submission = models.OneToOneField(Submission, related_name='battle_link', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('battle submission link')
        verbose_name_plural = _('battle submission links')

    @property
    def is_final(self):
        return self.submission.status != StatusChoices.JUDGING

    def to_event_payload(self):
        return {
            'room_id': str(self.room_id),
            'user_id': self.user_id,
            'submission_id': self.submission_id,
            'status': self.submission.status,
            'score': self.submission.score,
            'execute_time': self.submission.execute_time,
            'execute_memory': self.submission.execute_memory,
            'create_time': int(self.submission.create_time.timestamp()) if self.submission.create_time else None,
        }


class BattleSeason(models.Model):
    """对战赛季模型"""
    name = models.CharField(max_length=100, verbose_name=_('season name'))
    start_time = models.DateTimeField(verbose_name=_('start time'))
    end_time = models.DateTimeField(verbose_name=_('end time'))
    is_active = models.BooleanField(default=True, verbose_name=_('is active'))
    inherit_ratio = models.FloatField(default=0.5, verbose_name=_('inherit ratio'), help_text=_('继承上赛季分数的比例'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('battle season')
        verbose_name_plural = _('battle seasons')
        ordering = ['-start_time']

    def __str__(self):
        return self.name

    @classmethod
    def get_current_season(cls):
        """获取当前赛季"""
        now = timezone.now()
        return cls.objects.filter(
            start_time__lte=now,
            end_time__gte=now,
            is_active=True
        ).first()


class BattleRating(models.Model):
    """用户对战等级分模型"""
    user = models.ForeignKey(User, related_name='battle_ratings', on_delete=models.CASCADE)
    season = models.ForeignKey(BattleSeason, related_name='ratings', on_delete=models.CASCADE, null=True, blank=True)
    
    # 等级分（赛季分）
    rating = models.IntegerField(default=500, verbose_name=_('rating'))
    # 对战等级（不重置）
    battle_level = models.IntegerField(default=1, verbose_name=_('battle level'))
    # 经验值
    experience = models.IntegerField(default=0, verbose_name=_('experience'))
    
    # 统计数据
    total_battles = models.IntegerField(default=0, verbose_name=_('total battles'))
    wins = models.IntegerField(default=0, verbose_name=_('wins'))
    losses = models.IntegerField(default=0, verbose_name=_('losses'))
    
    # 最高分数
    peak_rating = models.IntegerField(default=500, verbose_name=_('peak rating'))
    
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('battle rating')
        verbose_name_plural = _('battle ratings')
        unique_together = [('user', 'season')]
        ordering = ['-rating', '-peak_rating']

    def __str__(self):
        return f'{self.user.username} - {self.rating}'

    @property
    def win_rate(self):
        """胜率"""
        if self.total_battles == 0:
            return 0
        return round(self.wins / self.total_battles * 100, 1)

    def update_rating(self, rating_change, exp_change, is_win):
        """更新等级分和经验"""
        self.rating += rating_change
        self.experience += exp_change
        self.total_battles += 1
        
        if is_win:
            self.wins += 1
        else:
            self.losses += 1
        
        # 更新最高分
        if self.rating > self.peak_rating:
            self.peak_rating = self.rating
        
        # 更新对战等级（每100经验升1级）
        self.battle_level = 1 + (self.experience // 100)
        
        self.save()


class BattleResult(models.Model):
    """对战结果记录"""
    room = models.OneToOneField(BattleRoom, related_name='result', on_delete=models.CASCADE)
    season = models.ForeignKey(BattleSeason, related_name='results', on_delete=models.SET_NULL, null=True, blank=True)
    
    # 参与者
    user_a = models.ForeignKey(User, related_name='battle_results_as_a', on_delete=models.CASCADE)
    user_b = models.ForeignKey(User, related_name='battle_results_as_b', on_delete=models.CASCADE)
    
    # 结果
    winner = models.ForeignKey(User, related_name='battle_wins', on_delete=models.SET_NULL, null=True, blank=True)
    
    # A方数据
    user_a_rating_before = models.IntegerField(default=500)
    user_a_rating_change = models.IntegerField(default=0)
    user_a_exp_change = models.IntegerField(default=0)
    user_a_ac_time = models.DateTimeField(null=True, blank=True, verbose_name=_('A AC time'))
    user_a_gave_up = models.BooleanField(default=False)
    
    # B方数据
    user_b_rating_before = models.IntegerField(default=500)
    user_b_rating_change = models.IntegerField(default=0)
    user_b_exp_change = models.IntegerField(default=0)
    user_b_ac_time = models.DateTimeField(null=True, blank=True, verbose_name=_('B AC time'))
    user_b_gave_up = models.BooleanField(default=False)
    
    # 是否在奖励时间内完成
    user_a_bonus_time = models.BooleanField(default=False)
    user_b_bonus_time = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('battle result')
        verbose_name_plural = _('battle results')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user_a.username} vs {self.user_b.username}'
