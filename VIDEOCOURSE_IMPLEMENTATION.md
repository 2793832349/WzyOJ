# 录播课系统完整实现指南

## 项目完成状态

✅ **已完成**：
- 后端视频处理系统（FFmpeg + Celery）
- 前端路由配置（4 个新路由）
- 前端页面实现：
  - `/videocourse/` - 课程列表页面
  - `/videocourse/:id/` - 课程详情页面
  - `/videocourse/create/` - 创建课程页面
  - `/videocourse/:id/edit/` - 编辑课程页面
- 数据库模型和迁移
- API 端点（视频上传、状态查询、播放列表）

## 系统结构图

```
直播课系统（原有，保持不变）
├── /course/                    - 课程列表
├── /course/:id/                - 课程详情
├── /course/:id/live/           - 直播课堂 ✓ 保持原样
├── /course/create/             - 创建课程
└── /course/:id/edit/           - 编辑课程

录播课系统（新增，独立）
├── /videocourse/               - 课程列表 ✓ 新增
├── /videocourse/:id/           - 课程详情 ✓ 新增
├── /videocourse/create/        - 创建课程 ✓ 新增
└── /videocourse/:id/edit/      - 编辑课程 ✓ 新增

后端 API（共用）
└── /api/course-chapters/       - 课程和视频数据接口
```

## 前端文件结构

```
frontend-naive/src/
├── pages/
│   ├── course/                 # 直播课页面（保持不变）
│   │   ├── index.vue
│   │   ├── _id.vue
│   │   ├── live.vue            ✓ 重要：不修改
│   │   └── edit.vue
│   │
│   └── videocourse/            # 录播课页面（新增）
│       ├── index.vue           ✓ 课程列表
│       ├── _id.vue             ✓ 课程详情
│       └── edit.vue            ✓ 创建/编辑
│
├── components/
│   ├── VideoPlayer.vue         ✓ 视频播放组件（HLS m3u8）
│   └── VideoCourseManager.vue  ✓ 视频管理组件
│
└── router/
    └── index.js                ✓ 已添加 4 个 videocourse 路由
```

## 后端文件结构

```
backend/oj_course/
├── models.py                   ✓ CourseChapter 扩展 8 个视频字段
├── serializers.py              ✓ 添加视频字段序列化
├── views.py                    ✓ 4 个新 API 端点
├── urls.py                     ✓ 路由配置
├── tasks.py                    ✓ Celery 异步任务
├── video_processor.py          ✓ FFmpeg 视频处理
├── migrations/
│   └── 0002_add_video_processing.py  ✓ 数据库迁移
└── admin.py                    ✓ Django Admin 配置
```

## 快速启动步骤

### 1. 后端准备

```bash
# 1.1 安装系统依赖
# Ubuntu/Debian
sudo apt-get install ffmpeg

# MacOS
brew install ffmpeg

# Windows
# 下载: https://ffmpeg.org/download.html

# 1.2 检查 FFmpeg 安装
ffmpeg -version
ffprobe -version

# 1.3 创建视频存储目录
mkdir -p backend/judge_data/videos

# 1.4 执行数据库迁移
cd backend
python manage.py migrate
python manage.py migrate oj_course

# 1.5 收集静态文件
python manage.py collectstatic --noinput

# 1.6 启动 Celery（在另一个终端）
celery -A oj_backend worker -l info

# 1.7 启动 Redis（如果还没启动）
redis-server

# 1.8 启动 Django 开发服务器
python manage.py runserver 0.0.0.0:8000
```

### 2. 前端准备

```bash
cd frontend-naive

# 2.1 安装依赖
npm install

# 2.2 启动开发服务器
npm run dev

# 访问: http://localhost:5173
```

### 3. 访问应用

- **直播课列表**：http://localhost:5173/course/
- **录播课列表**：http://localhost:5173/videocourse/
- **创建录播课**：http://localhost:5173/videocourse/create/

## 功能测试清单

### 前端测试

- [ ] 导航栏能正确显示 "录播课" 链接
- [ ] 访问 `/videocourse/` 显示课程列表页面
- [ ] 搜索功能可正常工作
- [ ] 分页功能可正常工作
- [ ] 教师可以看到 "新建录播课" 按钮
- [ ] 点击课程卡片进入详情页面
- [ ] 详情页面显示所有章节
- [ ] 点击章节展开/收起
- [ ] VideoPlayer 组件正确加载视频
- [ ] 可以加入/离开课程
- [ ] 教师可以编辑课程
- [ ] 编辑页面可以上传视频

### 后端 API 测试

```bash
# 使用 curl 或 Postman 测试

# 1. 获取课程列表
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/course-chapters/

# 2. 创建课程
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"title":"新课程","description":"描述"}' \
  http://localhost:8000/api/course-chapters/

# 3. 获取课程详情
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/course-chapters/1/

# 4. 上传视频
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -F "video=@video.mp4" \
  http://localhost:8000/api/course-chapters/1/upload-video/

# 5. 查询视频处理状态
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/course-chapters/1/video_status/

# 6. 获取 m3u8 播放列表
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/course-chapters/1/video_playlist/
```

## 页面功能详解

### 录播课列表页面（index.vue）

**路由**：`/videocourse/`

**功能**：
- 显示所有录播课程的网格列表
- 每个课程卡片包含：
  - 课程封面（视频图标）
  - 课程标题
  - 课程描述
  - 学生数量
  - 教师名称
  - 加入/已加入状态按钮

**交互**：
- 搜索课程（按标题）
- 分页浏览
- 点击卡片进入详情页
- 教师可以点击 "新建录播课"
- 可以加入/离开课程

**数据来源**：
```javascript
// GET /api/course-chapters/?search=xxx&page=1&limit=12
```

### 录播课详情页面（_id.vue）

**路由**：`/videocourse/:id/`

**功能**：
- 显示课程完整信息
- 列出所有章节（可展开/收起）
- 展示当前章节的视频播放器
- 列出相关的问题集
- 显示用户学习进度

**交互**：
- 点击章节展开/收起
- 选择章节播放视频
- 查看问题并跳转到答题
- 教师可以编辑/删除课程
- 学生可以加入/离开课程

**数据来源**：
```javascript
// GET /api/course-chapters/{id}/
// 包含所有章节和视频信息
```

**VideoPlayer 组件**：
```vue
<VideoPlayer 
  :m3u8Url="selectedChapter.m3u8_playlist"
  :title="selectedChapter.title"
/>
```

### 录播课编辑页面（edit.vue）

**路由**：
- 创建：`/videocourse/create/`
- 编辑：`/videocourse/:id/edit/`

**功能**：
- 表单编辑课程基本信息
- 章节管理界面
- 视频上传和处理状态显示

**表单字段**：
1. 课程名称 *（必填）
2. 课程描述
3. 隐藏课程（复选框）
4. 章节列表：
   - 章节标题
   - 章节描述
   - 视频文件上传
   - 视频处理状态
   - 删除按钮

**上传和处理流程**：
```
选择 MP4 文件
    ↓
点击 "保存课程"
    ↓
后端接收请求
    ↓
启动 Celery 任务 (process_chapter_video)
    ↓
FFmpeg 转码为 HLS
    ↓
更新数据库状态
    ↓
前端轮询检查状态
    ↓
处理完成，显示 m3u8 播放列表 URL
```

## API 接口文档

### 获取课程列表

```http
GET /api/course-chapters/
Authorization: Bearer <token>

Query Parameters:
  search: string        # 按标题搜索
  page: integer         # 页码（默认 1）
  limit: integer        # 每页数量（默认 12）
  course_id: integer    # 按课程 ID 筛选

Response:
{
  "count": 42,
  "next": "...",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Python 基础",
      "description": "...",
      "order": 1,
      "course": 5,
      "video_status": "completed",
      "m3u8_playlist": "https://...",
      "duration": 3600,
      "resolution": "1920x1080",
      "bitrate": "5000k",
      "error_message": ""
    },
    ...
  ]
}
```

### 获取课程详情

```http
GET /api/course-chapters/{id}/
Authorization: Bearer <token>

Response:
{
  "id": 1,
  "title": "Python 基础",
  "description": "...",
  "chapters": [
    {
      "id": 1,
      "title": "第一章：介绍",
      "description": "...",
      "order": 1,
      "video_status": "completed",
      "m3u8_playlist": "https://...",
      "duration": 3600,
      "resolution": "1920x1080",
      "bitrate": "5000k",
      "problems": [
        {"id": 1, "title": "题目 1"},
        ...
      ]
    },
    ...
  ]
}
```

### 上传视频

```http
POST /api/course-chapters/{id}/upload-video/
Authorization: Bearer <token>
Content-Type: multipart/form-data

Body:
  video: <File>  # 视频文件

Response:
{
  "status": "success",
  "message": "视频上传成功，处理中...",
  "task_id": "celery-task-uuid"
}
```

### 查询视频处理状态

```http
GET /api/course-chapters/{id}/video_status/
Authorization: Bearer <token>

Response:
{
  "id": 1,
  "video_status": "completed|processing|pending|failed",
  "m3u8_playlist": "https://..." or null,
  "duration": 3600,
  "resolution": "1920x1080",
  "bitrate": "5000k",
  "error_message": ""
}
```

### 获取 m3u8 播放列表

```http
GET /api/course-chapters/{id}/video_playlist/
Authorization: Bearer <token>

Response:
{
  "m3u8_url": "https://example.com/videos/chapter_1/master.m3u8"
}
```

### 重新处理视频

```http
POST /api/course-chapters/{id}/reprocess_video/
Authorization: Bearer <token>

Response:
{
  "status": "success",
  "message": "视频重新处理中...",
  "task_id": "celery-task-uuid"
}
```

## 配置说明

### Django Settings（backend/oj_backend/settings.py）

```python
# 应用注册
INSTALLED_APPS = [
    ...
    'oj_course',
    ...
]

# Celery 配置
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_TASK_SERIALIZER = 'json'

# 视频处理配置
VIDEO_PROCESS_ROOT = os.path.join(BASE_DIR, 'judge_data/videos')
VIDEO_SEGMENT_DURATION = 10  # 秒

# FFmpeg 路径
FFMPEG_PATH = '/usr/bin/ffmpeg'
FFPROBE_PATH = '/usr/bin/ffprobe'

# 允许的视频格式
ALLOWED_VIDEO_FORMATS = ['mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv']

# 最大上传文件大小
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024 * 1024  # 5GB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024 * 1024  # 5GB
```

### 前端路由配置（src/router/index.js）

```javascript
// 已添加的路由
{
  path: '/videocourse/',
  name: 'videocourse_list',
  component: () => import('@/pages/videocourse/index.vue'),
  meta: { title: '录播课', requiredLogin: true }
},
{
  path: '/videocourse/:id/',
  name: 'videocourse_detail',
  component: () => import('@/pages/videocourse/_id.vue'),
  meta: { title: '录播课详情', requiredLogin: true }
},
{
  path: '/videocourse/create/',
  name: 'videocourse_create',
  component: () => import('@/pages/videocourse/edit.vue'),
  meta: { title: '创建录播课', requiredLogin: true, permission: 'class' }
},
{
  path: '/videocourse/:id/edit/',
  name: 'videocourse_edit',
  component: () => import('@/pages/videocourse/edit.vue'),
  meta: { title: '编辑录播课', requiredLogin: true, permission: 'class' }
}
```

## 常见问题解决

### 问题 1：视频无法播放

**症状**：VideoPlayer 组件加载但视频不播放

**解决步骤**：
1. 检查浏览器控制台是否有错误信息
2. 确认 m3u8_playlist URL 是否正确：
   ```javascript
   console.log(chapter.m3u8_playlist)
   ```
3. 检查后端视频文件是否存在：
   ```bash
   ls -la backend/judge_data/videos/chapter_*/
   ```
4. 检查 Celery 任务是否成功执行：
   ```bash
   celery -A oj_backend inspect active
   ```

### 问题 2：视频处理失败

**症状**：`video_status` 显示 "failed"，有错误消息

**解决步骤**：
1. 查看详细错误信息：
   ```python
   python manage.py shell
   from oj_course.models import CourseChapter
   ch = CourseChapter.objects.get(id=1)
   print(ch.error_message)
   ```
2. 常见原因：
   - FFmpeg 未安装或路径错误
   - 视频文件损坏或格式不支持
   - 磁盘空间不足
   - 权限问题

3. 重新处理：
   - 点击 "重新处理视频" 按钮
   - 或在 Django shell 中：
     ```python
     from oj_course.tasks import process_chapter_video
     process_chapter_video.delay(chapter_id=1)
     ```

### 问题 3：上传超时

**症状**：上传大文件时请求超时

**解决步骤**：
1. 增加超时时间（Nginx）：
   ```nginx
   proxy_connect_timeout 300;
   proxy_send_timeout 300;
   proxy_read_timeout 300;
   ```
2. 增加 Django 设置：
   ```python
   DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024 * 1024
   ```
3. 使用分片上传（需自行实现）

### 问题 4：直播课和录播课混淆

**症状**：直播课功能受到影响

**检查**：
- [ ] `/course/:id/live/` 路由未被修改
- [ ] 直播课页面（live.vue）完全独立
- [ ] 录播课使用新的 `/videocourse/` 路由
- [ ] 后端 API 端点正确区分

## 性能优化建议

### 1. 视频转码优化

```python
# 使用 GPU 加速（如有 NVIDIA GPU）
import subprocess

cmd = [
    'ffmpeg',
    '-hwaccel', 'cuda',  # 使用 CUDA 加速
    '-i', input_file,
    ...
]
```

### 2. 缓存配置

```python
# Django 缓存设置
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# 缓存课程列表（10 分钟）
from django.views.decorators.cache import cache_page

@cache_page(60 * 10)
def get_courses(request):
    ...
```

### 3. 前端优化

```javascript
// 实现虚拟列表（处理大量课程）
import { VirtualList } from '@vueuse/components'

// 延迟加载视频 Player
const VideoPlayer = defineAsyncComponent(
  () => import('@/components/VideoPlayer.vue')
)
```

## 监控和日志

### 启用详细日志

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/video_processing.log',
        },
    },
    'loggers': {
        'oj_course.video_processor': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

### 监控 Celery 任务

```bash
# 实时监控
celery -A oj_backend events

# 查看任务统计
celery -A oj_backend inspect stats

# 清理失败任务
celery -A oj_backend purge
```

## 下一步（可选功能）

- [ ] 实现视频分片上传
- [ ] 添加视频水印
- [ ] 支持多语言字幕
- [ ] 学习进度跟踪
- [ ] 视频下载功能（离线观看）
- [ ] 交互式内容（章节内嵌问题）
- [ ] 直播录制转换工具
- [ ] 批量上传功能
- [ ] CDN 集成
- [ ] 视频分析和统计

## 总结

✅ 录播课系统已完全独立于直播课系统实现，包括：
- 完整的后端视频处理流程
- 前端页面和路由配置
- API 接口
- 数据库模型

🚀 现在可以：
1. 启动后端和前端服务
2. 访问 `/videocourse/` 浏览课程
3. 创建新课程并上传视频
4. 学生观看视频课程

⚠️ 重要提醒：
- 直播课（`/course/:id/live/`）保持完全不变
- 两个系统使用不同的路由和存储空间
- 确保 FFmpeg 和 Redis/Celery 正确配置
