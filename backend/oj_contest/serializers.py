from django.core.cache import caches
from django.utils import timezone
from django.utils import timezone
from oj_problem.models import Problem
from oj_problem.serializers import ProblemSerializer
from oj_submission.models import StatusChoices, Submission
from oj_user.models import User
from oj_user.serializers import UserBriefSerializer
from rest_framework import serializers

from .models import Contest, ContestProblem, ContestUser


class ContestJoined(serializers.ReadOnlyField):

    def to_internal_value(self, data):
        pass

    def to_representation(self, value):
        request = self.context.get('request')
        return value.filter(id=request.user.id).exists()


class ContestSerializer(serializers.ModelSerializer):
    joined = ContestJoined(source='users')
    ranking_revealed_at = serializers.SerializerMethodField()

    class Meta:
        model = Contest
        fields = [
            'id', 'title', 'start_time', 'end_time', 'joined',
            'problem_list_mode', 'rule_type', 'freeze_time', 'ranking_revealed_at', 'allow_sign_up',
            'public_ranking', 'is_hidden'
        ]

    def get_ranking_revealed_at(self, obj):
        ts = caches['default'].get(f'contest_ranking_revealed_at_{obj.id}')
        return ts


class ContestBriefSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contest
        fields = ['id', 'title', 'problem_list_mode', 'is_hidden']


class ProblemsField(serializers.Field):

    def to_representation(self, value):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return []

        progress_cache = caches['contest_progress']

        # Problemset mode: must be joined to see problems (admins bypass)
        if value.problem_list_mode and not (
            request.user.is_staff or 'contest' in request.user.permissions
        ):
            if not value.users.filter(id=request.user.id).exists():
                return []

        if (
            'contest' not in request.user.permissions and value.start_time
            and value.start_time > timezone.now()
        ):
            return []
        cps = (
            ContestProblem.objects
            .filter(contest=value)
            .select_related('problem')
            .order_by('order', 'id')
        )
        problems = [cp.problem for cp in cps]

        problem_ids = [p.id for p in problems]
        reset_ts = progress_cache.get(f'contest_progress_reset_{value.id}_{request.user.id}')
        reset_dt = None
        if reset_ts:
            reset_dt = timezone.datetime.fromtimestamp(
                float(reset_ts),
                tz=timezone.get_current_timezone(),
            )

        solved_qs = Submission.objects.filter(
            user=request.user,
            problem_id__in=problem_ids,
            status=StatusChoices.ACCEPTED,
        )
        if reset_dt is not None:
            solved_qs = solved_qs.filter(create_time__gte=reset_dt)

        solved_problem_ids = set(solved_qs.values_list('problem_id', flat=True).distinct())

        now = timezone.now()
        is_admin = request.user.is_staff or 'contest' in request.user.permissions
        in_window = (
            (value.start_time is None or value.start_time < now)
            and (value.end_time is None or value.end_time > now)
        )
        if value.rule_type == 'OI' and in_window and not is_admin:
            solved_problem_ids = set()

        context = {**self.context, 'solved_problem_ids': solved_problem_ids}
        return ProblemSerializer(problems, many=True, context=context).data

    def to_internal_value(self, data):
        if not isinstance(data, list):
            raise serializers.ValidationError('problems 必须是题目 ID 列表')

        ids = []
        for i in data:
            try:
                ids.append(int(i))
            except (TypeError, ValueError):
                raise serializers.ValidationError('problems 必须是题目 ID 列表')

        problems = [Problem.objects.get(id=i) for i in ids]
        return {'problems': problems, '_problem_order_ids': ids}


class UsersField(serializers.Field):

    def to_representation(self, value):
        return UserBriefSerializer(value, many=True).data

    def to_internal_value(self, data):
        return [User.objects.get(id=i) for i in data]


class ContestDetailSerializer(serializers.ModelSerializer):
    joined = ContestJoined(source='users')
    problems = ProblemsField(required=False, source='*')
    users = UsersField(required=False)
    ranking_revealed_at = serializers.SerializerMethodField()

    class Meta:
        model = Contest
        fields = [
            'id', 'title', 'start_time', 'end_time', 'joined', 'description',
            'problem_list_mode', 'rule_type', 'freeze_time', 'ranking_revealed_at', 'public_ranking',
            'is_hidden', 'allow_sign_up', 'problems', 'users'
        ]
        read_only_fields = ['id']

    def get_ranking_revealed_at(self, obj):
        ts = caches['default'].get(f'contest_ranking_revealed_at_{obj.id}')
        return ts

    def _apply_problem_order(self, contest, problem_ids):
        if problem_ids is None:
            return
        order_map = {pid: idx for idx, pid in enumerate(problem_ids)}

        # Remove relations not in incoming list
        ContestProblem.objects.filter(contest=contest).exclude(problem_id__in=problem_ids).delete()

        # Upsert order for remaining/new
        for pid in problem_ids:
            ContestProblem.objects.update_or_create(
                contest=contest,
                problem_id=pid,
                defaults={'order': order_map[pid]},
            )

    def create(self, validated_data):
        problem_ids = validated_data.pop('_problem_order_ids', None)
        contest = super().create(validated_data)
        self._apply_problem_order(contest, problem_ids)
        return contest

    def update(self, instance, validated_data):
        problem_ids = validated_data.pop('_problem_order_ids', None)
        contest = super().update(instance, validated_data)
        self._apply_problem_order(contest, problem_ids)
        return contest
