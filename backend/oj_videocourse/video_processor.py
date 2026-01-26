"""
独立的录播课视频处理器
使用 FFmpeg 转码视频
"""

import os
import json
import subprocess
import logging
from django.conf import settings
from pathlib import Path

logger = logging.getLogger(__name__)


class VideoCourseVideoProcessor:
    """视频课程视频处理器 - 转码为 HLS 格式"""
    
    def __init__(self):
        self.ffmpeg_path = getattr(settings, 'FFMPEG_PATH', '/usr/bin/ffmpeg')
        self.ffprobe_path = getattr(settings, 'FFPROBE_PATH', '/usr/bin/ffprobe')
        self.segment_duration = getattr(settings, 'VIDEO_SEGMENT_DURATION', 10)
        self.output_root = getattr(
            settings,
            'VIDEOCOURSE_OUTPUT_ROOT',
            os.path.join(settings.BASE_DIR, 'judge_data/videocourse_output')
        )
    
    def process(self, input_file, chapter_id):
        """
        处理视频文件
        
        Args:
            input_file: 输入视频文件路径
            chapter_id: 章节 ID
        
        Returns:
            dict: 处理信息（m3u8_url, duration, resolution, bitrate）
        """
        # 创建输出目录
        output_dir = self._create_output_directory(chapter_id)
        
        # 获取视频信息
        video_info = self._get_video_info(input_file)
        
        # 转码为 HLS
        self._convert_to_hls(input_file, output_dir)
        
        # 返回处理信息
        m3u8_url = f'/media/videocourse_output/chapter_{chapter_id}/master.m3u8'
        
        return {
            'm3u8_url': m3u8_url,
            'duration': video_info.get('duration', 0),
            'resolution': video_info.get('resolution', ''),
            'bitrate': video_info.get('bitrate', ''),
        }
    
    def _create_output_directory(self, chapter_id):
        """创建输出目录"""
        output_dir = os.path.join(self.output_root, f'chapter_{chapter_id}')
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        return output_dir
    
    def _get_video_info(self, input_file):
        """获取视频信息"""
        try:
            cmd = [
                self.ffprobe_path,
                '-v', 'error',
                '-show_format',
                '-show_streams',
                '-of', 'json',
                input_file
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return {}
            
            data = json.loads(result.stdout)
            
            # 提取信息
            duration = 0
            resolution = ''
            bitrate = ''
            
            if 'format' in data:
                duration = int(float(data['format'].get('duration', 0)))
                bitrate = data['format'].get('bit_rate', '')
            
            if 'streams' in data:
                for stream in data['streams']:
                    if stream.get('codec_type') == 'video':
                        width = stream.get('width', 0)
                        height = stream.get('height', 0)
                        if width and height:
                            resolution = f"{width}x{height}"
                        break
            
            return {
                'duration': duration,
                'resolution': resolution,
                'bitrate': bitrate,
            }
        except Exception as e:
            logger.error(f"获取视频信息失败: {str(e)}")
            return {}
    
    def _convert_to_hls(self, input_file, output_dir):
        """转码为 HLS 格式"""
        m3u8_file = os.path.join(output_dir, 'master.m3u8')
        segment_file = os.path.join(output_dir, 'segment_%03d.ts')
        
        cmd = [
            self.ffmpeg_path,
            '-i', input_file,
            '-c:v', 'h264',
            '-c:a', 'aac',
            '-hls_time', str(self.segment_duration),
            '-hls_playlist_type', 'vod',
            '-hls_segment_filename', segment_file,
            m3u8_file
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600  # 1小时超时
        )
        
        if result.returncode != 0:
            error_msg = result.stderr if result.stderr else 'FFmpeg 转码失败'
            raise Exception(error_msg)
        
        logger.info(f"视频转码成功: {output_dir}")
