from django.contrib import admin

from .models import (
    ObjectivePaper,
    ObjectivePaperItem,
    ObjectivePaperSubmission,
    ObjectiveQuestion,
    ObjectiveSubmission,
)


@admin.register(ObjectiveQuestion)
class ObjectiveQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'question_type', 'difficulty', '_is_hidden', 'submission_count', 'accepted_count')
    search_fields = ('id', 'title')
    list_filter = ('question_type', '_is_hidden', 'difficulty')


@admin.register(ObjectiveSubmission)
class ObjectiveSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'user', 'is_correct', 'create_time')
    search_fields = ('question__title', 'user__username')
    list_filter = ('is_correct',)


@admin.register(ObjectivePaper)
class ObjectivePaperAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'pass_score', '_is_hidden', 'create_time', 'update_time')
    search_fields = ('id', 'title')
    list_filter = ('_is_hidden',)


@admin.register(ObjectivePaperItem)
class ObjectivePaperItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'paper', 'question', 'order', 'score')
    search_fields = ('paper__title', 'question__title')


@admin.register(ObjectivePaperSubmission)
class ObjectivePaperSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'paper', 'user', 'total_score', 'max_score', 'is_pass', 'create_time')
    search_fields = ('paper__title', 'user__username')
    list_filter = ('is_pass',)
