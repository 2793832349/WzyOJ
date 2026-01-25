from celery import shared_task
from django.conf import settings
from django.utils import timezone
import shutil
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .judger import JudgeClient, ResultMapping
from .models import Submission, StatusChoices
from oj_problem.models import ProblemSolve


@shared_task
def judge(task_id, case_id, spj_id, test_case_config, subcheck_config, lang,
          code, limit):
    submission = Submission.objects.get(id=task_id)
    judger = JudgeClient()

    if spj_id:
        testlib_dst = settings.SPJ_ROOT / 'testlib.h'
        if not testlib_dst.exists():
            testlib_src = settings.BASE_DIR / 'judge_data/spj/testlib.h'
            if testlib_src.is_file():
                shutil.copyfile(testlib_src, testlib_dst)

    submission.status = StatusChoices.JUDGING
    submission.allow_download = submission.problem.test_case.allow_download
    submission.save(update_fields=['status', 'allow_download'])
    try:
        result = judger.judge(task_id, case_id, spj_id, test_case_config,
                              subcheck_config, lang, code, limit)
        submission.status = ResultMapping[result['status']]
        submission.score = result['score']
        submission.execute_time = result['statistics']['max_time']
        submission.execute_memory = result['statistics']['max_memory']
        submission.detail = result['detail']
        submission.log = result['log']
        submission.save(update_fields=[
            'status', 'score', 'execute_time', 'execute_memory', 'detail', 'log'
        ])
    except Exception as e:
        submission.status = StatusChoices.SYSTEM_ERROR
        submission.score = 0
        submission.execute_time = 0
        submission.execute_memory = 0
        submission.detail = []
        submission.log = f'Judge task failed: {type(e).__name__}: {e}'
        submission.save(update_fields=[
            'status', 'score', 'execute_time', 'execute_memory', 'detail', 'log'
        ])

    try:
        from oj_battle.models import BattleFinishReason, BattleRoomStatus, BattleSubmissionLink

        link = (
            BattleSubmissionLink.objects
            .select_related('room', 'submission')
            .filter(submission_id=submission.id)
            .first()
        )
        if link:
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f'battle_room_{link.room_id}',
                    {
                        'type': 'battle_event',
                        'payload': {
                            'type': 'submission_update',
                            **link.to_event_payload(),
                        },
                    },
                )

            # 记录第一个 AC 的用户，但不立即结束对战
            # 允许另一方继续提交以获得经验和分数（根据规则表）
            if submission.status == StatusChoices.ACCEPTED and link.room.status == BattleRoomStatus.RUNNING:
                if link.room.winner_id is None:
                    # 只记录第一个 AC 的用户作为潜在赢家，但不结束对战
                    link.room.winner_id = submission.user_id
                    link.room.save(update_fields=['winner'])
                    
                    # 通知前端有人首先 AC 了
                    if channel_layer:
                        async_to_sync(channel_layer.group_send)(
                            f'battle_room_{link.room_id}',
                            {
                                'type': 'battle_event',
                                'payload': {
                                    'type': 'first_ac',
                                    'room_id': str(link.room_id),
                                    'user_id': submission.user_id,
                                },
                            },
                        )
                else:
                    # 如果已经有人 AC 了，现在第二个人也 AC 了，对战结束
                    link.room.status = BattleRoomStatus.FINISHED
                    link.room.finish_reason = BattleFinishReason.FIRST_AC
                    link.room.end_time = timezone.now()
                    link.room.save(update_fields=['status', 'finish_reason', 'end_time'])
                    
                    # 计算和保存对战结果
                    from oj_battle.tasks import process_battle_result
                    process_battle_result(link.room)
                    
                    if channel_layer:
                        async_to_sync(channel_layer.group_send)(
                            f'battle_room_{link.room_id}',
                            {
                                'type': 'battle_event',
                                'payload': {
                                    'type': 'room_finished',
                                    'room_id': str(link.room_id),
                                    'finish_reason': link.room.finish_reason,
                                    'winner_id': link.room.winner_id,
                                },
                            },
                        )
    except Exception:
        pass
    if submission.status == StatusChoices.ACCEPTED:
        submission.problem.accepted_count += 1
        submission.problem.save(update_fields=['accepted_count'])
        ProblemSolve.objects.get_or_create(user=submission.user,
                                           problem=submission.problem)
