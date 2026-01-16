from rest_framework import serializers

from oj_problem.serializers import ProblemBriefSerializer
from oj_user.serializers import UserBriefSerializer

from .models import BattleParticipant, BattleRating, BattleResult, BattleRoom, BattleSeason


class BattleParticipantSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer(read_only=True)

    class Meta:
        model = BattleParticipant
        fields = ['user', 'side', 'joined_at']


class BattleRoomSerializer(serializers.ModelSerializer):
    created_by = UserBriefSerializer(read_only=True)
    problem = ProblemBriefSerializer(read_only=True)
    participants = BattleParticipantSerializer(many=True, read_only=True)
    winner = UserBriefSerializer(read_only=True)

    class Meta:
        model = BattleRoom
        fields = [
            'id',
            'room_type',
            'status',
            'created_by',
            'problem',
            'difficulty_min',
            'difficulty_max',
            'duration_seconds',
            'start_time',
            'end_time',
            'winner',
            'finish_reason',
            'create_time',
            'participants',
        ]


class BattleSeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = BattleSeason
        fields = ['id', 'name', 'start_time', 'end_time', 'is_active', 'inherit_ratio', 'created_at']


class BattleRatingSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer(read_only=True)
    win_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = BattleRating
        fields = [
            'id',
            'user',
            'rating',
            'battle_level',
            'experience',
            'total_battles',
            'wins',
            'losses',
            'win_rate',
            'peak_rating',
            'updated_at',
        ]


class BattleResultSerializer(serializers.ModelSerializer):
    user_a = UserBriefSerializer(read_only=True)
    user_b = UserBriefSerializer(read_only=True)
    winner = UserBriefSerializer(read_only=True)
    
    class Meta:
        model = BattleResult
        fields = [
            'id',
            'user_a',
            'user_b',
            'winner',
            'user_a_rating_before',
            'user_a_rating_change',
            'user_a_exp_change',
            'user_a_ac_time',
            'user_a_gave_up',
            'user_a_bonus_time',
            'user_b_rating_before',
            'user_b_rating_change',
            'user_b_exp_change',
            'user_b_ac_time',
            'user_b_gave_up',
            'user_b_bonus_time',
            'created_at',
        ]
