"""
视频处理模块：MP4 转换为 HLS (m3u8/ts) 格式
"""
import os
import json
import logging
import subprocess
from pathlib import Path
from django.conf import settings
from django.core.files.base import ContentFile
from .models import CourseChapter, VideoProcessingStatus

logger = logging.getLogger(__name__)


class VideoProcessor:
    """视频处理器 - 将 MP4 转换为 m3u8 + ts segments"""
    
    # 视频段时长（秒）
    SEGMENT_DURATION = 10
    
    # 支持的分辨率和码率预设
    PRESETS = {
        'hd': {
            'resolution': '1280x720',
            'bitrate': '3000k',
            'label': 'HD (720p)'
        },
        'sd': {
            'resolution': '854x480',
            'bitrate': '1500k',
            'label': 'SD (480p)'
        },
        'mobile': {
            'resolution': '640x360',
            'bitrate': '800k',
            'label': 'Mobile (360p)'
        }
    }
    
    def __init__(self, chapter: CourseChapter):
        self.chapter = chapter
        self.logger = logging.getLogger(__name__)
        
    def process(self):
        """处理视频"""
        try:
            self.chapter.video_status = VideoProcessingStatus.PROCESSING
            self.chapter.error_message = ''
            self.chapter.save()
            
            # 获取视频信息
            video_info = self._get_video_info()
            if not video_info:
                raise Exception('无法获取视频信息')
            
            # 创建输出目录
            output_dir = self._create_output_directory()
            
            # 转换视频为 HLS 格式
            m3u8_path = self._convert_to_hls(output_dir)
            
            # 保存处理信息
            self._save_processing_info(output_dir, m3u8_path, video_info)
            
            self.chapter.video_status = VideoProcessingStatus.COMPLETED
            self.chapter.save()
            
            self.logger.info(f'视频处理成功: Chapter {self.chapter.id}')
            return True
            
        except Exception as e:
            self.logger.error(f'视频处理失败: {str(e)}')
            self.chapter.video_status = VideoProcessingStatus.FAILED
            self.chapter.error_message = str(e)
            self.chapter.save()
            return False
    
    def _get_video_info(self):
        """获取视频信息"""
        try:
            video_path = self.chapter.video.path
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_format',
                '-show_streams',
                '-print_json',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return None
                
            data = json.loads(result.stdout)
            format_data = data.get('format', {})
            
            info = {
                'duration': int(float(format_data.get('duration', 0))),
                'size': int(format_data.get('size', 0)),
            }
            
            # 获取视频流信息
            for stream in data.get('streams', []):
                if stream['codec_type'] == 'video':
                    info['width'] = stream.get('width', 0)
                    info['height'] = stream.get('height', 0)
                    break
            
            return info
        except Exception as e:
            self.logger.error(f'获取视频信息失败: {str(e)}')
            return None
    
    def _create_output_directory(self):
        """创建输出目录"""
        # 使用媒体根目录
        media_root = settings.MEDIA_ROOT
        output_dir = os.path.join(
            media_root,
            'course_videos_hls',
            str(self.chapter.course.id),
            str(self.chapter.id)
        )
        
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    def _convert_to_hls(self, output_dir):
        """转换视频为 HLS 格式"""
        video_path = self.chapter.video.path
        m3u8_path = os.path.join(output_dir, 'index.m3u8')
        segment_pattern = os.path.join(output_dir, 'segment_%03d.ts')
        
        # FFmpeg HLS 转换命令
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-c:v', 'libx264',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-f', 'hls',
            '-hls_time', str(self.SEGMENT_DURATION),
            '-hls_list_size', '0',  # 不限制列表大小
            '-hls_segment_filename', segment_pattern,
            m3u8_path
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600  # 1小时超时
        )
        
        if result.returncode != 0:
            raise Exception(f'FFmpeg 转换失败: {result.stderr}')
        
        return m3u8_path
    
    def _save_processing_info(self, output_dir, m3u8_path, video_info):
        """保存处理信息"""
        # 读取 m3u8 文件内容
        with open(m3u8_path, 'r') as f:
            m3u8_content = f.read()
        
        # 保存 m3u8 内容到数据库
        self.chapter.m3u8_playlist = m3u8_content
        
        # 计算相对路径用于前端请求
        relative_path = os.path.relpath(
            output_dir,
            settings.MEDIA_ROOT
        )
        self.chapter.video_segments_dir = relative_path
        
        # 提取视频信息
        self.chapter.duration = video_info.get('duration', 0)
        
        # 保存元数据
        if 'width' in video_info and 'height' in video_info:
            self.chapter.resolution = f"{video_info['width']}x{video_info['height']}"
        
        self.chapter.save()
    
    @staticmethod
    def generate_adaptive_hls(video_path, output_dir):
        """
        生成自适应 HLS（多码率）
        这是更高级的功能，支持不同设备的自动选择
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # 为不同分辨率创建变体
        variants = []
        
        for preset_name, preset_config in VideoProcessor.PRESETS.items():
            preset_output = os.path.join(output_dir, preset_name)
            os.makedirs(preset_output, exist_ok=True)
            
            resolution = preset_config['resolution'].split('x')
            
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vf', f"scale={preset_config['resolution']}:force_original_aspect_ratio=decrease",
                '-c:v', 'libx264',
                '-crf', '23',
                '-b:v', preset_config['bitrate'],
                '-c:a', 'aac',
                '-b:a', '128k',
                '-f', 'hls',
                '-hls_time', str(VideoProcessor.SEGMENT_DURATION),
                '-hls_list_size', '0',
                '-hls_segment_filename', os.path.join(preset_output, 'segment_%03d.ts'),
                os.path.join(preset_output, 'index.m3u8')
            ]
            
            subprocess.run(cmd, capture_output=True, timeout=3600)
            
            variants.append({
                'name': preset_name,
                'bandwidth': preset_config['bitrate'],
                'resolution': preset_config['resolution'],
                'path': f'{preset_name}/index.m3u8'
            })
        
        # 创建主 m3u8 文件
        master_m3u8 = '#EXTM3U\n#EXT-X-VERSION:3\n'
        for variant in variants:
            master_m3u8 += f'#EXT-X-STREAM-INF:BANDWIDTH={variant["bandwidth"]},RESOLUTION={variant["resolution"]}\n'
            master_m3u8 += f'{variant["path"]}\n'
        
        master_path = os.path.join(output_dir, 'master.m3u8')
        with open(master_path, 'w') as f:
            f.write(master_m3u8)
        
        return master_path
