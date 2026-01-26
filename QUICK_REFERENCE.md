# ⚡ 快速参考卡

## 📦 系统现状

### ✅ 已完成
```
新应用: oj_videocourse
├── models.py           ✓ 3 个模型
├── views.py            ✓ 3 个视图集
├── serializers.py      ✓ 5 个序列化器
├── urls.py             ✓ 独立路由
├── tasks.py            ✓ Celery 任务
├── video_processor.py  ✓ 视频处理
├── admin.py            ✓ Admin 配置
├── apps.py             ✓ 应用配置
└── migrations/         ✓ 数据库迁移

settings.py            ✓ 已注册应用
urls.py                ✓ 已添加路由
```

### ⏳ 需要在 Linux 服务器上执行
```
1. 执行清理脚本
2. 重启服务
3. 验证 API
```

---

## 🚀 快速部署（Linux 服务器）

### 方案 1：自动清理（推荐）
```bash
# 上传脚本到服务器
scp cleanup_database.py user@server:/path/to/wzyoj/

# 执行自动清理
cd /path/to/wzyoj
python3 cleanup_database.py

# 重启服务
sudo systemctl restart wzyoj-backend
```

### 方案 2：手动清理
```bash
cd /path/to/wzyoj/backend

# 备份
pg_dump -U postgres oj | gzip > backup_$(date +%Y%m%d).sql.gz

# 清理数据
python3 manage.py shell << 'EOF'
from oj_course.models import CourseChapter
CourseChapter.objects.all().delete()
EOF

# 迁移
python3 manage.py migrate

# 验证
python3 manage.py shell << 'EOF'
from oj_course.models import CourseChapter
from oj_videocourse.models import VideoCourseChapter
print(f"直播课: {CourseChapter.objects.count()}")
print(f"录播课: {VideoCourseChapter.objects.count()}")
EOF
```

---

## 🔍 API 端点

### 直播课（保持原样）
```
GET    /api/course-chapters/              列表
POST   /api/course-chapters/              创建
GET    /api/course-chapters/{id}/         详情
PUT    /api/course-chapters/{id}/         更新
DELETE /api/course-chapters/{id}/         删除
```

### 录播课（新增）
```
GET    /api/video-courses/                列表
POST   /api/video-courses/                创建
GET    /api/video-courses/{id}/           详情
PUT    /api/video-courses/{id}/           更新
DELETE /api/video-courses/{id}/           删除
POST   /api/video-courses/{id}/join/      加入
POST   /api/video-courses/{id}/leave/     离开
```

---

## 📊 数据库表

### 直播课（course_）
```
✓ course_course
✓ course_coursechapter
✓ course_courseproblem
✓ course_coursestudent
```

### 录播课（videocourse_）
```
✓ videocourse_videocourse
✓ videocourse_videocourseChapter
✓ videocourse_progress
```

---

## 🆘 常见问题速查

| 问题 | 解决 |
|------|------|
| 找不到 oj_videocourse | `grep oj_videocourse settings.py` |
| API 返回 404 | `python3 manage.py showmigrations` |
| 迁移失败 | `python3 manage.py migrate oj_videocourse zero` |
| 数据库仍混乱 | `python3 cleanup_database.py` |
| Celery 报错 | `pkill -f celery; celery -A oj_backend worker` |

---

## 📋 验证清单

部署后检查：

```bash
# ✅ 应用已注册
python3 manage.py shell -c "from django.apps import apps; print('oj_videocourse' in [a.name for a in apps.get_app_configs()])"

# ✅ 表已创建
python3 manage.py shell -c "from oj_videocourse.models import VideoCourse; print('表已创建')"

# ✅ API 可访问
curl http://localhost:8000/api/video-courses/

# ✅ 数据分离
python3 manage.py shell << 'EOF'
from oj_course.models import CourseChapter
from oj_videocourse.models import VideoCourseChapter
assert CourseChapter.objects.count() == 0  # 直播课应为空
print("✓ 数据已分离")
EOF
```

---

## 📁 新增文件

```
backend/
  oj_videocourse/              # 新应用
    __init__.py
    apps.py
    models.py
    views.py
    serializers.py
    urls.py
    admin.py
    tasks.py
    video_processor.py
    migrations/

根目录:
  cleanup_database.py          # 自动清理脚本
  cleanup_database.sh          # Bash 清理脚本
  DATABASE_CLEANUP_GUIDE.md    # 详细指南
  DEPLOYMENT_CHECKLIST.md      # 部署清单
  DATABASE_SEPARATION_CHECKLIST.md
  DATABASE_SEPARATION_CORRECTION.md
```

---

## ⚙️ 配置要点

### settings.py
```python
INSTALLED_APPS = [
    ...
    'oj_videocourse.apps.OjVideocourseConfig',  # ← 新增
    ...
]

VIDEOCOURSE_OUTPUT_ROOT = Path(...)  # ← 新增
```

### urls.py
```python
urlpatterns = [
    ...
    path('videocourse/', include('oj_videocourse.urls')),  # ← 新增
    ...
]
```

---

## 🎯 下一步

1. **上传代码** → 同步 backend 目录到服务器
2. **执行脚本** → 运行 `python3 cleanup_database.py`
3. **重启服务** → `systemctl restart wzyoj-backend`
4. **验证 API** → 测试两个 API 端点
5. **更新前端** → 确保调用正确的端点
6. **监控日志** → 检查错误日志

---

## 💾 重要提醒

- ✅ **直播课完全保持不变** - 无任何影响
- ⚠️ **录播课数据将被清除** - 需重新上传
- 📦 **备份原数据库** - 以防万一
- 🔒 **维护时段执行** - 避免服务中断
- 📝 **保留日志** - 便于排查问题

---

## 📞 参考文档

- 📖 [完整清理指南](./DATABASE_CLEANUP_GUIDE.md)
- ✓ [分离验证清单](./DATABASE_SEPARATION_CHECKLIST.md)
- 🏗️ [架构说明](./DATABASE_SEPARATION_CORRECTION.md)
- 📋 [部署清单](./DEPLOYMENT_CHECKLIST.md)

---

**最后更新**: 2026-01-26  
**状态**: ✅ 就绪部署  
**维护者**: AI Assistant
