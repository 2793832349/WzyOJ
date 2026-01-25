from celery import shared_task
from datetime import timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from oj_submission.models import StatusChoices, Submission

from .models import BattleFinishReason, BattleRoom, BattleRoomStatus, BattleResult, BattleSeason
from .rating_calculator import RatingCalculator


WRONG_STATUSES = [
    StatusChoices.WRONG_ANSWER,
    StatusChoices.COMPILE_ERROR,
    StatusChoices.RUNTIME_ERROR,
    StatusChoices.TIME_LIMIT_EXCEEDED,
    StatusChoices.MEMORY_LIMIT_EXCEEDED,
]


def _send_room_event(room_id: str, payload: dict):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'battle_room_{room_id}',
        {
            'type': 'battle_event',
            'payload': payload,
        },
    )


def process_battle_result(room: BattleRoom):
    """
    处理对战结束后的结果计算和保存
    计算双方的等级分和经验变化，并更新 BattleRating
    """
    # 检查是否已经处理过
    if hasattr(room, 'result') and room.result:
        return
    
    participants = list(room.participants.select_related('user').all())
    if len(participants) != 2:
        return
    
    user_a = participants[0].user
    user_b = participants[1].user
    
    # 获取当前赛季
    current_season = BattleSeason.objects.filter(is_active=True).first()
    
    # 获取或创建双方的等级分记录
    rating_a = RatingCalculator.get_or_create_rating(user_a, current_season)
    rating_b = RatingCalculator.get_or_create_rating(user_b, current_season)
    
    # 获取双方的 AC 时间
    from .models import BattleSubmissionLink
    
    def get_first_ac_time(user):
        ac_submission = BattleSubmissionLink.objects.filter(
            room=room,
            user=user,
            submission__status=StatusChoices.ACCEPTED
        ).select_related('submission').order_by('submission__create_time').first()
        if ac_submission:
            return ac_submission.submission.create_time
        return None
    
    a_ac_time = get_first_ac_time(user_a)
    b_ac_time = get_first_ac_time(user_b)
    
    # 准备计算数据
    user_a_data = {
        'ac_time': a_ac_time,
        'gave_up': False,  # TODO: 实现放弃功能后更新
    }
    user_b_data = {
        'ac_time': b_ac_time,
        'gave_up': False,
    }
    
    # 获取题目难度
    problem_difficulty = None
    if room.problem:
        problem_difficulty = room.problem.difficulty
    
    # 计算等级分和经验变化
    result = RatingCalculator.calculate_rating_change(user_a_data, user_b_data, room.start_time, problem_difficulty)
    
    # 确定胜者
    winner = None
    if result['user_a']['is_win']:
        winner = user_a
    elif result['user_b']['is_win']:
        winner = user_b
    
    # 创建对战结果记录
    battle_result = BattleResult.objects.create(
        room=room,
        season=current_season,
        user_a=user_a,
        user_b=user_b,
        winner=winner,
        user_a_rating_before=rating_a.rating,
        user_a_rating_change=result['user_a']['rating_change'],
        user_a_exp_change=result['user_a']['exp_change'],
        user_a_ac_time=a_ac_time,
        user_a_gave_up=user_a_data['gave_up'],
        user_a_bonus_time=result['user_a']['bonus_time'],
        user_b_rating_before=rating_b.rating,
        user_b_rating_change=result['user_b']['rating_change'],
        user_b_exp_change=result['user_b']['exp_change'],
        user_b_ac_time=b_ac_time,
        user_b_gave_up=user_b_data['gave_up'],
        user_b_bonus_time=result['user_b']['bonus_time'],
    )
    
    # 更新双方的等级分和经验
    rating_a.update_rating(
        result['user_a']['rating_change'],
        result['user_a']['exp_change'],
        result['user_a']['is_win']
    )
    rating_b.update_rating(
        result['user_b']['rating_change'],
        result['user_b']['exp_change'],
        result['user_b']['is_win']
    )
    
    return battle_result


@shared_task
def finish_room_if_timeout(room_id: str):
    room = BattleRoom.objects.filter(id=room_id).first()
    if not room or room.status != BattleRoomStatus.RUNNING or not room.start_time:
        return

    deadline = room.start_time + timedelta(seconds=room.duration_seconds)
    if timezone.now() < deadline:
        return

    participants = list(room.participants.values_list('user_id', flat=True))
    if len(participants) != 2:
        room.status = BattleRoomStatus.FINISHED
        room.finish_reason = BattleFinishReason.TIMEOUT_DRAW
        room.winner_id = None
        room.end_time = timezone.now()
        room.save(update_fields=['status', 'finish_reason', 'winner', 'end_time'])
        _send_room_event(str(room.id), {
            'type': 'room_finished',
            'room_id': str(room.id),
            'finish_reason': room.finish_reason,
            'winner_id': room.winner_id,
        })
        return

    room.status = BattleRoomStatus.FINISHED
    room.finish_reason = BattleFinishReason.TIMEOUT_DRAW
    room.end_time = timezone.now()
    
    # 如果有人已经 AC 了，那个人就是赢家
    # winner_id 可能在 first_ac 时已经设置
    room.save(update_fields=['status', 'finish_reason', 'end_time'])
    
    # 计算和保存对战结果
    process_battle_result(room)

    _send_room_event(str(room.id), {
        'type': 'room_finished',
        'room_id': str(room.id),
        'finish_reason': room.finish_reason,
        'winner_id': room.winner_id,
    })
