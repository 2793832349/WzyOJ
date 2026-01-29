from celery import shared_task
from django.conf import settings
from oj_course.models import CourseChapter
import os
import subprocess
from urllib.parse import urljoin

@shared_task(bind=True, soft_time_limit=1800)
def transcode_video_to_hls(self, chapter_id):
    """
    Celery task: transcode an uploaded video (chapter.video) into HLS format and
    write the public index.m3u8 URL to chapter.hls_url. This implementation assumes
    the worker can access MEDIA_ROOT (local filesystem). For S3/OSS adjust download/upload.
    """
    try:
        chapter = CourseChapter.objects.get(id=chapter_id)
        if not chapter.video:
            chapter.video_processing = False
            chapter.video_processing_error = 'no source video'
            chapter.save(update_fields=['video_processing', 'video_processing_error'])
            return

        src_path = chapter.video.path
        out_dir = os.path.join(settings.MEDIA_ROOT, 'hls', f'chapter_{chapter_id}')
        os.makedirs(out_dir, exist_ok=True)
        out_m3u8 = os.path.join(out_dir, 'index.m3u8')

        # Basic single-bitrate HLS generation. Consider multi-bitrate/master playlist for production.
        cmd = [
            'ffmpeg', '-y', '-i', src_path,
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
            '-c:a', 'aac', '-b:a', '128k',
            '-hls_time', '8', '-hls_list_size', '0',
            '-hls_segment_filename', os.path.join(out_dir, 'seg_%03d.ts'),
            out_m3u8
        ]

        subprocess.check_call(cmd)

        media_url = getattr(settings, 'MEDIA_URL', '/media/')
        site_base = getattr(settings, 'SITE_BASE_URL', '')
        # Build public URL for the generated m3u8
        # Ensure SITE_BASE_URL ends with '/'
        if site_base and not site_base.endswith('/):
            site_base += '/'  
        public_m3u8 = urljoin(site_base, os.path.join(media_url.lstrip('/'), 'hls', f'chapter_{chapter_id}', 'index.m3u8'))

        chapter.hls_url = public_m3u8
        chapter.video_processing = False
        chapter.video_processing_error = ''
        chapter.save(update_fields=['hls_url', 'video_processing', 'video_processing_error'])
        return public_m3u8

    except Exception as e:
        try:
            chapter.video_processing = False
            chapter.video_processing_error = str(e)
            chapter.save(update_fields=['video_processing', 'video_processing_error'])
        except Exception:
            pass
        raise
