# ✅ 数据库彻底分离 - 改正报告

## 问题确认

您说得对！我之前的实现有严重的架构问题：

```
❌ 错误的做法：
   - 直播课：Course + CourseChapter（原有）
   - 录播课：使用同一个 CourseChapter 模型
   - API：共享 /api/course-chapters/
   → 结果：两个系统数据混在一起！
```

## 现在的正确做法

```
✅ 彻底分离：

直播课系统（保持不变）：
  └── 应用：oj_course
      ├── 模型：Course + CourseChapter
      ├── API：/api/course-chapters/
      └── 数据库表：course_* 前缀

录播课系统（全新独立）：
  └── 应用：oj_videocourse
      ├── 模型：VideoCourse + VideoCourseChapter + VideoCourseProgress
      ├── API：/api/video-courses/
      └── 数据库表：videocourse_* 前缀
```

## 完整的分离方案

### 1. 数据库完全独立

#### 直播课数据库表（oj_course）
```
course_course                    # 课程表
course_coursechapter             # 课程章节表
course_courseproblem             # 课程问题表
course_coursestudent             # 课程学生表
...等
```

#### 录播课数据库表（oj_videocourse）
```
videocourse_videocourse          # 视频课程表
videocourse_videocourseChapter   # 视频课程章节表
videocourse_progress             # 视频课程学习进度表
...
```

**没有任何共享的数据表！**

### 2. API 完全独立

#### 直播课 API（现有，不修改）
```
GET    /api/course-chapters/           # 获取课程列表
POST   /api/course-chapters/           # 创建课程
GET    /api/course-chapters/{id}/      # 获取课程详情
PUT    /api/course-chapters/{id}/      # 更新课程
DELETE /api/course-chapters/{id}/      # 删除课程
POST   /api/course-chapters/{id}/live/ # 直播课特有
...
```

#### 录播课 API（全新创建）
```
GET    /api/video-courses/             # 获取课程列表
POST   /api/video-courses/             # 创建课程
GET    /api/video-courses/{id}/        # 获取课程详情
PUT    /api/video-courses/{id}/        # 更新课程
DELETE /api/video-courses/{id}/        # 删除课程
POST   /api/video-courses/{id}/join/   # 加入课程
POST   /api/video-courses/{id}/leave/  # 离开课程
POST   /api/video-courses/{id}/upload_chapter_video/  # 上传视频
GET    /api/video-courses/{id}/chapters/{cid}/video_status/  # 视频状态
...
```

**没有任何共享的 API 端点！**

### 3. 前端完全独立

#### 直播课前端（现有，不修改）
```
pages/course/
  ├── index.vue      # 课程列表
  ├── _id.vue        # 课程详情
  ├── live.vue       # 直播课堂
  └── edit.vue       # 编辑课程
```

#### 录播课前端（全新创建）
```
pages/videocourse/
  ├── index.vue      # 课程列表
  ├── _id.vue        # 课程详情
  └── edit.vue       # 编辑课程
```

**没有任何共享的页面！**

## 已创建的独立文件

### ✅ 数据库模型（oj_videocourse/models.py）
```python
VideoCourse                  # 新的视频课程模型
VideoCourseChapter           # 新的视频课程章节模型
VideoCourseProgress          # 新的学习进度模型

数据库表：
  - videocourse_videocourse
  - videocourse_videocourseChapter
  - videocourse_progress
```

**与 Course 和 CourseChapter 完全独立！**

### ✅ API 视图（oj_videocourse/views.py）
```python
VideoCourseViewSet           # 视频课程 API
VideoCourseChapterViewSet    # 视频课程章节 API
VideoCourseProgressViewSet   # 学习进度 API

API 端点：
  - /api/video-courses/
  - /api/video-courses/{id}/
  - /api/video-courses/{id}/join/
  - /api/video-courses/{id}/leave/
  - /api/video-courses/{id}/chapters/
  - /api/video-courses/{id}/upload_chapter_video/
  - 等...
```

**与 /api/course-chapters/ 完全独立！**

### ✅ 序列化器（oj_videocourse/serializers.py）
```python
VideoCourseListSerializer           # 列表序列化
VideoCourseDetailSerializer         # 详情序列化
VideoCourseChapterSerializer        # 章节序列化
VideoCourseProgressSerializer       # 进度序列化
VideoCourseCreateUpdateSerializer   # 创建/更新序列化
```

**使用独立的 VideoCourse 模型！**

### ✅ 异步任务（oj_videocourse/tasks.py）
```python
process_videocourse_video()  # 独立的视频处理任务

与 oj_course.tasks 完全独立！
```

### ✅ 视频处理（oj_videocourse/video_processor.py）
```python
VideoCourseVideoProcessor    # 独立的视频处理器

与 oj_course.video_processor 分开！
```

### ✅ 应用配置（oj_videocourse/apps.py）
```python
class OjVideocourseConfig(AppConfig):
    name = 'oj_videocourse'
```

**完全独立的 Django 应用！**

## 需要进行的配置

### 1. 注册应用到 settings.py

```python
# backend/oj_backend/settings.py

INSTALLED_APPS = [
    # ... 其他应用 ...
    'oj_course',           # 直播课应用（现有）
    'oj_videocourse',      # 录播课应用（新增）← 添加这一行
    # ... 其他应用 ...
]
```

### 2. 注册 URL 到 urls.py

```python
# backend/oj_backend/urls.py

urlpatterns = [
    # ... 其他 URL ...
    path('api/', include([
        path('', include('oj_course.urls')),        # 直播课 API
        path('', include('oj_videocourse.urls')),   # 录播课 API（新增）
        # ... 其他 URL ...
    ])),
    # ... 其他 URL ...
]
```

### 3. 执行数据库迁移

```bash
cd backend

# 迁移直播课（现有）
python manage.py migrate oj_course

# 迁移录播课（新建）
python manage.py migrate oj_videocourse

# 或一次性迁移所有
python manage.py migrate
```

### 4. 创建输出目录

```bash
mkdir -p backend/judge_data/videocourse_output
```

## 数据流对比

### 直播课（保持不变）
```
学生 → /course/live/
     ↓
前端：pages/course/live.vue
     ↓
API：/api/course-chapters/
     ↓
后端：oj_course.views
     ↓
数据库：course_course, course_coursechapter
```

### 录播课（完全独立）
```
学生 → /videocourse/
     ↓
前端：pages/videocourse/*.vue
     ↓
API：/api/video-courses/
     ↓
后端：oj_videocourse.views
     ↓
数据库：videocourse_videocourse, videocourse_videocourseChapter
```

## 确保完全分离的检查清单

- [x] 使用新的应用 `oj_videocourse`（不是 `oj_course`）
- [x] 使用新的模型 `VideoCourse`（不是 `Course`）
- [x] 使用新的 API 端点 `/api/video-courses/`（不是 `/api/course-chapters/`）
- [x] 使用新的数据库表 `videocourse_*`（不是 `course_*`）
- [x] 使用新的视图集 `VideoCourseViewSet`（不是 `CourseViewSet`）
- [x] 使用新的序列化器 `VideoCourseSerializer`（不是 `CourseSerializer`）
- [x] 使用新的任务 `process_videocourse_video`（不是 `process_chapter_video`）
- [x] 使用新的视频处理器 `VideoCourseVideoProcessor`（不是 `VideoProcessor`）
- [x] 使用新的前端 URL `/videocourse/`（不是 `/course/`）
- [x] 使用新的前端页面 `pages/videocourse/*`（不是 `pages/course/*`）
- [x] 直播课 `pages/course/live.vue` 完全不修改

## 好处

### 1. 完全隔离
- 直播课数据和录播课数据完全分开
- 互不影响，互不污染

### 2. 独立维护
- 可以独立升级录播课功能
- 不会影响直播课系统

### 3. 独立扩展
- 可以为录播课添加特有功能（如下载、字幕等）
- 而不用修改直播课代码

### 4. 数据安全
- 两个系统的数据库迁移独立
- 一个出问题不会影响另一个

## 最后确认

✅ **直播课系统**：
- 保持完全不变
- `/course/:id/live/` 路由未修改
- `pages/course/live.vue` 文件未修改
- `oj_course` 应用未修改
- 数据库表 `course_*` 未修改

✅ **录播课系统**：
- 完全独立创建
- `/videocourse/*` 路由独立
- `pages/videocourse/*` 文件独立
- `oj_videocourse` 应用独立
- 数据库表 `videocourse_*` 独立

✅ **没有任何数据混乱！**

---

**非常抱歉之前的错误！** 现在所有文件都已正确分离。
