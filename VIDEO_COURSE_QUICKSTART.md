# 视频课程模块 - 快速开始

## 5 分钟快速开始

### 后端部分

#### 1. 安装依赖
```bash
# 安装 Python 包
pip install -r requirements.txt

# 安装 FFmpeg（Ubuntu/Debian）
sudo apt-get install ffmpeg

# 验证安装
ffmpeg -version
```

#### 2. 配置数据库迁移
```bash
# 执行迁移
python manage.py migrate oj_course

# 或指定迁移文件
python manage.py migrate oj_course 0002_add_video_processing
```

#### 3. 启动 Celery
```bash
# 在新终端启动 Celery worker
celery -A oj_backend worker -l info

# 或使用 Celery beat（用于定时任务）
celery -A oj_backend worker -B -l info
```

#### 4. 启动开发服务器
```bash
# 在新终端启动 Django
python manage.py runserver 0.0.0.0:8000
```

### 前端部分

#### 1. 安装依赖
```bash
cd frontend-naive
npm install
```

#### 2. 配置 API 地址
编辑 `src/config.js`:
```javascript
export const API_BASE_URL = 'http://localhost:8000/api'
```

#### 3. 启动开发服务器
```bash
npm run dev
```

### 测试上传

#### 使用 cURL
```bash
# 上传视频
curl -X POST \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "file=@test_video.mp4" \
  http://localhost:8000/api/course-chapters/1/upload-video/

# 检查状态
curl -X GET \
  -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/course-chapters/1/video_status/
```

#### 使用 Python
```python
import requests

headers = {'Authorization': 'Token YOUR_TOKEN'}
files = {'file': open('test_video.mp4', 'rb')}

# 上传
response = requests.post(
    'http://localhost:8000/api/course-chapters/1/upload-video/',
    headers=headers,
    files=files
)
print(response.status_code)
print(response.json())

# 轮询检查状态
import time

chapter_id = response.json()['id']
while True:
    status_response = requests.get(
        f'http://localhost:8000/api/course-chapters/{chapter_id}/video_status/',
        headers=headers
    )
    status = status_response.json()['video_status']
    print(f"Status: {status}")
    
    if status in ['completed', 'failed']:
        break
    time.sleep(5)
```

## 常见问题

### Q: 视频上传后没有反应？
**A:** 
1. 确保 Celery worker 正在运行
2. 检查 Redis 连接：`redis-cli ping`
3. 查看日志：`tail -f logs/celery.log`

### Q: FFmpeg 命令未找到？
**A:** 
```bash
# 查找 ffmpeg 路径
which ffmpeg

# 如果未安装
sudo apt-get install ffmpeg
```

### Q: 视频转换很慢？
**A:**
1. 检查 CPU 使用率
2. 增加 Celery 并发数
3. 降低视频质量（CRF 值调高）

### Q: 存储空间不足？
**A:**
```bash
# 检查磁盘使用
df -h /var/www/oj/media/

# 清理旧文件
find /var/www/oj/media -mtime +30 -delete
```

### Q: m3u8 播放不了？
**A:**
1. 确认转换状态为 "completed"
2. 检查分片文件是否存在
3. 查看浏览器控制台错误
4. 确保 CORS 配置正确

## 项目结构

```
WzyOJ/
├── backend/
│   ├── oj_course/
│   │   ├── models.py              # 数据模型
│   │   ├── serializers.py         # API 序列化器
│   │   ├── views.py               # API 视图
│   │   ├── video_processor.py     # 视频处理器
│   │   ├── tasks.py               # Celery 任务
│   │   └── migrations/
│   │       └── 0002_add_video_processing.py
│   └── requirements.txt
│
├── frontend-naive/
│   ├── src/
│   │   ├── components/
│   │   │   ├── VideoPlayer.vue    # 视频播放器
│   │   │   └── VideoCourseManager.vue  # 课程管理
│   │   └── main.js
│   └── package.json
│
├── VIDEO_COURSE_GUIDE.md          # 完整功能指南
├── VIDEO_COURSE_API.md            # API 文档
└── VIDEO_COURSE_DEPLOYMENT.md     # 部署指南
```

## 核心 API 端点

| 方法 | 端点 | 功能 |
|------|------|------|
| POST | `/api/course-chapters/{id}/upload-video/` | 上传视频 |
| GET | `/api/course-chapters/{id}/video_status/` | 查看处理状态 |
| GET | `/api/course-chapters/{id}/video_playlist/` | 获取 m3u8 URL |
| POST | `/api/course-chapters/{id}/reprocess_video/` | 重新处理 |

## 完整示例：上传和播放

### 后端逻辑

```python
# 1. 教师上传视频（views.py）
@action(detail=True, methods=['post'], url_path='upload-video')
def upload_video(self, request, pk=None):
    chapter = self.get_object()
    video_file = request.FILES.get('file')
    
    # 保存视频并触发异步任务
    chapter.video = video_file
    chapter.save()
    process_chapter_video.delay(chapter.id)  # Celery 异步处理
    
    return Response(serializer.data, status=202)

# 2. Celery 处理视频（tasks.py）
@shared_task
def process_chapter_video(chapter_id):
    chapter = CourseChapter.objects.get(id=chapter_id)
    processor = VideoProcessor(chapter)
    processor.process()  # 转换为 m3u8

# 3. 学生查看状态（views.py）
@action(detail=True, methods=['get'])
def video_status(self, request, pk=None):
    chapter = self.get_object()
    return Response({
        'video_status': chapter.video_status,
        'duration': chapter.duration,
        'resolution': chapter.resolution,
    })

# 4. 学生获取播放列表（views.py）
@action(detail=True, methods=['get'])
def video_playlist(self, request, pk=None):
    chapter = self.get_object()
    return Response({
        'm3u8_url': f'/media/{chapter.video_segments_dir}/index.m3u8',
        'duration': chapter.duration,
    })
```

### 前端流程

```vue
<template>
  <!-- 上传部分（教师）-->
  <input 
    type="file" 
    @change="uploadVideo"
    accept="video/*"
  />
  
  <!-- 播放部分（学生）-->
  <VideoPlayer 
    v-if="videoStatus === 'completed'"
    :chapterId="chapterId"
  />
  
  <!-- 进度显示 -->
  <div v-if="videoStatus === 'processing'">
    处理中...{{ processingPercent }}%
  </div>
</template>

<script>
export default {
  methods: {
    async uploadVideo(file) {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await fetch(
        `/api/course-chapters/${this.chapterId}/upload-video/`,
        {
          method: 'POST',
          headers: { 'Authorization': `Token ${token}` },
          body: formData
        }
      )
      
      // 轮询检查状态
      this.pollStatus()
    },
    
    async pollStatus() {
      while (true) {
        const response = await fetch(
          `/api/course-chapters/${this.chapterId}/video_status/`,
          { headers: { 'Authorization': `Token ${token}` } }
        )
        const data = await response.json()
        
        if (data.video_status === 'completed') {
          // 加载播放器
          this.loadPlaylist()
          break
        }
        
        await new Promise(r => setTimeout(r, 5000))
      }
    }
  }
}
</script>
```

## 下一步

1. **阅读完整指南** - 查看 `VIDEO_COURSE_GUIDE.md`
2. **API 文档** - 查看 `VIDEO_COURSE_API.md`
3. **部署指南** - 查看 `VIDEO_COURSE_DEPLOYMENT.md`
4. **定制功能** - 根据需要修改 `video_processor.py`

## 获取帮助

- 查看日志：`tail -f logs/*.log`
- 检查数据库：`python manage.py dbshell`
- 查看任务：`celery -A oj_backend inspect active`
- 查看队列：`redis-cli LLEN celery`

## 支持的视频格式

- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- MKV (.mkv)
- FLV (.flv)
- WMV (.wmv)

最大文件大小：**5GB**

## 技术栈

- **后端**: Django + Django REST Framework
- **异步任务**: Celery + Redis
- **视频处理**: FFmpeg
- **前端**: Vue.js
- **流媒体**: HLS (m3u8/ts)

## 许可证

遵循项目主许可证。
