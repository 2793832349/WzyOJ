# 🚀 录播课系统 - 3 分钟快速启动

## 前置要求

- [ ] Python 3.8+ 已安装
- [ ] Node.js 14+ 已安装
- [ ] FFmpeg 已安装：`ffmpeg -version`
- [ ] Redis 已安装：`redis-server --version`

## ⚡ 一键启动（推荐）

### 在 Linux/Mac 上

创建 `start-videocourse.sh`：

```bash
#!/bin/bash

echo "🚀 启动录播课系统..."

# 启动 Redis
echo "📌 启动 Redis..."
redis-server --daemonize yes

# 启动后端
echo "📌 启动后端服务..."
cd backend
python manage.py migrate > /dev/null 2>&1
celery -A oj_backend worker -l warning --logfile=/tmp/celery.log &
CELERY_PID=$!
python manage.py runserver 0.0.0.0:8000 &
DJANGO_PID=$!

# 启动前端
echo "📌 启动前端服务..."
cd ../frontend-naive
npm install > /dev/null 2>&1
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ 所有服务已启动！"
echo ""
echo "访问地址："
echo "  • 录播课列表：http://localhost:5173/videocourse/"
echo "  • 直播课列表：http://localhost:5173/course/"
echo "  • Admin 后台：http://localhost:8000/admin/"
echo ""
echo "进程 ID："
echo "  • Django:  $DJANGO_PID"
echo "  • Celery:  $CELERY_PID"
echo "  • Frontend: $FRONTEND_PID"
echo ""
echo "停止服务："
echo "  kill $DJANGO_PID $CELERY_PID $FRONTEND_PID"
echo ""

wait
```

执行：
```bash
chmod +x start-videocourse.sh
./start-videocourse.sh
```

### 在 Windows 上

创建 `start-videocourse.bat`：

```batch
@echo off
echo 🚀 启动录播课系统...

REM 启动 Redis（确保已安装）
echo 📌 启动 Redis...
start redis-server.exe

REM 启动后端
echo 📌 启动后端服务...
cd backend
python manage.py migrate
start /B celery -A oj_backend worker -l warning
start python manage.py runserver 0.0.0.0:8000

REM 启动前端
echo 📌 启动前端服务...
cd ..\frontend-naive
npm install
start npm run dev

echo.
echo ✅ 所有服务已启动！
echo.
echo 访问地址：
echo   • 录播课列表：http://localhost:5173/videocourse/
echo   • 直播课列表：http://localhost:5173/course/
echo   • Admin 后台：http://localhost:8000/admin/
echo.

pause
```

执行：
```bash
start-videocourse.bat
```

---

## 📝 分步启动（如需调试）

### 步骤 1：启动 Redis（终端 1）

```bash
redis-server
```

### 步骤 2：启动 Celery Worker（终端 2）

```bash
cd backend
celery -A oj_backend worker -l info
```

### 步骤 3：启动 Django（终端 3）

```bash
cd backend
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### 步骤 4：启动前端（终端 4）

```bash
cd frontend-naive
npm install
npm run dev
```

### 步骤 5：访问应用

打开浏览器，访问：
```
http://localhost:5173/videocourse/
```

---

## ✨ 第一次使用

### 创建管理员账户

```bash
cd backend
python manage.py createsuperuser
```

### 登录 Admin 后台

访问 `http://localhost:8000/admin/` 并登录

### 创建第一个课程

1. 访问 `http://localhost:5173/videocourse/create/`
2. 填写课程信息：
   - **课程名称**：例如 "Python 基础"
   - **课程描述**：例如 "学习 Python 编程基础"

3. 添加章节：
   - 点击 "添加章节" 按钮
   - 填写章节标题：例如 "第一章：介绍"
   - 填写章节描述

4. 上传视频：
   - 选择 MP4 视频文件
   - 点击保存

5. 等待处理：
   - 视频会在后台异步处理
   - 您可以查看处理状态
   - 处理完成后可以播放

### 学生使用

1. 访问 `http://localhost:5173/videocourse/`
2. 搜索或浏览课程
3. 点击课程卡片查看详情
4. 点击 "加入课程" 按钮
5. 选择章节播放视频

---

## 🔍 常见问题速查

### Q1：FFmpeg 未安装
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# MacOS
brew install ffmpeg

# Windows
# 下载：https://ffmpeg.org/download.html
```

### Q2：Redis 连接失败
```bash
# 检查 Redis 是否运行
redis-cli ping

# 应该返回 PONG
# 如果没有，启动 Redis：
redis-server
```

### Q3：视频上传后未处理
```bash
# 检查 Celery Worker 是否运行
ps aux | grep celery

# 如果未运行，启动它
celery -A oj_backend worker -l info
```

### Q4：前端访问 localhost:5173 超时
```bash
# 检查前端进程
ps aux | grep "npm run dev"

# 或重启前端
cd frontend-naive
npm run dev
```

### Q5：直播课功能缺失
```bash
# 确认 /course/:id/live/ 路由未被修改
grep -A 5 "course_live" frontend-naive/src/router/index.js

# 直播课应该完全独立于录播课
```

---

## 📊 服务状态检查

### 检查所有服务

```bash
# Redis
redis-cli ping
# 应该输出：PONG

# Celery
celery -A oj_backend inspect active
# 应该显示任务信息

# Django
curl http://localhost:8000/api/course-chapters/
# 应该返回 JSON 数据

# 前端
curl http://localhost:5173/videocourse/
# 应该返回 HTML
```

### 查看日志

```bash
# Celery 日志
tail -f /tmp/celery.log

# Django 日志
# 在启动的终端中直接显示

# 系统日志
# 检查 browser console：F12 → Console 标签
```

---

## 🧹 清理和重置

### 清除数据库

```bash
cd backend
python manage.py flush --noinput
python manage.py migrate
```

### 清除视频文件

```bash
rm -rf backend/judge_data/videos/*
```

### 清除 Celery 任务队列

```bash
celery -A oj_backend purge
```

### 清除前端缓存

```bash
cd frontend-naive
rm -rf node_modules/
npm install
```

---

## 📚 有用的命令

### 创建测试数据

```bash
cd backend
python manage.py shell

from oj_course.models import CourseChapter, Course
from django.contrib.auth.models import User

# 创建课程
course = Course.objects.create(
    title="测试课程",
    description="这是一个测试课程",
    creator=User.objects.first()
)

# 创建章节
chapter = CourseChapter.objects.create(
    title="第一章",
    description="测试章节",
    course=course,
    order=1
)

print(f"课程 ID: {course.id}")
print(f"章节 ID: {chapter.id}")
```

### 监控视频处理

```bash
cd backend
python manage.py shell

from oj_course.models import CourseChapter

# 查看所有视频处理状态
for ch in CourseChapter.objects.filter(video_status__isnull=False):
    print(f"ID: {ch.id}, 标题: {ch.title}, 状态: {ch.video_status}")
    if ch.error_message:
        print(f"  错误：{ch.error_message}")
```

### 手动处理视频

```bash
cd backend
python manage.py shell

from oj_course.tasks import process_chapter_video

# 重新处理视频
process_chapter_video.delay(chapter_id=1)

# 或同步处理
process_chapter_video(chapter_id=1)
```

---

## 🎯 完整工作流示例

```
1. 启动所有服务
   ↓
2. 访问 Admin 后台创建测试账户
   ↓
3. 访问 /videocourse/create/ 创建课程
   ↓
4. 上传 MP4 视频文件
   ↓
5. 等待 Celery 处理（后台自动进行）
   ↓
6. 处理完成后，视频自动可用
   ↓
7. 学生访问 /videocourse/ 查看课程
   ↓
8. 点击课程进入详情页
   ↓
9. 选择章节播放视频
   ↓
✅ 完成！
```

---

## 🆘 需要帮助？

1. **查看日志**：检查终端输出和浏览器控制台
2. **查看文档**：
   - 用户指南：[VIDEOCOURSE_GUIDE.md](./VIDEOCOURSE_GUIDE.md)
   - 实现指南：[VIDEOCOURSE_IMPLEMENTATION.md](./VIDEOCOURSE_IMPLEMENTATION.md)
   - 完整检查：[VIDEOCOURSE_VERIFICATION.md](./VIDEOCOURSE_VERIFICATION.md)

3. **问题排查**：[VIDEOCOURSE_CHECKLIST.md](./VIDEOCOURSE_CHECKLIST.md#-常见问题快速排查)

---

## ⏱️ 预期启动时间

| 操作 | 耗时 |
|------|------|
| Redis 启动 | < 1 秒 |
| Celery Worker 启动 | 2-3 秒 |
| Django 启动 | 3-5 秒 |
| 前端 npm install | 30-60 秒（首次） |
| 前端启动 | 5-10 秒 |
| **总计（首次）** | **50-80 秒** |
| **总计（后续）** | **10-15 秒** |

---

## ✅ 验证清单

启动完成后，检查以下项目：

- [ ] Redis 运行中：`redis-cli ping` 返回 PONG
- [ ] Celery 运行中：终端显示 "Listening on amqp://..."
- [ ] Django 运行中：终端显示 "Starting development server..."
- [ ] 前端运行中：访问 `http://localhost:5173` 显示页面
- [ ] 录播课可访问：访问 `http://localhost:5173/videocourse/` 显示课程列表
- [ ] 直播课可访问：访问 `http://localhost:5173/course/` 显示课程列表
- [ ] Admin 可访问：访问 `http://localhost:8000/admin/` 显示登录页

---

## 🎉 祝您使用愉快！

现在您可以：
- ✅ 创建和管理录播课程
- ✅ 上传和处理 MP4 视频
- ✅ 学生观看视频课程
- ✅ 完整的学习体验

**立即开始**：`http://localhost:5173/videocourse/`
