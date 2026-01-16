from rest_framework import serializers

from oj_user.serializers import UserBriefSerializer

from .models import LiveParticipant, LiveSession


class LiveParticipantSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer(read_only=True)

    class Meta:
        model = LiveParticipant
        fields = ['id', 'user', 'role', 'joined_at', 'left_at', 'muted', 'hand_raised']


class LiveSessionSerializer(serializers.ModelSerializer):
    course_id = serializers.IntegerField(source='course.id', read_only=True)
    started_by = UserBriefSerializer(read_only=True)
    participants = LiveParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = LiveSession
        fields = ['id', 'course_id', 'title', 'status', 'started_by', 'start_time', 'end_time', 'created_at', 'participants']
