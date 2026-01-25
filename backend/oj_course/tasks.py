"""
视频处理相关的异步任务
"""
from celery import shared_task
from .models import CourseChapter, VideoProcessingStatus
from .video_processor import VideoProcessor
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_chapter_video(self, chapter_id):
    """
    异步处理章节视频转换任务
    
    Args:
        chapter_id: 课程章节 ID
    """
    try:
        chapter = CourseChapter.objects.get(id=chapter_id)
        
        if not chapter.video:
            logger.warning(f'章节 {chapter_id} 没有上传视频')
            return False
        
        processor = VideoProcessor(chapter)
        success = processor.process()
        
        return success
        
    except CourseChapter.DoesNotExist:
        logger.error(f'找不到章节: {chapter_id}')
        return False
    except Exception as e:
        logger.error(f'视频处理失败: {str(e)}')
        # 重试 3 次，间隔为 60, 300, 600 秒
        raise self.retry(exc=e, countdown=2 ** self.request.retries * 60)


@shared_task
def check_video_processing_status(chapter_id):
    """检查视频处理状态"""
    try:
        chapter = CourseChapter.objects.get(id=chapter_id)
        return {
            'chapter_id': chapter_id,
            'status': chapter.video_status,
            'duration': chapter.duration,
            'resolution': chapter.resolution,
            'error': chapter.error_message if chapter.video_status == VideoProcessingStatus.FAILED else None
        }
    except CourseChapter.DoesNotExist:
        return None
