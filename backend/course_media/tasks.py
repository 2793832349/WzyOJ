import os
import shutil
import subprocess
from django.conf import settings
from celery import shared_task
from .models import CourseVideo

@shared_task(bind=True)
def transcode_to_hls(self, course_video_id):
    try:
        cv = CourseVideo.objects.get(id=course_video_id)
    except CourseVideo.DoesNotExist:
        return

    cv.status = CourseVideo.STATUS_PROCESSING
    cv.save(update_fields=['status'])

    original_path = os.path.join(settings.MEDIA_ROOT, cv.original_file.name)
    out_dir = os.path.join(settings.MEDIA_ROOT, 'course_videos', 'hls', str(cv.id))
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    out_m3u8 = os.path.join(out_dir, 'index.m3u8')
    cmd = [
        'ffmpeg',
        '-y',
        '-i', original_path,
        '-profile:v', 'baseline',
        '-level', '3.0',
        '-start_number', '0',
        '-hls_time', '10',
        '-hls_list_size', '0',
        '-f', 'hls',
        out_m3u8
    ]

    try:
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        rel_dir = os.path.relpath(out_dir, settings.MEDIA_ROOT)
        m3u8_url = os.path.join(settings.MEDIA_URL.rstrip('/'), rel_dir.replace(os.sep, '/'), 'index.m3u8')
        cv.hls_dir = rel_dir
        cv.m3u8_url = m3u8_url
        cv.status = CourseVideo.STATUS_READY
        cv.error = ''
        cv.save(update_fields=['hls_dir', 'm3u8_url', 'status', 'error'])
    except subprocess.CalledProcessError as e:
        cv.status = CourseVideo.STATUS_FAILED
        cv.error = e.output.decode(errors='ignore') if isinstance(e.output, (bytes, bytearray)) else str(e)
        cv.save(update_fields=['status', 'error'])
        raise