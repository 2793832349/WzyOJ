from rest_framework import serializers
from .models import CourseVideo

class CourseVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseVideo
        fields = ['id', 'course_id', 'm3u8_url', 'status', 'error', 'created_at', 'updated_at']
        read_only_fields = ['id', 'm3u8_url', 'status', 'error', 'created_at', 'updated_at']