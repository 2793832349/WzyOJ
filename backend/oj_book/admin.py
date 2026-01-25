from django.contrib import admin
from .models import Book, Chapter, Section, UserBookProgress


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 1
    ordering = ['order']


class SectionInline(admin.TabularInline):
    model = Section
    extra = 1
    ordering = ['order']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'is_published', 'is_free', 'reader_count', 'chapter_count', 'created_at']
    list_filter = ['difficulty', 'is_published', 'is_free']
    search_fields = ['title', 'description']
    inlines = [ChapterInline]
    ordering = ['order', '-created_at']


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['title', 'book', 'order', 'section_count']
    list_filter = ['book']
    search_fields = ['title']
    inlines = [SectionInline]
    ordering = ['book', 'order']


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'chapter', 'content_type', 'order', 'estimated_time']
    list_filter = ['content_type', 'chapter__book']
    search_fields = ['title', 'content']
    ordering = ['chapter__book', 'chapter__order', 'order']
    filter_horizontal = ['problems']


@admin.register(UserBookProgress)
class UserBookProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'completed_count', 'total_count', 'progress_percent', 'last_read_at']
    list_filter = ['book']
    search_fields = ['user__username', 'book__title']
