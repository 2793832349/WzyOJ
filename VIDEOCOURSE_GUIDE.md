# 录播课（视频课程）系统使用指南

## 概述

录播课（视频课程）系统是一个完全独立的模块，与原有的直播课系统完全分离。

- **直播课**：`/course/:id/live/` - 实时互动课堂（WebRTC）
- **录播课**：`/videocourse/*` - 视频课程系统（异步视频处理）

## 系统架构

### 前端路由

```
/videocourse/              - 录播课列表页面
/videocourse/:id/          - 录播课详情页面
/videocourse/create/       - 创建新录播课
/videocourse/:id/edit/     - 编辑录播课
```

### 页面结构

| 页面 | 文件 | 功能 |
|------|------|------|
| 列表 | `pages/videocourse/index.vue` | 浏览所有录播课、搜索、分页、加入/离开课程 |
| 详情 | `pages/videocourse/_id.vue` | 查看课程详情、播放视频、查看章节和问题 |
| 编辑 | `pages/videocourse/edit.vue` | 创建/编辑课程、管理章节、上传视频 |

### 后端 API

所有请求使用 `/api/course-chapters/` 端点：

```
GET    /api/course-chapters/              - 获取课程列表
POST   /api/course-chapters/              - 创建新课程
GET    /api/course-chapters/{id}/         - 获取课程详情
PUT    /api/course-chapters/{id}/         - 更新课程信息
DELETE /api/course-chapters/{id}/         - 删除课程

POST   /api/course-chapters/{id}/upload-video/      - 上传视频
GET    /api/course-chapters/{id}/video_status/      - 获取视频处理状态
GET    /api/course-chapters/{id}/video_playlist/    - 获取m3u8播放列表
POST   /api/course-chapters/{id}/reprocess_video/   - 重新处理视频
```

## 核心功能

### 1. 视频上传和处理

```python
# 支持的格式
MP4, AVI, MOV, WMV, FLV 等

# 处理流程
1. 用户上传 MP4 视频
2. 系统使用 FFmpeg 转换为 HLS (m3u8 + ts 文件)
3. 异步处理（Celery 任务）
4. 处理完成后学生可以播放
```

### 2. 视频播放

```vue
<!-- VideoPlayer.vue 组件 -->
<VideoPlayer 
  :m3u8Url="chapter.m3u8_playlist"
  :title="chapter.title"
/>
```

支持：
- HLS 直播流和点播
- 适配不同网络带宽
- 自动清晰度切换
- 缓存和离线播放

### 3. 课程管理

教师可以：
- 创建新课程
- 添加多个章节
- 为每个章节上传视频
- 编辑课程信息
- 删除课程

学生可以：
- 浏览所有课程
- 加入/离开课程
- 查看课程章节
- 播放课程视频
- 查看相关问题

## 使用示例

### 创建录播课

1. 访问 `/videocourse/create/`
2. 填写课程基本信息：
   - 课程名称
   - 课程描述
   - 隐藏状态

3. 添加章节：
   - 点击 "添加章节" 按钮
   - 输入章节标题和描述
   - 选择视频文件上传

4. 保存课程

### 学生观看录播课

1. 访问 `/videocourse/`，浏览所有课程
2. 点击课程卡片查看详情
3. 点击 "加入课程" 按钮
4. 在课程详情页选择章节，点击视频播放
5. 查看章节中的相关问题

## 数据库模型

### CourseChapter 模型扩展

新增字段用于视频处理：

```python
class CourseChapter(models.Model):
    # 原有字段
    title = CharField(max_length=255)
    description = TextField()
    order = IntegerField()
    course = ForeignKey(Course)
    
    # 新增视频字段
    video_status = CharField(
        max_length=20,
        choices=[
            ('pending', '待处理'),
            ('processing', '处理中'),
            ('completed', '已完成'),
            ('failed', '处理失败'),
        ]
    )
    m3u8_playlist = TextField(blank=True)  # HLS 播放列表
    duration = IntegerField(null=True)      # 视频时长（秒）
    resolution = CharField(max_length=10, blank=True)  # 分辨率
    bitrate = CharField(max_length=20, blank=True)     # 比特率
    error_message = TextField(blank=True)  # 错误信息
```

## 视频处理流程

### 后端处理（FFmpeg）

```
输入文件 (MP4)
    ↓
VideoProcessor.process()
    ↓
FFmpeg 转码为 HLS
    ├── 生成 m3u8 索引文件
    └── 生成 .ts 分段文件
    ↓
保存处理信息 (时长、分辨率等)
    ↓
更新数据库 (video_status = 'completed')
```

### 异步任务（Celery）

```python
@shared_task
def process_chapter_video(chapter_id):
    # 获取章节
    # 调用 VideoProcessor.process()
    # 更新数据库状态
    # 重试机制（最多 3 次）
```

### 监控处理状态

```javascript
// 前端获取处理状态
async function checkVideoStatus(chapterId) {
  const response = await axios.get(
    `/api/course-chapters/${chapterId}/video_status/`
  )
  
  return {
    status: response.video_status,    // pending/processing/completed/failed
    m3u8: response.m3u8_playlist,     // 播放列表 URL
    duration: response.duration,       // 视频时长
    resolution: response.resolution,   // 分辨率
    error: response.error_message      // 错误信息
  }
}
```

## 文件存储

### 目录结构

```
judge_data/
├── submission/
├── test_data/
└── videos/
    ├── chapter_<id>/
    │   ├── master.m3u8        # HLS 主播放列表
    │   ├── playlist.m3u8       # 分段播放列表
    │   ├── segment_0.ts        # 视频分段
    │   ├── segment_1.ts
    │   └── ...
    └── chapter_<id>/
        └── ...
```

## 配置文件

### Django 设置（settings.py）

```python
# Celery 配置
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# 视频处理配置
VIDEO_PROCESS_ROOT = os.path.join(BASE_DIR, 'judge_data/videos')
VIDEO_SEGMENT_DURATION = 10  # 秒
VIDEO_BITRATES = ['2000k', '1000k', '500k']  # 多码率适配

# FFmpeg 路径
FFMPEG_PATH = '/usr/bin/ffmpeg'
FFPROBE_PATH = '/usr/bin/ffprobe'
```

## 常见问题

### Q: 如何修改直播课功能？

A: 直播课位于 `/course/:id/live/` 路由，对应 `pages/course/live.vue` 文件。录播课系统完全独立，不会影响直播课。

### Q: 视频处理失败怎么办？

A: 
1. 检查视频文件格式是否支持
2. 检查服务器磁盘空间是否充足
3. 查看错误信息：`CourseChapter.error_message`
4. 点击 "重新处理" 按钮重试

### Q: 如何调整视频码率？

A: 编辑 `settings.py` 中的 `VIDEO_BITRATES` 配置

```python
VIDEO_BITRATES = [
    '2000k',  # 高质量
    '1000k',  # 中等
    '500k',   # 低质量
]
```

### Q: 支持直播转录播吗？

A: 当前版本需要手动上传视频。可以先通过 ffmpeg 转换，再上传：

```bash
# 例如，将直播录制转换为适配格式
ffmpeg -i live_recording.mkv -c:v h264 -crf 23 video.mp4
```

## 安全考虑

### 访问控制

- 课程列表：需要登录
- 非公开课程：仅教师和已加入的学生可见
- 编辑课程：仅教师（`permission: 'class'`）

### 文件上传

- 最大 5GB
- 支持的格式：MP4、AVI、MOV 等
- 病毒扫描：可扩展（需配置）
- 文件隔离：每个章节独立目录

## 部署检查清单

- [ ] FFmpeg 已安装：`ffmpeg -version`
- [ ] FFprobe 已安装：`ffprobe -version`
- [ ] Celery 服务已启动
- [ ] Redis 服务已启动
- [ ] 视频存储目录有写权限
- [ ] 数据库迁移已执行：`python manage.py migrate`
- [ ] 静态文件已收集：`python manage.py collectstatic`
- [ ] 前端路由已配置
- [ ] 环境变量已设置

## 监控和维护

### 查看 Celery 任务状态

```bash
# 启动 Celery 监控工具
celery -A oj_backend inspect active

# 查看任务统计
celery -A oj_backend inspect stats

# 查看待处理任务
celery -A oj_backend inspect reserved
```

### 检查视频处理日志

```python
# 在 Django shell 中查看
python manage.py shell

from oj_course.models import CourseChapter
ch = CourseChapter.objects.get(id=1)
print(ch.video_status)
print(ch.error_message)
```

## 进阶配置

### 添加水印

在 `video_processor.py` 中的 `_convert_to_hls()` 方法修改 FFmpeg 命令：

```python
cmd = [
    'ffmpeg', '-i', input_path,
    '-vf', "drawtext=text='Your Watermark':fontsize=30:fontcolor=white",
    # ... 其他参数
]
```

### 转码参数优化

```python
# 自定义转码配置
VIDEO_ENCODE_PARAMS = {
    'codec': 'h264',      # 编码器
    'preset': 'medium',   # fast/medium/slow - 权衡速度和质量
    'crf': 23,            # 质量 (0-51, 越小越好)
    'maxrate': '5000k',   # 最大比特率
    'bufsize': '10000k',  # 缓冲区大小
}
```

## 技术支持

如有问题，请参考以下文件：

- [完整 API 文档](./VIDEOCOURSE_API.md)
- [部署指南](./VIDEOCOURSE_DEPLOYMENT.md)
- [技术架构文档](./VIDEOCOURSE_TECHNICAL.md)
- [快速开始指南](./VIDEOCOURSE_QUICKSTART.md)
