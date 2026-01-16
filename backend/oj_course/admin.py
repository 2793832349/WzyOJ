from django.contrib import admin

from .models import ChapterProblem, Course, CourseChapter, CourseEnrollment

admin.site.register(Course)
admin.site.register(CourseEnrollment)
admin.site.register(CourseChapter)
admin.site.register(ChapterProblem)
