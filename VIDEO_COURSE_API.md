# 视频课程模块 API 文档

## 基础信息

**Base URL:** `/api/course-chapters/`

**认证:** Token 认证 (Authorization: Token {token})

**内容类型:** application/json

## API 端点

### 1. 上传视频

**请求:**
```
POST /api/course-chapters/{id}/upload-video/
Content-Type: multipart/form-data

Parameters:
- file: 视频文件 (必需)
```

**cURL 示例:**
```bash
curl -X POST \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "file=@course_video.mp4" \
  http://localhost:8000/api/course-chapters/1/upload-video/
```

**Python 示例:**
```python
import requests

headers = {
    'Authorization': 'Token YOUR_TOKEN'
}

files = {
    'file': open('course_video.mp4', 'rb')
}

response = requests.post(
    'http://localhost:8000/api/course-chapters/1/upload-video/',
    headers=headers,
    files=files
)

print(response.status_code)  # 202
print(response.json())
```

**JavaScript/Fetch 示例:**
```javascript
const fileInput = document.getElementById('video-file');
const file = fileInput.files[0];

const formData = new FormData();
formData.append('file', file);

fetch('/api/course-chapters/1/upload-video/', {
  method: 'POST',
  headers: {
    'Authorization': 'Token YOUR_TOKEN'
  },
  body: formData
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

**响应 (202 Accepted):**
```json
{
  "id": 1,
  "course": 1,
  "title": "第一章：基础概念",
  "description": "介绍基础概念",
  "order": 1,
  "video": "/media/course_videos/2024/01/video.mp4",
  "video_url": "http://localhost:8000/media/course_videos/2024/01/video.mp4",
  "video_status": "pending",
  "duration": 0,
  "resolution": "",
  "bitrate": "",
  "m3u8_url": null,
  "segments_url": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "problems": [],
  "total_count": 0,
  "solved_count": 0,
  "error_message": ""
}
```

**错误响应:**
```json
// 400 Bad Request - 未上传文件
{
  "error": "未上传文件"
}

// 400 Bad Request - 不支持的文件类型
{
  "error": "不支持的文件类型，允许的格式: .mp4, .avi, .mov, .mkv, .flv, .wmv"
}

// 400 Bad Request - 文件过大
{
  "error": "文件过大，最大允许 5GB"
}

// 403 Forbidden - 无权限
{
  "detail": "只有教师可以上传视频"
}
```

---

### 2. 查看视频处理状态

**请求:**
```
GET /api/course-chapters/{id}/video_status/
```

**cURL 示例:**
```bash
curl -X GET \
  -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/course-chapters/1/video_status/
```

**Python 示例:**
```python
import requests

headers = {'Authorization': 'Token YOUR_TOKEN'}

response = requests.get(
    'http://localhost:8000/api/course-chapters/1/video_status/',
    headers=headers
)

print(response.json())
```

**响应 (200 OK):**
```json
{
  "id": 1,
  "video_status": "processing",
  "duration": 0,
  "resolution": "",
  "bitrate": "",
  "error_message": null
}
```

**视频处理状态值:**
- `pending` - 待处理
- `processing` - 处理中
- `completed` - 已完成
- `failed` - 处理失败

**失败时的响应:**
```json
{
  "id": 1,
  "video_status": "failed",
  "duration": 0,
  "resolution": "",
  "bitrate": "",
  "error_message": "FFmpeg conversion failed: Invalid file format"
}
```

---

### 3. 获取 m3u8 播放列表

**请求:**
```
GET /api/course-chapters/{id}/video_playlist/
```

**说明:** 仅在视频处理完成后可用

**cURL 示例:**
```bash
curl -X GET \
  -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/course-chapters/1/video_playlist/
```

**Python 示例:**
```python
import requests

headers = {'Authorization': 'Token YOUR_TOKEN'}

response = requests.get(
    'http://localhost:8000/api/course-chapters/1/video_playlist/',
    headers=headers
)

data = response.json()
m3u8_url = data['m3u8_url']
print(f"M3U8 URL: {m3u8_url}")
```

**响应 (200 OK):**
```json
{
  "id": 1,
  "title": "第一章：基础概念",
  "duration": 3600,
  "resolution": "1280x720",
  "bitrate": "2500k",
  "m3u8_url": "http://localhost:8000/media/course_videos_hls/1/1/index.m3u8",
  "m3u8_content": "#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:11\n#EXT-X-MEDIA-SEQUENCE:0\n#EXTINF:10.0,\nsegment_000.ts\n#EXTINF:10.0,\nsegment_001.ts\n..."
}
```

**M3U8 文件格式示例:**
```
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:11
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:10.0,
segment_000.ts
#EXTINF:10.0,
segment_001.ts
#EXTINF:10.0,
segment_002.ts
...
#EXT-X-ENDLIST
```

**错误响应:**
```json
// 400 Bad Request - 视频还未处理完成
{
  "error": "视频处理状态: processing"
}

// 404 Not Found - 视频不存在
{
  "error": "未找到 m3u8 播放列表"
}
```

---

### 4. 重新处理视频

**请求:**
```
POST /api/course-chapters/{id}/reprocess_video/
```

**说明:** 重新开始视频转换流程，通常用于修复失败的转换

**cURL 示例:**
```bash
curl -X POST \
  -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/course-chapters/1/reprocess_video/
```

**Python 示例:**
```python
import requests

headers = {'Authorization': 'Token YOUR_TOKEN'}

response = requests.post(
    'http://localhost:8000/api/course-chapters/1/reprocess_video/',
    headers=headers
)

print(response.status_code)  # 202
print(response.json())
```

**响应 (202 Accepted):**
```json
{
  "id": 1,
  "course": 1,
  "title": "第一章：基础概念",
  "video_status": "pending",
  "duration": 0,
  "resolution": "",
  "m3u8_url": null,
  "segments_url": null,
  "error_message": ""
}
```

**错误响应:**
```json
// 400 Bad Request - 没有视频文件
{
  "error": "章节中没有视频文件"
}

// 403 Forbidden - 无权限
{
  "detail": "只有教师可以重新处理视频"
}
```

---

### 5. 获取课程章节列表

**请求:**
```
GET /api/course-chapters/?course_id={course_id}
```

**查询参数:**
- `course_id` - 课程 ID (可选)
- `limit` - 分页数量 (默认: 20)
- `offset` - 分页偏移 (默认: 0)

**cURL 示例:**
```bash
curl -X GET \
  "http://localhost:8000/api/course-chapters/?course_id=1&limit=10"
```

**Python 示例:**
```python
import requests

params = {
    'course_id': 1,
    'limit': 10,
    'offset': 0
}

response = requests.get(
    'http://localhost:8000/api/course-chapters/',
    params=params
)

chapters = response.json()['results']
for chapter in chapters:
    print(f"{chapter['title']}: {chapter['video_status']}")
```

**响应 (200 OK):**
```json
{
  "count": 5,
  "next": "http://localhost:8000/api/course-chapters/?course_id=1&limit=10&offset=10",
  "previous": null,
  "results": [
    {
      "id": 1,
      "course": 1,
      "title": "第一章：基础概念",
      "description": "介绍基础概念",
      "order": 1,
      "video": "/media/course_videos/2024/01/video.mp4",
      "video_url": "http://localhost:8000/media/course_videos/2024/01/video.mp4",
      "video_status": "completed",
      "duration": 3600,
      "resolution": "1280x720",
      "bitrate": "2500k",
      "m3u8_url": "http://localhost:8000/media/course_videos_hls/1/1/index.m3u8",
      "segments_url": "http://localhost:8000/media/course_videos_hls/1/1/",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T11:00:00Z",
      "problems": [],
      "total_count": 0,
      "solved_count": 0,
      "error_message": ""
    },
    {
      "id": 2,
      "course": 1,
      "title": "第二章：进阶内容",
      "description": "深入讲解进阶主题",
      "order": 2,
      "video": null,
      "video_url": null,
      "video_status": "pending",
      "duration": 0,
      "resolution": "",
      "bitrate": "",
      "m3u8_url": null,
      "segments_url": null,
      "created_at": "2024-01-15T11:30:00Z",
      "updated_at": "2024-01-15T11:30:00Z",
      "problems": [],
      "total_count": 0,
      "solved_count": 0,
      "error_message": ""
    }
  ]
}
```

---

### 6. 创建课程章节

**请求:**
```
POST /api/course-chapters/
Content-Type: application/json

{
  "course": 1,
  "title": "第一章",
  "description": "章节描述",
  "order": 1,
  "problem_ids": [1, 2, 3]
}
```

**cURL 示例:**
```bash
curl -X POST \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "course": 1,
    "title": "第一章",
    "description": "章节描述",
    "order": 1
  }' \
  http://localhost:8000/api/course-chapters/
```

**响应 (201 Created):**
```json
{
  "id": 3,
  "course": 1,
  "title": "第一章",
  "description": "章节描述",
  "order": 1,
  "video": null,
  "video_url": null,
  "video_status": "pending",
  "duration": 0,
  "resolution": "",
  "m3u8_url": null,
  "segments_url": null,
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-15T12:00:00Z",
  "problems": [],
  "total_count": 0,
  "solved_count": 0,
  "error_message": ""
}
```

---

### 7. 更新课程章节

**请求:**
```
PUT /api/course-chapters/{id}/
PATCH /api/course-chapters/{id}/
Content-Type: application/json
```

**示例:**
```bash
curl -X PATCH \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "更新后的标题",
    "description": "更新后的描述"
  }' \
  http://localhost:8000/api/course-chapters/1/
```

**响应 (200 OK):** 更新后的章节数据

---

### 8. 删除课程章节

**请求:**
```
DELETE /api/course-chapters/{id}/
```

**cURL 示例:**
```bash
curl -X DELETE \
  -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/course-chapters/1/
```

**响应 (204 No Content):** 无响应体

---

## 常见使用场景

### 场景 1: 完整的视频上传流程

```python
import requests
import time

BASE_URL = 'http://localhost:8000/api'
HEADERS = {'Authorization': 'Token YOUR_TOKEN'}

# 第一步：上传视频
print("1. 上传视频...")
files = {'file': open('lecture.mp4', 'rb')}
response = requests.post(
    f'{BASE_URL}/course-chapters/1/upload-video/',
    headers=HEADERS,
    files=files
)
print(f"上传状态: {response.status_code}")

# 第二步：轮询检查处理状态
print("2. 等待视频处理...")
chapter_id = response.json()['id']

while True:
    response = requests.get(
        f'{BASE_URL}/course-chapters/{chapter_id}/video_status/',
        headers=HEADERS
    )
    status = response.json()['video_status']
    print(f"处理状态: {status}")
    
    if status == 'completed':
        print("3. 处理完成!")
        break
    elif status == 'failed':
        print(f"处理失败: {response.json()['error_message']}")
        break
    
    time.sleep(5)  # 每 5 秒检查一次

# 第三步：获取播放列表
if status == 'completed':
    response = requests.get(
        f'{BASE_URL}/course-chapters/{chapter_id}/video_playlist/',
        headers=HEADERS
    )
    m3u8_url = response.json()['m3u8_url']
    print(f"4. 播放 URL: {m3u8_url}")
```

### 场景 2: 在前端显示视频播放器

```vue
<template>
  <div>
    <!-- 查看视频处理状态 -->
    <div v-if="videoStatus === 'processing'">
      <p>视频处理中，请稍候...</p>
      <progress :value="processingPercent" max="100"></progress>
    </div>

    <!-- 播放完成的视频 -->
    <div v-else-if="videoStatus === 'completed'">
      <video controls width="100%" height="auto">
        <source :src="m3u8Url" type="application/x-mpegURL" />
      </video>
    </div>

    <!-- 显示错误信息 -->
    <div v-else-if="videoStatus === 'failed'">
      <p style="color: red;">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      chapterId: 1,
      videoStatus: 'pending',
      m3u8Url: '',
      errorMessage: ''
    }
  },
  mounted() {
    this.pollVideoStatus()
  },
  methods: {
    async pollVideoStatus() {
      const poll = setInterval(async () => {
        const response = await fetch(
          `/api/course-chapters/${this.chapterId}/video_status/`,
          {
            headers: {
              'Authorization': `Token ${this.getAuthToken()}`
            }
          }
        )
        const data = await response.json()
        this.videoStatus = data.video_status

        if (this.videoStatus === 'completed') {
          clearInterval(poll)
          await this.loadPlaylist()
        } else if (this.videoStatus === 'failed') {
          clearInterval(poll)
          this.errorMessage = data.error_message
        }
      }, 5000)
    },

    async loadPlaylist() {
      const response = await fetch(
        `/api/course-chapters/${this.chapterId}/video_playlist/`,
        {
          headers: {
            'Authorization': `Token ${this.getAuthToken()}`
          }
        }
      )
      const data = await response.json()
      this.m3u8Url = data.m3u8_url
    },

    getAuthToken() {
      return localStorage.getItem('auth_token')
    }
  }
}
</script>
```

---

## 错误处理

### HTTP 状态码

| 状态码 | 含义 | 处理方式 |
|--------|------|---------|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 202 | Accepted | 异步任务已接受 |
| 204 | No Content | 成功删除 |
| 400 | Bad Request | 检查请求参数 |
| 403 | Forbidden | 检查权限 |
| 404 | Not Found | 资源不存在 |
| 500 | Server Error | 服务器错误，检查日志 |

### 常见错误处理

```python
import requests

try:
    response = requests.post(
        'http://localhost:8000/api/course-chapters/1/upload-video/',
        files={'file': open('video.mp4', 'rb')},
        headers={'Authorization': 'Token TOKEN'}
    )
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 400:
        error_data = e.response.json()
        print(f"请求错误: {error_data.get('error')}")
    elif e.response.status_code == 403:
        print("您没有权限执行此操作")
    elif e.response.status_code == 500:
        print("服务器错误，请重试")
except Exception as e:
    print(f"网络错误: {e}")
```

---

## 性能提示

1. **使用异步处理** - 长时间的视频转换应使用异步任务
2. **合理轮询间隔** - 检查状态的间隔不应过短（建议 5-10 秒）
3. **缓存结果** - 获取到 m3u8 URL 后应缓存，避免重复请求
4. **分页加载** - 列表数据应使用分页避免一次加载过多
5. **错误重试** - 失败的任务应支持重新处理

