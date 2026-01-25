from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import User
from oj_contest.models import Contest
from oj_problem.serializers import (ProblemBriefSerializer,
                                    ProblemSolveSerializer)
from oj_submission.models import StatusChoices, Submission


def _is_admin_user(user) -> bool:
    perms = getattr(user, 'permissions', [])
    return any([
        getattr(user, 'is_staff', False),
        getattr(user, 'is_superuser', False),
        'submission' in perms,
        'contest' in perms,
        'problem' in perms,
    ])


def _processing_contests(now):
    return (
        Contest.objects
        .filter(problem_list_mode=False)
        .filter(Q(start_time__isnull=True) | Q(start_time__lt=now))
        .filter(Q(end_time__isnull=True) | Q(end_time__gt=now))
    )


def _exclude_processing_contest_window_submissions(qs, now):
    processing = list(_processing_contests(now).values_list('id', 'start_time', 'end_time'))
    if not processing:
        return qs

    q = Q()
    for contest_id, start_time, end_time in processing:
        cq = Q(problem__contests__contest_id=contest_id)
        if start_time is not None:
            cq &= Q(create_time__gte=start_time)
        if end_time is not None:
            cq &= Q(create_time__lte=end_time)
        q |= cq
    return qs.exclude(q).distinct()


def _exclude_processing_contest_window_solves(qs, now):
    processing = list(_processing_contests(now).values_list('id', 'start_time', 'end_time'))
    if not processing:
        return qs

    q = Q()
    for contest_id, start_time, end_time in processing:
        cq = Q(problem__contests__contest_id=contest_id)
        if start_time is not None:
            cq &= Q(create_time__gte=start_time)
        if end_time is not None:
            cq &= Q(create_time__lte=end_time)
        q |= cq
    return qs.exclude(q).distinct()


class UserBriefSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'real_name', 'avatar']


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'real_name', 'student_id', 'avatar',
            'permissions', 'is_superuser', 'is_staff', 'is_active'
        ]
        read_only_fields = ['id', 'username', 'is_superuser', 'is_staff', 'is_active']


class _SubmissionSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer()
    problem = ProblemBriefSerializer()

    class Meta:
        model = Submission
        fields = [
            'id', 'user', 'problem', 'language', 'status', 'score',
            'execute_time', 'execute_memory', 'create_time'
        ]
        read_only_fields = [
            'status', 'score', 'execute_time', 'execute_memory', 'create_time'
        ]


class UserSubmissionField(serializers.ListField):

    def to_internal_value(self, data):
        pass

    def to_representation(self, value):
        request_user = self.context['request'].user
        now = timezone.now()

        if not _is_admin_user(request_user):
            value = _exclude_processing_contest_window_submissions(value, now)

        if not value.exists():
            return []

        profile_user = getattr(self.parent, 'instance', None)
        is_owner = bool(
            profile_user
            and getattr(profile_user, 'id', None) is not None
            and getattr(request_user, 'id', None) is not None
            and profile_user.id == request_user.id
        )

        if 'submission' not in getattr(request_user, 'permissions', []) and not is_owner:
            value = value.exclude(
                Q(_is_hidden=True) | Q(problem___is_hidden=True)
                | Q(problem__hide_submissions=True)
            ).distinct()
        return _SubmissionSerializer(value.order_by('-id')[:10],
                                     many=True).data


class AcceptedCountField(serializers.ReadOnlyField):

    def to_internal_value(self, data):
        pass

    def to_representation(self, value):
        request = self.context.get('request')
        user = getattr(request, 'user', None) if request else None
        if user is None:
            return value.filter(status=StatusChoices.ACCEPTED).count()

        if _is_admin_user(user):
            return value.filter(status=StatusChoices.ACCEPTED).count()

        now = timezone.now()
        qs = _exclude_processing_contest_window_submissions(value, now)
        return qs.filter(status=StatusChoices.ACCEPTED).count()


class SubmissionCountField(serializers.ReadOnlyField):

    def to_internal_value(self, data):
        pass

    def to_representation(self, value):
        request = self.context.get('request')
        user = getattr(request, 'user', None) if request else None
        if user is None:
            return value.count()

        if _is_admin_user(user):
            return value.count()

        now = timezone.now()
        qs = _exclude_processing_contest_window_submissions(value, now)
        return qs.count()


class SolvedProblemsField(serializers.ListField):

    def to_internal_value(self, data):
        pass

    def to_representation(self, value):
        request = self.context.get('request')
        user = getattr(request, 'user', None) if request else None
        if user is None:
            return ProblemSolveSerializer(value.order_by('-id'), many=True).data

        if _is_admin_user(user):
            return ProblemSolveSerializer(value.order_by('-id'), many=True).data

        now = timezone.now()
        qs = _exclude_processing_contest_window_solves(value, now)
        return ProblemSolveSerializer(qs.order_by('-id'), many=True).data


class UserDetailSerializer(serializers.ModelSerializer):
    solved_problems = SolvedProblemsField(source='problem_solve', read_only=True)
    submission_count = SubmissionCountField(source='submissions')
    accepted_count = AcceptedCountField(source='submissions')
    submissions = UserSubmissionField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'real_name', 'student_id',
            'permissions', 'avatar', 'solved_problems', 'submission_count',
            'accepted_count', 'submissions'
        ]


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(label=_('username'), max_length=150)
    password = serializers.CharField(label=_('password'))

    class Meta:
        model = User
        fields = ['username', 'password']


class CreateUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(label=_('username'), max_length=150)
    password = serializers.CharField(label=_('password'), write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'real_name', 'student_id', 'permissions']

    def create(self, validated_data):
        password = validated_data.pop('password')
        return User.objects.create_user(password=password, **validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(label=_('old password'))
    new_password = serializers.CharField(label=_('new password'))

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(_('Old password error.'))
        return value
