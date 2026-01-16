from django.contrib import admin

from .models import BattleParticipant, BattleRoom, BattleSubmissionLink


@admin.register(BattleRoom)
class BattleRoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'room_type', 'status', 'created_by', 'problem', 'start_time', 'end_time', 'winner']
    list_filter = ['room_type', 'status']
    search_fields = ['id']


@admin.register(BattleParticipant)
class BattleParticipantAdmin(admin.ModelAdmin):
    list_display = ['room', 'user', 'side', 'joined_at']
    list_filter = ['side']


@admin.register(BattleSubmissionLink)
class BattleSubmissionLinkAdmin(admin.ModelAdmin):
    list_display = ['room', 'user', 'submission', 'created_at']
