import os
import uuid
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import CourseVideo
from .serializers import CourseVideoSerializer
from .tasks import transcode_to_hls

class CourseVideoUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, course_id, format=None):
        f = request.FILES.get('file')
        if not f:
            return Response({'detail': 'no file'}, status=status.HTTP_400_BAD_REQUEST)

        filename = f'{uuid.uuid4().hex}_{f.name}'
        save_path = os.path.join('course_videos', 'originals', filename)
        full_path = os.path.join(settings.MEDIA_ROOT, save_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'wb') as wf:
            for chunk in f.chunks():
                wf.write(chunk)

        cv = CourseVideo.objects.create(
            course_id=course_id,
            original_file=save_path,
            status=CourseVideo.STATUS_PENDING,
        )

        transcode_to_hls.delay(cv.id)

        serializer = CourseVideoSerializer(cv)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CourseVideoDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id, pk, format=None):
        try:
            cv = CourseVideo.objects.get(pk=pk, course_id=course_id)
        except CourseVideo.DoesNotExist:
            return Response({'detail': 'not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CourseVideoSerializer(cv)
        return Response(serializer.data)