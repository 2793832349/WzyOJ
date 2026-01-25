# 视频课程模块 - 实施检查清单

## 安装和配置检查

### ✅ 后端配置

- [ ] 安装 Python 依赖
  ```bash
  pip install -r backend/requirements.txt
  ```
  
- [ ] 安装 FFmpeg
  ```bash
  # Ubuntu/Debian
  sudo apt-get install ffmpeg
  
  # 验证
  ffmpeg -version
  ```

- [ ] 配置 Django 设置 (settings.py)
  ```python
  INSTALLED_APPS = [..., 'oj_course', ...]
  MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
  MEDIA_URL = '/media/'
  ```

- [ ] 配置 Celery (settings.py)
  ```python
  CELERY_BROKER_URL = 'redis://localhost:6379/0'
  CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
  ```

- [ ] 运行数据库迁移
  ```bash
  python manage.py migrate oj_course
  ```

- [ ] 启动 Redis
  ```bash
  redis-server
  ```

- [ ] 启动 Celery Worker
  ```bash
  celery -A oj_backend worker -l info
  ```

### ✅ 前端配置

- [ ] 安装前端依赖
  ```bash
  cd frontend-naive
  npm install
  ```

- [ ] 配置 API 地址 (src/config.js)
  ```javascript
  export const API_BASE_URL = 'http://localhost:8000/api'
  ```

- [ ] 注册组件
  - [ ] VideoPlayer.vue
  - [ ] VideoCourseManager.vue

- [ ] 启动开发服务器
  ```bash
  npm run dev
  ```

## 功能测试检查

### ✅ 后端功能

- [ ] **上传视频**
  - [ ] 上传 MP4 文件
  - [ ] 验证文件类型检查
  - [ ] 验证文件大小限制
  - [ ] 确认返回 202 状态码
  - [ ] 验证权限检查（仅教师可上传）

- [ ] **异步处理**
  - [ ] Celery 任务被创建
  - [ ] 视频状态变为 "processing"
  - [ ] FFmpeg 转换开始
  - [ ] 生成 ts 分片
  - [ ] 状态变为 "completed"

- [ ] **查询状态**
  ```bash
  curl -X GET \
    -H "Authorization: Token YOUR_TOKEN" \
    http://localhost:8000/api/course-chapters/{id}/video_status/
  ```
  - [ ] 返回正确的状态
  - [ ] 显示时长和分辨率
  - [ ] 错误时显示错误信息

- [ ] **获取播放列表**
  ```bash
  curl -X GET \
    -H "Authorization: Token YOUR_TOKEN" \
    http://localhost:8000/api/course-chapters/{id}/video_playlist/
  ```
  - [ ] 返回 m3u8 URL
  - [ ] m3u8 内容正确
  - [ ] 分片文件存在

- [ ] **重新处理**
  ```bash
  curl -X POST \
    -H "Authorization: Token YOUR_TOKEN" \
    http://localhost:8000/api/course-chapters/{id}/reprocess_video/
  ```
  - [ ] 状态重置为 "pending"
  - [ ] 重新开始处理
  - [ ] 新的分片生成

### ✅ 前端功能

- [ ] **VideoPlayer 组件**
  - [ ] 初始化时检查状态
  - [ ] 轮询状态（5 秒间隔）
  - [ ] 处理完成后加载 m3u8
  - [ ] 视频正常播放
  - [ ] 显示视频信息
  - [ ] 显示加载状态
  - [ ] 显示错误信息
  - [ ] 错误时提供重试按钮

- [ ] **VideoCourseManager 组件**
  - [ ] 显示章节列表
  - [ ] 显示上传表单
  - [ ] 拖拽上传工作
  - [ ] 显示上传进度
  - [ ] 显示处理状态
  - [ ] 显示视频信息
  - [ ] 支持编辑操作
  - [ ] 支持删除操作
  - [ ] 支持重新处理

### ✅ API 端点

- [ ] POST /api/course-chapters/{id}/upload-video/
  - [ ] 上传成功返回 202
  - [ ] 权限验证
  - [ ] 文件验证

- [ ] GET /api/course-chapters/{id}/video_status/
  - [ ] 返回当前状态
  - [ ] 显示处理信息

- [ ] GET /api/course-chapters/{id}/video_playlist/
  - [ ] 返回 m3u8 URL
  - [ ] 返回 m3u8 内容

- [ ] POST /api/course-chapters/{id}/reprocess_video/
  - [ ] 重新处理成功
  - [ ] 权限验证

## 文件检查

### ✅ 后端文件

- [ ] `backend/oj_course/models.py` - 数据模型扩展
  - [ ] `VideoProcessingStatus` 枚举
  - [ ] `CourseChapter` 新增字段

- [ ] `backend/oj_course/serializers.py` - API 序列化器
  - [ ] `CourseChapterSerializer` 更新
  - [ ] 新增字段支持

- [ ] `backend/oj_course/views.py` - API 视图
  - [ ] `upload_video` 方法
  - [ ] `video_status` 方法
  - [ ] `video_playlist` 方法
  - [ ] `reprocess_video` 方法

- [ ] `backend/oj_course/video_processor.py` - 视频处理
  - [ ] `VideoProcessor` 类
  - [ ] FFmpeg 集成
  - [ ] 错误处理

- [ ] `backend/oj_course/tasks.py` - Celery 任务
  - [ ] `process_chapter_video` 任务
  - [ ] 重试机制

- [ ] `backend/oj_course/migrations/0002_add_video_processing.py` - 数据库迁移
  - [ ] 所有新字段都包含

- [ ] `backend/requirements.txt` - 依赖更新
  - [ ] opencv-python 添加
  - [ ] Pillow 添加

### ✅ 前端文件

- [ ] `frontend-naive/src/components/VideoPlayer.vue`
  - [ ] 完整的播放器逻辑
  - [ ] 状态检查
  - [ ] 错误处理

- [ ] `frontend-naive/src/components/VideoCourseManager.vue`
  - [ ] 上传界面
  - [ ] 列表管理
  - [ ] 操作功能

### ✅ 文档文件

- [ ] `VIDEO_COURSE_GUIDE.md` - 完整功能指南
- [ ] `VIDEO_COURSE_API.md` - API 文档
- [ ] `VIDEO_COURSE_DEPLOYMENT.md` - 部署指南
- [ ] `VIDEO_COURSE_QUICKSTART.md` - 快速开始
- [ ] `VIDEO_COURSE_SUMMARY.md` - 实现总结

## 部署检查

### ✅ 开发环境

- [ ] Django 开发服务器运行
- [ ] Celery worker 运行
- [ ] Redis 运行
- [ ] PostgreSQL 运行
- [ ] 前端开发服务器运行

### ✅ 测试环境

- [ ] Docker 构建成功
- [ ] docker-compose 启动成功
- [ ] 所有服务正常运行
- [ ] 日志输出正常

### ✅ 生产环境准备

- [ ] Nginx 配置完成
- [ ] SSL 证书配置
- [ ] 日志目录创建
- [ ] 媒体目录权限设置
- [ ] 数据库备份策略
- [ ] 监控脚本部署

## 性能测试

- [ ] 上传 100MB 文件 - 检查速度和稳定性
- [ ] 上传 1GB 文件 - 检查大文件处理
- [ ] 转换完成时间 - 检查是否在预期范围
- [ ] 播放流畅度 - 检查 m3u8 播放质量
- [ ] 并发处理 - 测试多个视频同时处理
- [ ] 磁盘占用 - 验证预期的 1.2x 倍数

## 安全检查

- [ ] 权限验证
  - [ ] 仅教师可上传
  - [ ] 仅创建者可删除
  - [ ] 学生只能查看

- [ ] 文件验证
  - [ ] 文件类型检查
  - [ ] 文件大小限制
  - [ ] 恶意文件拒绝

- [ ] API 安全
  - [ ] Token 认证
  - [ ] CORS 配置
  - [ ] Rate limiting（可选）

- [ ] 存储安全
  - [ ] 目录权限设置
  - [ ] 备份策略
  - [ ] 数据加密（可选）

## 兼容性检查

### 浏览器

- [ ] Chrome 最新版
- [ ] Firefox 最新版
- [ ] Safari 最新版
- [ ] Edge 最新版
- [ ] 移动浏览器 (iOS Safari, Chrome Mobile)

### 视频格式

- [ ] MP4 (.mp4)
- [ ] AVI (.avi)
- [ ] MOV (.mov)
- [ ] MKV (.mkv)
- [ ] FLV (.flv)
- [ ] WMV (.wmv)

### 设备

- [ ] 桌面电脑 (1920x1080)
- [ ] 平板 (iPad 1024x768)
- [ ] 手机 (iPhone 375x667)
- [ ] 高分屏 (4K 3840x2160)

## 文档检查

- [ ] 所有 API 端点有文档
- [ ] 所有参数有说明
- [ ] 所有响应格式清晰
- [ ] 有使用示例 (cURL, Python, JS)
- [ ] 有错误处理说明
- [ ] 有部署说明
- [ ] 有故障排查说明
- [ ] 有快速开始指南

## 最后检查

- [ ] 代码审查完成
- [ ] 没有硬编码的敏感信息
- [ ] 日志不泄露敏感信息
- [ ] 错误消息对用户友好
- [ ] 性能满足预期
- [ ] 所有功能正常工作
- [ ] 文档完整准确
- [ ] 准备好上线

## 上线前待办事项

- [ ] [ ] 备份生产数据库
- [ ] [ ] 配置监控告警
- [ ] [ ] 准备回滚方案
- [ ] [ ] 通知用户更新信息
- [ ] [ ] 准备技术支持文档
- [ ] [ ] 安排值班人员
- [ ] [ ] 测试日志收集
- [ ] [ ] 验证备份恢复流程

## 反馈和改进

- [ ] 收集用户反馈
- [ ] 记录 bug
- [ ] 优化性能
- [ ] 改进文档
- [ ] 添加新功能

---

**检查清单版本**: 1.0
**最后更新**: 2026年1月25日
**状态**: 准备上线

完成以上所有检查后，系统即可正式上线！
