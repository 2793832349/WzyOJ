from django.contrib import admin

from .models import LiveParticipant, LiveSession


@admin.register(LiveSession)
class LiveSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'status', 'started_by', 'start_time', 'end_time')
    list_filter = ('status',)
    search_fields = ('course__title', 'started_by__username')


@admin.register(LiveParticipant)
class LiveParticipantAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'user', 'role', 'joined_at', 'left_at', 'muted', 'hand_raised')
    list_filter = ('role', 'muted', 'hand_raised')
    search_fields = ('user__username',)
