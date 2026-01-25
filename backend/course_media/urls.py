from django.urls import path
from .views import CourseVideoUploadView, CourseVideoDetailView

urlpatterns = [
    path('course/<int:course_id>/videos/', CourseVideoUploadView.as_view(), name='course_video_upload'),
    path('course/<int:course_id>/videos/<int:pk>/', CourseVideoDetailView.as_view(), name='course_video_detail'),
]