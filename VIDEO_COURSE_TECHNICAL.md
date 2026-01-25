# 视频课程模块 - 技术实现细节

## 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    用户 (学生/教师)                           │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼────┐      ┌────▼────┐     ┌───▼────┐
   │ Web UI  │      │ Mobile  │     │ API    │
   │(Vue.js) │      │(React)  │     │Client  │
   └────┬────┘      └────┬────┘     └───┬────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                    ┌────▼─────────┐
                    │  Django API  │
                    │ (REST)       │
                    └────┬─────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼────┐      ┌────▼────┐     ┌───▼────┐
   │ Database │     │  Redis  │     │Celery  │
   │(Postgre)│     │ (Queue) │     │Worker  │
   └─────────┘      └────┬────┘     └───┬────┘
                         │                │
                         │           ┌────▼────┐
                         │           │ FFmpeg  │
                         │           │(Video)  │
                         │           └─────────┘
                         │
                    ┌────▼──────────┐
                    │ Media Storage │
                    │(m3u8/ts files)│
                    └────────────────┘
```

## 数据流图

### 视频上传流程

```
用户上传
   │
   ▼
前端验证 (文件类型、大小)
   │
   ▼
POST /api/course-chapters/{id}/upload-video/
   │
   ▼
后端验证 (权限、文件)
   │
   ▼
保存视频文件 (media/course_videos/{date}/)
   │
   ▼
设置状态为 "pending"
   │
   ▼
触发 Celery 任务
   │
   ▼
返回 202 Accepted
   │
   ▼
前端接收响应
```

### 视频处理流程

```
Celery Worker 接收任务
   │
   ▼
VideoProcessor.process()
   │
   ├─ 设置状态为 "processing"
   │
   ├─ 获取视频信息 (ffprobe)
   │  ├─ 时长
   │  ├─ 分辨率
   │  └─ 码率
   │
   ├─ 创建输出目录
   │
   ├─ 转换视频 (ffmpeg)
   │  ├─ 输入: MP4
   │  ├─ 视频编码: H.264
   │  ├─ 音频编码: AAC
   │  ├─ 分片时长: 10 秒
   │  └─ 输出: m3u8 + ts files
   │
   ├─ 生成 m3u8 文件
   │  ```
   │  #EXTM3U
   │  #EXT-X-VERSION:3
   │  #EXT-X-TARGETDURATION:11
   │  #EXT-X-MEDIA-SEQUENCE:0
   │  #EXTINF:10.0,
   │  segment_000.ts
   │  #EXTINF:10.0,
   │  segment_001.ts
   │  ...
   │  #EXT-X-ENDLIST
   │  ```
   │
   ├─ 保存处理信息到数据库
   │  ├─ 视频时长
   │  ├─ 分辨率
   │  └─ m3u8 路径
   │
   ├─ 设置状态为 "completed"
   │
   └─ 任务完成

前端检测到完成
   │
   ▼
GET /api/course-chapters/{id}/video_playlist/
   │
   ▼
后端返回 m3u8 URL
   │
   ▼
前端加载 m3u8 播放器
   │
   ▼
用户观看视频
```

## 数据库模型关系

```
Course (课程)
├── id: INT PRIMARY
├── title: VARCHAR(100)
├── description: TEXT
├── teacher: FK → User
├── is_hidden: BOOL
├── created_at: DATETIME
└── updated_at: DATETIME
    │
    └─► CourseChapter (课程章节)
        ├── id: INT PRIMARY
        ├── course: FK → Course
        ├── title: VARCHAR(100)
        ├── description: TEXT
        ├── order: INT
        ├── video: FILE (原始视频)
        ├── video_status: ENUM (pending/processing/completed/failed)
        ├── m3u8_playlist: TEXT (m3u8 内容)
        ├── m3u8_file: FILE (m3u8 文件)
        ├── video_segments_dir: VARCHAR(500) (输出目录)
        ├── duration: INT (时长,秒)
        ├── bitrate: VARCHAR(50)
        ├── resolution: VARCHAR(50)
        ├── error_message: TEXT
        ├── created_at: DATETIME
        ├── updated_at: DATETIME
        │
        └─► ChapterProblem (章节练习题)
            ├── id: INT PRIMARY
            ├── chapter: FK → CourseChapter
            ├── problem: FK → Problem
            └── order: INT
```

## FFmpeg 命令分析

### 基础转换命令

```bash
ffmpeg \
  -i input.mp4 \                      # 输入文件
  -c:v libx264 \                      # 视频编码器 (H.264)
  -crf 23 \                           # 质量 (0-51, 低=好, 默认28)
  -c:a aac \                          # 音频编码器
  -b:a 128k \                         # 音频码率
  -f hls \                            # 输出格式 (HLS)
  -hls_time 10 \                      # 分片时长 (秒)
  -hls_list_size 0 \                  # 播放列表大小 (0=不限)
  -hls_segment_filename 'segment_%03d.ts' \  # 分片文件名
  output/index.m3u8                   # 输出文件
```

### 参数说明

| 参数 | 说明 | 取值范围/建议 |
|------|------|-------------|
| -crf | 视频质量 | 0-51, 推荐 18-28 |
| -b:v | 视频码率 | 800k-5000k |
| -b:a | 音频码率 | 128k-256k |
| -hls_time | 分片时长 | 5-15 秒 |
| -preset | 转换速度 | ultrafast/superfast/veryfast/faster/fast/medium/slow |

### 性能优化

```bash
# 快速转换（质量降低）
ffmpeg -i input.mp4 -c:v libx264 -preset faster -crf 28 ... output.m3u8

# 高质量转换（需要更多时间）
ffmpeg -i input.mp4 -c:v libx264 -preset slow -crf 18 ... output.m3u8

# 使用硬件加速（如果支持）
ffmpeg -i input.mp4 -c:v h264_nvenc ... output.m3u8  # NVIDIA GPU
ffmpeg -i input.mp4 -c:v h264_videotoolbox ... output.m3u8  # macOS
ffmpeg -i input.mp4 -c:v h264_qsv ... output.m3u8  # Intel Quick Sync
```

## API 响应流程

### 上传视频响应

```
请求: POST /api/course-chapters/1/upload-video/
响应 (202 Accepted):
{
  "id": 1,
  "video_status": "pending",      # 立即返回 pending
  "duration": 0,                  # 暂时为 0
  "resolution": "",               # 暂时为空
  "m3u8_url": null                # 暂时为空
}

Celery 异步处理:
→ VideoProcessor.process()
→ 调用 ffmpeg
→ 生成 m3u8 和 ts 分片
→ 更新数据库字段
→ 设置 video_status = "completed"
```

### 状态查询响应

```
请求: GET /api/course-chapters/1/video_status/

响应 1 (处理中):
{
  "video_status": "processing",
  "duration": 0,
  "resolution": "",
  "error_message": null
}

响应 2 (处理完成):
{
  "video_status": "completed",
  "duration": 3600,               # 已更新
  "resolution": "1280x720",       # 已更新
  "error_message": null
}

响应 3 (处理失败):
{
  "video_status": "failed",
  "duration": 0,
  "resolution": "",
  "error_message": "FFmpeg conversion failed: codec not found"
}
```

### 播放列表响应

```
请求: GET /api/course-chapters/1/video_playlist/

响应:
{
  "id": 1,
  "title": "第一章",
  "duration": 3600,
  "resolution": "1280x720",
  "bitrate": "2500k",
  "m3u8_url": "http://localhost:8000/media/course_videos_hls/1/1/index.m3u8",
  "m3u8_content": "#EXTM3U\n#EXT-X-VERSION:3\n...#EXTINF:10.0,\nsegment_000.ts\n..."
}

前端使用 m3u8_url:
<video controls>
  <source src="http://localhost:8000/media/course_videos_hls/1/1/index.m3u8" 
          type="application/x-mpegURL" />
</video>
```

## 前端组件状态机

### VideoPlayer 状态转换

```
[初始化]
   │
   ▼
[检查状态] ──► 错误 ──► [错误状态]
   │              │
   ├─ pending      │
   │   │           │
   │   ▼           │
   │ [轮询中]      │
   │   │           │
   │   └─ 5秒后 ───┘
   │
   ├─ processing
   │   │
   │   ▼
   │ [轮询中]
   │   │
   │   └─ 5秒后 ───┐
   │               │
   ├─ completed    ▼
   │   │       [继续轮询]
   │   │
   │   ▼
   │ [加载 m3u8] ──► [播放器初始化] ──► [准备就绪]
   │
   └─ failed ──► [显示错误] ──► [提供重试按钮]
```

### VideoCourseManager 生命周期

```
mounted
   │
   ▼
[加载章节列表]
   │
   ├─ 成功 ▼
   │    [渲染章节卡片]
   │    │
   │    ├─ 教师: 显示上传表单和操作按钮
   │    │
   │    └─ 学生: 仅显示视频信息和播放器
   │
   └─ 失败 ▼
        [显示错误消息]

用户操作
   │
   ├─ 上传视频
   │  └─ POST upload-video ──► 更新列表
   │
   ├─ 编辑章节
   │  └─ 打开编辑对话框
   │
   ├─ 删除章节
   │  └─ 确认 ──► DELETE ──► 更新列表
   │
   └─ 重新处理
      └─ POST reprocess-video ──► 更新列表

beforeUnmount
   │
   └─ [清理资源]
```

## 错误处理流程

### 后端错误处理

```
try:
    VideoProcessor.process()
    ✅ 成功 → status = "completed"
catch Exception as e:
    ❌ 失败
    ├─ 记录日志
    ├─ 保存错误信息
    ├─ 设置 status = "failed"
    └─ Celery 重试机制
       ├─ 第 1 次失败: 60 秒后重试
       ├─ 第 2 次失败: 300 秒后重试
       ├─ 第 3 次失败: 600 秒后重试
       └─ 第 3 次后: 放弃
```

### 前端错误处理

```
VideoPlayer 初始化
   │
   ▼
loadVideoPlaylist()
   │
   ├─ 成功 ▼
   │    [加载播放器]
   │
   └─ 失败 ▼
        error = "加载失败: xxx"
        │
        ▼
        [显示错误消息和重试按钮]
        │
        用户点击重试
        │
        ▼
        [重新调用 loadVideoPlaylist()]
```

## 性能考虑

### 1. 视频转换优化

```python
# 分辨率自适应
profiles = {
    '720p': {'resolution': '1280x720', 'bitrate': '2500k'},
    '480p': {'resolution': '854x480', 'bitrate': '1500k'},
    '360p': {'resolution': '640x360', 'bitrate': '800k'}
}

# 用户网络速度检查后自动选择
if user.connection == 'slow':
    quality = '360p'
elif user.connection == 'medium':
    quality = '480p'
else:
    quality = '720p'
```

### 2. 缓存策略

```
媒体文件缓存:
└─ 浏览器缓存: 30 天
└─ CDN 缓存: 7 天
└─ 服务器缓存: 无

m3u8 文件缓存:
└─ 浏览器缓存: 1 小时（不缓存）
└─ CDN 缓存: 不缓存
└─ 服务器缓存: 实时查询
```

### 3. 并发处理

```
Celery Worker 并发数 = CPU核数 - 1

例如:
4 核 CPU: 3 个 worker
8 核 CPU: 7 个 worker
16 核 CPU: 15 个 worker

每个 worker 可处理:
─ 1 个转换 + N 个查询操作
```

## 存储空间计算

```
单个视频存储占用:
= 原始文件大小 × (1 + 转换率)
= 原始文件大小 × 1.2

例如:
- 1GB MP4 → 约 1.2GB HLS

年度存储需求:
= 平均视频大小 × 日均上传数 × 365
= 500MB × 10 × 365
= 1825GB ≈ 2TB
```

## 部署最佳实践

### 1. 任务队列配置

```python
# settings.py
CELERY_TASK_TIME_LIMIT = 3600 * 2          # 2 小时硬限制
CELERY_TASK_SOFT_TIME_LIMIT = 3600 * 1.5   # 1.5 小时软限制
CELERY_TASK_MAX_RETRIES = 3                # 最多重试 3 次
CELERY_TASK_ACKS_LATE = True               # 任务完成后确认
CELERY_WORKER_PREFETCH_MULTIPLIER = 1      # 每次只预取 1 个任务
```

### 2. 日志配置

```python
# 任务级别日志
CELERY_TASK_LOG_FORMAT = '[%(levelname)s/%(processName)s] %(message)s'
CELERY_TASK_LOG_COLOR = True

# 文件日志轮转
'maxBytes': 1024 * 1024 * 100,  # 100MB
'backupCount': 10,               # 保留 10 个备份
```

### 3. 监控指标

```
关键指标:
├─ 任务队列长度
├─ worker 活跃数
├─ 平均转换时间
├─ 错误率
├─ 磁盘空间使用
├─ 内存使用
└─ CPU 使用率

告警阈值:
├─ 队列长度 > 100
├─ 错误率 > 5%
├─ 磁盘使用 > 80%
├─ 内存使用 > 85%
└─ CPU 使用 > 95% (持续 5 分钟)
```

## 安全性考虑

### 1. 文件上传安全

```python
# 文件类型白名单
ALLOWED_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']

# 文件大小限制
MAX_UPLOAD_SIZE = 5 * 1024 * 1024 * 1024  # 5GB

# 文件内容验证
def validate_video_file(file):
    # 使用 ffprobe 验证文件
    # 检查是否为有效视频文件
    pass

# 防止目录遍历
safe_filename = werkzeug.utils.secure_filename(filename)
```

### 2. 权限控制

```python
# 上传权限
- 仅教师 (is_staff or has_class_permission)

# 删除权限
- 创建者或管理员

# 查看权限
- 已加入课程的学生
- 课程创建者
- 管理员
```

### 3. API 安全

```python
# Token 认证
permission_classes = [IsAuthenticated]

# Rate limiting (可选)
throttle_classes = [UserRateThrottle]
throttle_rates = {'user': '1000/hour'}

# CORS 配置
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'https://example.com'
]
```

---

**文档版本**: 1.0
**最后更新**: 2026年1月25日
**维护者**: 开发团队

详细的实现细节已在此文档中概述，可根据实际需求进行调整和优化。
