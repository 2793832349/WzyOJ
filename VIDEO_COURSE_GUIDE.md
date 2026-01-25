# 视频课程模块 - 使用指南

## 功能概述

视频课程模块支持以下功能：

1. **MP4 视频上传** - 支持多种格式（MP4、AVI、MOV、MKV、FLV 等）
2. **自动转换为 HLS (m3u8)** - 自动将上传的视频转换为 HLS 流媒体格式
3. **实时进度追踪** - 异步处理视频，支持前端实时检查处理状态
4. **自适应比特率** - 支持多码率自适应播放
5. **响应式播放器** - 支持各种设备（PC、平板、手机）

## 系统架构

### 后端组件

#### 1. 数据模型 (models.py)
- **VideoProcessingStatus** - 视频处理状态枚举
  - `pending`: 待处理
  - `processing`: 处理中
  - `completed`: 已完成
  - `failed`: 处理失败

- **CourseChapter** 扩展字段
  - `video_status`: 视频处理状态
  - `m3u8_playlist`: m3u8 播放列表内容
  - `m3u8_file`: m3u8 文件存储
  - `video_segments_dir`: 视频分片目录路径
  - `duration`: 视频时长（秒）
  - `bitrate`: 比特率
  - `resolution`: 分辨率
  - `error_message`: 错误信息

#### 2. 视频处理器 (video_processor.py)
负责 MP4 到 HLS 的转换：
```python
from oj_course.video_processor import VideoProcessor

processor = VideoProcessor(chapter)
processor.process()  # 同步处理
```

**主要方法：**
- `process()` - 执行完整的视频处理流程
- `_get_video_info()` - 获取视频信息（时长、分辨率等）
- `_create_output_directory()` - 创建输出目录
- `_convert_to_hls()` - 使用 FFmpeg 转换视频
- `_save_processing_info()` - 保存处理结果

#### 3. 异步任务 (tasks.py)
使用 Celery 进行异步处理：
```python
from oj_course.tasks import process_chapter_video

# 异步处理视频
process_chapter_video.delay(chapter_id)
```

#### 4. API 视图 (views.py)

**CourseChapterViewSet 新增端点：**

##### 上传视频
```
POST /api/course-chapters/{id}/upload-video/
Content-Type: multipart/form-data

file: <video_file>
```

**响应 (202 Accepted):**
```json
{
  "id": 1,
  "course": 1,
  "title": "第一课",
  "video_status": "pending",
  "duration": 0,
  "resolution": "",
  "m3u8_url": null,
  "segments_url": null
}
```

##### 检查视频处理状态
```
GET /api/course-chapters/{id}/video_status/
```

**响应:**
```json
{
  "id": 1,
  "video_status": "processing",
  "duration": 3600,
  "resolution": "1280x720",
  "error_message": null
}
```

##### 获取 m3u8 播放列表
```
GET /api/course-chapters/{id}/video_playlist/
```

**响应:**
```json
{
  "id": 1,
  "title": "第一课",
  "duration": 3600,
  "resolution": "1280x720",
  "bitrate": "2500k",
  "m3u8_url": "http://example.com/media/course_videos_hls/1/1/index.m3u8",
  "m3u8_content": "#EXTM3U\n#EXT-X-VERSION:3\n..."
}
```

##### 重新处理视频
```
POST /api/course-chapters/{id}/reprocess_video/
```

**响应 (202 Accepted):**
```json
{
  "id": 1,
  "video_status": "pending",
  "duration": 0,
  "resolution": "",
  "m3u8_url": null
}
```

### 前端组件

#### 1. VideoPlayer.vue
负责视频播放：
```vue
<VideoPlayer 
  :chapterId="1" 
  apiBaseUrl="/api/course-chapters"
/>
```

**Props:**
- `chapterId` (Number, required) - 课程章节 ID
- `apiBaseUrl` (String, default: '/api/course-chapters') - API 基础 URL

**事件:**
- `play` - 视频播放时触发
- `pause` - 视频暂停时触发
- `timeupdate` - 播放时间更新时触发

**功能：**
- 自动检查视频处理状态
- 轮询检查（5 秒间隔）
- 加载完成后播放 m3u8 视频
- 显示视频信息（时长、分辨率、码率）

#### 2. VideoCourseManager.vue
负责视频上传和课程管理：
```vue
<VideoCourseManager 
  :courseId="1" 
  apiBaseUrl="/api/course-chapters"
  uploadUrl="/api/course-chapters"
/>
```

**Props:**
- `courseId` (Number, required) - 课程 ID
- `apiBaseUrl` (String) - API 基础 URL
- `uploadUrl` (String) - 上传 API URL

**功能：**
- 拖拽或点击上传视频
- 显示上传进度
- 管理课程章节
- 查看视频处理状态
- 重新处理视频
- 删除章节

## 安装和配置

### 后端配置

#### 1. 安装依赖

```bash
# FFmpeg 转换依赖
pip install opencv-python  # 用于视频分析
```

#### 2. 系统依赖
需要安装 FFmpeg：

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
从 https://ffmpeg.org/download.html 下载或使用包管理器

#### 3. Django 设置 (settings.py)

```python
# 添加到 INSTALLED_APPS
INSTALLED_APPS = [
    ...
    'oj_course',
    ...
]

# 媒体文件配置
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# 添加 Celery 配置
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Shanghai'

# 视频处理配置
VIDEO_SEGMENT_DURATION = 10  # 秒
VIDEO_MAX_SIZE = 5 * 1024 * 1024 * 1024  # 5GB
```

#### 4. URL 配置 (urls.py)

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... 其他 URL
]

# 开发环境下提供媒体文件
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

#### 5. 运行迁移

```bash
python manage.py migrate oj_course
```

#### 6. 启动 Celery Worker

```bash
# 启动 Celery worker
celery -A oj_backend worker -l info

# 或使用 Celery beat 进行定时任务
celery -A oj_backend worker -B -l info
```

### 前端配置

#### 1. 安装依赖

```bash
npm install axios
```

#### 2. 注册组件

```vue
<script>
import VideoPlayer from '@/components/VideoPlayer.vue'
import VideoCourseManager from '@/components/VideoCourseManager.vue'

export default {
  components: {
    VideoPlayer,
    VideoCourseManager
  }
}
</script>
```

#### 3. 使用示例

```vue
<template>
  <div>
    <!-- 视频课程管理（教师）-->
    <VideoCourseManager v-if="isTeacher" :courseId="courseId" />
    
    <!-- 视频播放器（学生）-->
    <VideoPlayer v-if="isStudent" :chapterId="chapterId" />
  </div>
</template>
```

## 工作流程

### 上传和处理流程

```
1. 教师上传 MP4 文件
   ↓
2. 后端保存视频文件，设置状态为 "pending"
   ↓
3. 触发异步任务 (Celery)
   ↓
4. VideoProcessor 处理视频：
   - 读取视频信息
   - 创建输出目录
   - 使用 FFmpeg 转换为 HLS (m3u8 + ts 分片)
   ↓
5. 保存处理结果，更新状态为 "completed"
   ↓
6. 前端检测到完成，加载 m3u8 播放列表
   ↓
7. 学生在线观看视频流
```

### 前端轮询流程

```
VideoPlayer 初始化
   ↓
调用 /api/course-chapters/{id}/video_status/
   ↓
如果状态是 "processing" 或 "pending"：
   ↓
每 5 秒重新检查一次
   ↓
状态变为 "completed" 后：
   ↓
调用 /api/course-chapters/{id}/video_playlist/
   ↓
获取 m3u8 URL 和内容
   ↓
加载视频播放器
```

## FFmpeg 转换详解

### 转换命令

```bash
ffmpeg \
  -i input.mp4 \                    # 输入文件
  -c:v libx264 \                    # 视频编码器
  -crf 23 \                         # 视频质量 (0-51, 低=好)
  -c:a aac \                        # 音频编码器
  -b:a 128k \                       # 音频码率
  -f hls \                          # 输出格式
  -hls_time 10 \                    # 分片时长
  -hls_list_size 0 \                # 播放列表大小
  -hls_segment_filename output/%03d.ts \  # 分片文件名
  output/index.m3u8                 # 输出 m3u8 文件
```

### 生成的文件结构

```
course_videos_hls/
├── {course_id}/
│   └── {chapter_id}/
│       ├── index.m3u8              # 播放列表
│       ├── segment_000.ts          # 视频分片
│       ├── segment_001.ts
│       ├── segment_002.ts
│       └── ...
```

## 性能优化

### 1. 分片大小优化
- 默认 10 秒一个分片
- 可根据需求调整 `SEGMENT_DURATION`

### 2. 码率选择
- 低质量：800k (360p)
- 中等质量：1500k (480p)
- 高质量：3000k (720p)

### 3. 并发处理
- 使用 Celery 异步处理
- 支持多个 worker 并发转换
- Redis 用于任务队列和结果存储

## 错误处理

### 常见错误

#### 1. FFmpeg 未找到
```
Error: 'ffmpeg' not found
解决: 确保系统已安装 FFmpeg
```

#### 2. 磁盘空间不足
```
Error: No space left on device
解决: 清理磁盘或增加存储空间
```

#### 3. 权限问题
```
Error: Permission denied
解决: 检查媒体目录权限: chmod 755 media/
```

#### 4. Celery 连接错误
```
Error: Connection refused
解决: 确保 Redis 服务正在运行
```

## 监控和调试

### 查看 Celery 任务状态
```python
from oj_course.tasks import process_chapter_video

# 获取任务状态
result = process_chapter_video.delay(chapter_id)
print(result.status)  # PENDING, PROGRESS, SUCCESS, FAILURE
```

### 日志查看
```bash
# 查看处理日志
tail -f logs/video_processing.log
```

### 数据库查询
```python
from oj_course.models import CourseChapter, VideoProcessingStatus

# 查看处理失败的视频
failed_chapters = CourseChapter.objects.filter(
    video_status=VideoProcessingStatus.FAILED
)

for chapter in failed_chapters:
    print(f"Chapter {chapter.id}: {chapter.error_message}")
```

## 扩展功能建议

1. **缩略图生成** - 自动生成视频缩略图
2. **字幕支持** - 支持上传和自动生成字幕
3. **视频统计** - 记录学生观看进度和时长
4. **DRM 保护** - 添加数字版权管理
5. **CDN 集成** - 集成 CDN 加速分发
6. **批量转换** - 支持批量视频处理
7. **直播功能** - 支持直播教学

## 故障排查

### 视频上传后一直显示"处理中"
1. 检查 Celery worker 是否运行
2. 查看 worker 日志中的错误信息
3. 检查 Redis 连接状态
4. 查看数据库中的 error_message 字段

### m3u8 播放不了
1. 确认视频处理状态为 "completed"
2. 检查分片文件是否存在
3. 验证 m3u8 文件内容
4. 检查浏览器控制台错误信息

### 转换速度很慢
1. 降低视频质量 (CRF 参数调高)
2. 增加 Celery worker 数量
3. 检查系统 CPU 和磁盘 I/O
4. 考虑使用更快的硬件

## 许可证和支持

视频课程模块遵循项目主许可证。
如有问题，请提交 issue 或联系开发团队。
