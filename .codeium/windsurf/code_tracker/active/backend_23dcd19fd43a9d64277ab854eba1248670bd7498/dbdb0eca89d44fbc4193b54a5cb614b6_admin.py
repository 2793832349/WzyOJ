�from django.contrib import admin
from .models import Class, ClassStudent, ClassProblem, Assignment, AssignmentProblem


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'teacher', 'is_hidden', 'created_at']
    list_filter = ['is_hidden', 'created_at']
    search_fields = ['title', 'teacher__username']
    date_hierarchy = 'created_at'


@admin.register(ClassStudent)
class ClassStudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'class_obj', 'user', 'role', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['class_obj__title', 'user__username']


@admin.register(ClassProblem)
class ClassProblemAdmin(admin.ModelAdmin):
    list_display = ['id', 'class_obj', 'get_title', 'is_reference', 'order', 'created_at']
    list_filter = ['is_reference', 'created_at']
    search_fields = ['class_obj__title', 'title', 'reference_problem__title']
    
    def get_title(self, obj):
        return obj.get_title()
    get_title.short_description = '题目标题'


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'class_obj', 'title', 'deadline', 'is_hidden', 'created_at']
    list_filter = ['is_hidden', 'deadline', 'created_at']
    search_fields = ['title', 'class_obj__title']
    date_hierarchy = 'created_at'


@admin.register(AssignmentProblem)
class AssignmentProblemAdmin(admin.ModelAdmin):
    list_display = ['id', 'assignment', 'problem', 'order']
    list_filter = ['assignment__class_obj']
    search_fields = ['assignment__title', 'problem__title']
�*cascade08"(23dcd19fd43a9d64277ab854eba1248670bd74982&file:///root/backend/oj_class/admin.py:file:///root/backend