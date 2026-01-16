import random

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from oj_backend.permissions import IsAuthenticatedAndReadCreate
from oj_problem.models import ProblemSolve
from oj_problem.views import get_problem_queryset
from oj_submission.serializers import SubmissionSerializer
from oj_submission.models import Submission
from oj_submission.tasks import judge

from .models import (
    BattleParticipant,
    BattleParticipantSide,
    BattleRoom,
    BattleRoomStatus,
    BattleRoomType,
    BattleSubmissionLink,
)
from .serializers import BattleRoomSerializer
from .tasks import finish_room_if_timeout


def _parse_int(v):
    if v is None or v == '':
        return None
    return int(v)


def _validate_difficulty_range(dmin, dmax):
    if dmin is None and dmax is None:
        return
    if dmin is None or dmax is None:
        raise ValidationError('difficulty_min/difficulty_max 需要同时提供')
    if dmin < 0 or dmax < 0 or dmin > 6 or dmax > 6:
        raise ValidationError('difficulty 取值范围为 0~6')
    if dmin > dmax:
        raise ValidationError('difficulty_min 不能大于 difficulty_max')


def _pick_problem_for_room(request, room, user_ids):
    qs_base = get_problem_queryset(request).filter(_allow_submit=True).order_by('id')

    dmin = room.difficulty_min
    dmax = room.difficulty_max

    if len(user_ids) >= 2:
        u1, u2 = user_ids[0], user_ids[1]
    elif len(user_ids) == 1:
        u1, u2 = user_ids[0], user_ids[0]
    else:
        u1, u2 = None, None

    solved1 = set()
    solved2 = set()
    if u1 is not None:
        solved1 = set(ProblemSolve.objects.filter(user_id=u1).values_list('problem_id', flat=True))
    if u2 is not None:
        solved2 = set(ProblemSolve.objects.filter(user_id=u2).values_list('problem_id', flat=True))

    def choose_from(qs, predicate):
        cand = list(qs[:500])
        random.shuffle(cand)
        for p in cand:
            try:
                if not p.allow_submit:
                    continue
            except Exception:
                continue
            if predicate(p.id):
                return p
        return None

    def with_range(qs):
        if dmin is None or dmax is None:
            return qs
        return qs.filter(difficulty__gte=dmin, difficulty__lte=dmax)

    union = solved1 | solved2
    inter = solved1 & solved2

    p = choose_from(with_range(qs_base), lambda pid: pid not in union)
    if p:
        return p

    p = choose_from(with_range(qs_base), lambda pid: pid not in inter)
    if p:
        return p

    p = choose_from(qs_base, lambda pid: pid not in union)
    if p:
        return p

    p = choose_from(qs_base, lambda pid: pid not in inter)
    if p:
        return p

    p = choose_from(qs_base, lambda _pid: True)
    return p


def _send_room_event(room_id: str, payload: dict):
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    async_to_sync(channel_layer.group_send)(
        f'battle_room_{room_id}',
        {
            'type': 'battle_event',
            'payload': payload,
        },
    )


class BattleRoomViewSet(ModelViewSet):
    queryset = BattleRoom.objects.all().order_by('-create_time')
    serializer_class = BattleRoomSerializer
    permission_classes = [IsAuthenticatedAndReadCreate]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        from django.db.models import Q
        user = self.request.user
        if not user.is_authenticated:
            return BattleRoom.objects.none()
        if user.is_staff:
            return BattleRoom.objects.all().order_by('-create_time')
        return BattleRoom.objects.filter(
            Q(participants__user_id=user.id) | Q(status=BattleRoomStatus.WAITING)
        ).distinct().order_by('-create_time')

    def create(self, request, *args, **kwargs):
        user = request.user
        if not user.is_active:
            raise ValidationError('您的账号已被封禁，无法创建对战房间')

        room_type = request.data.get('room_type') or BattleRoomType.FRIEND
        duration_seconds = int(request.data.get('duration_seconds') or 1800)
        if duration_seconds <= 0 or duration_seconds > 4 * 3600:
            raise ValidationError('duration_seconds 非法')

        difficulty_min = _parse_int(request.data.get('difficulty_min'))
        difficulty_max = _parse_int(request.data.get('difficulty_max'))
        _validate_difficulty_range(difficulty_min, difficulty_max)

        with transaction.atomic():
            room = BattleRoom.objects.create(
                room_type=room_type,
                duration_seconds=duration_seconds,
                created_by=user,
                difficulty_min=difficulty_min,
                difficulty_max=difficulty_max,
            )
            BattleParticipant.objects.create(room=room, user=user, side=BattleParticipantSide.A)

        serializer = self.get_serializer(room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='join')
    def join(self, request, pk=None):
        room: BattleRoom = self.get_object()
        user = request.user

        if room.status != BattleRoomStatus.WAITING:
            return Response({'error': '房间已开始或已结束，无法加入'}, status=400)
        if room.participants.filter(user_id=user.id).exists():
            return Response(self.get_serializer(room).data)
        if room.participants.count() >= 2:
            return Response({'error': '房间已满'}, status=400)

        side = BattleParticipantSide.B
        with transaction.atomic():
            BattleParticipant.objects.create(room=room, user=user, side=side)

        data = self.get_serializer(room).data
        _send_room_event(str(room.id), {'type': 'participant_joined', 'room': data})
        return Response(data)

    @action(detail=True, methods=['post'], url_path='start')
    def start(self, request, pk=None):
        room: BattleRoom = self.get_object()
        user = request.user

        if room.created_by_id != user.id and not user.is_staff:
            return Response({'error': '只有房主可以开始对战'}, status=403)
        if room.status != BattleRoomStatus.WAITING:
            return Response({'error': '房间不是等待状态'}, status=400)
        if room.participants.count() != 2:
            return Response({'error': '需要两名玩家才能开始'}, status=400)

        problem_id = request.data.get('problem_id')
        problem = None
        if problem_id:
            qs = get_problem_queryset(request)
            problem = qs.filter(id=int(problem_id)).first()
        if not problem:
            user_ids = list(room.participants.values_list('user_id', flat=True).order_by('id'))
            problem = _pick_problem_for_room(request, room, user_ids)

        if not problem:
            return Response({'error': '未找到可用题目'}, status=400)

        room.problem = problem
        room.status = BattleRoomStatus.RUNNING
        room.start_time = timezone.now()
        room.end_time = None
        room.winner = None
        room.finish_reason = None
        room.save(update_fields=['problem', 'status', 'start_time', 'end_time', 'winner', 'finish_reason'])

        finish_room_if_timeout.apply_async(args=[str(room.id)], countdown=room.duration_seconds)

        data = self.get_serializer(room).data
        _send_room_event(str(room.id), {'type': 'room_started', 'room': data})
        return Response(data)

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):
        room: BattleRoom = self.get_object()
        user = request.user

        if room.status != BattleRoomStatus.RUNNING:
            return Response({'error': '房间未开始或已结束'}, status=400)
        if not room.participants.filter(user_id=user.id).exists() and not user.is_staff:
            return Response({'error': '你不是该房间参与者'}, status=403)
        if not room.problem_id:
            return Response({'error': '房间尚未分配题目'}, status=400)
        
        # 检查用户是否已经 AC 了，AC 后不允许再次提交
        from oj_submission.models import StatusChoices
        user_ac_submission = BattleSubmissionLink.objects.filter(
            room=room, 
            user=user, 
            submission__status=StatusChoices.ACCEPTED
        ).exists()
        if user_ac_submission:
            return Response({'error': '你已经通过了本题，无法再次提交'}, status=400)

        language = (request.data.get('language') or '').strip()
        source = request.data.get('source') or ''
        if not language or not source:
            return Response({'error': 'language/source 不能为空'}, status=400)

        submission = Submission.objects.create(
            user=user,
            problem_id=room.problem_id,
            language=language,
            source=source,
        )

        BattleSubmissionLink.objects.create(room=room, user=user, submission=submission)

        judge.delay(
            submission.id,
            submission.problem.test_case.test_case_id,
            submission.problem.test_case.spj_id if submission.problem.test_case.use_spj else None,
            submission.problem.test_case.test_case_config,
            submission.problem.test_case.subcheck_config if submission.problem.test_case.use_subcheck else None,
            submission.language,
            submission.source,
            {
                'max_cpu_time': submission.problem.time_limit,
                'max_memory': submission.problem.memory_limit * 1024 * 1024,
            },
        )
        submission.problem.submission_count += 1
        submission.problem.save(update_fields=['submission_count'])

        _send_room_event(
            str(room.id),
            {
                'type': 'submission_created',
                'room_id': str(room.id),
                'user_id': user.id,
                'submission_id': submission.id,
                'status': submission.status,
                'create_time': int(submission.create_time.timestamp()) if submission.create_time else None,
            },
        )

        return Response({'submission_id': submission.id})

    @action(detail=True, methods=['get'], url_path='timeline')
    def timeline(self, request, pk=None):
        room: BattleRoom = self.get_object()

        user = request.user
        if not room.participants.filter(user_id=user.id).exists() and not user.is_staff:
            return Response({'error': '你不是该房间参与者'}, status=403)

        links = (
            room.battle_submissions
            .select_related('submission', 'user')
            .order_by('created_at', 'id')
        )
        submissions = [link.submission for link in links]
        data = SubmissionSerializer(submissions, many=True, context={'request': request}).data
        return Response({'room_id': str(room.id), 'submissions': data})
