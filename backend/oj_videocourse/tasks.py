"""
录播课视频处理异步任务
"""

from celery import shared_task
from django.core.files.storage import default_storage
from .models import VideoCourseChapter
from .video_processor import VideoCourseVideoProcessor
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_videocourse_video(self, chapter_id):
    """
    异步处理视频课程视频
    
    将 MP4 视频转码为 HLS (m3u8) 格式
    支持自动重试（最多 3 次）
    """
    try:
        chapter = VideoCourseChapter.objects.get(id=chapter_id)
        
        if not chapter.video_file:
            chapter.video_status = 'failed'
            chapter.error_message = '没有视频文件'
            chapter.save()
            return
        
        # 更新状态为处理中
        chapter.video_status = 'processing'
        chapter.save()
        
        # 获取视频文件路径
        video_path = chapter.video_file.path
        
        # 创建处理器并处理视频
        processor = VideoCourseVideoProcessor()
        output_info = processor.process(video_path, chapter_id)
        
        # 更新章节信息
        chapter.video_status = 'completed'
        chapter.m3u8_playlist = output_info['m3u8_url']
        chapter.duration = output_info.get('duration', 0)
        chapter.resolution = output_info.get('resolution', '')
        chapter.bitrate = output_info.get('bitrate', '')
        chapter.error_message = ''
        chapter.save()
        
        logger.info(f"视频课程视频处理成功: chapter_id={chapter_id}")
        
    except VideoCourseChapter.DoesNotExist:
        logger.error(f"视频课程章节不存在: chapter_id={chapter_id}")
    except Exception as e:
        logger.error(f"视频课程视频处理失败: {str(e)}")
        
        try:
            chapter = VideoCourseChapter.objects.get(id=chapter_id)
            chapter.error_message = str(e)
            chapter.save()
        except:
            pass
        
        # 自动重试，使用指数退避
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
