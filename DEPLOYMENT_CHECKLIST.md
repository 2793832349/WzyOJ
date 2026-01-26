# ✅ 数据库分离部署清单

## 📋 部署前检查清单

### ✅ 代码准备完成
- [x] 创建 `oj_videocourse` Django 应用
- [x] 创建独立的数据库模型
- [x] 创建独立的 API 端点
- [x] 创建独立的序列化器和视图
- [x] 创建独立的 Celery 任务
- [x] 创建独立的视频处理器
- [x] 创建迁移文件

### ⚠️ 配置更新完成
- [x] `settings.py` - 已添加 `'oj_videocourse.apps.OjVideocourseConfig'`
- [x] `settings.py` - 已添加 `VIDEOCOURSE_OUTPUT_ROOT` 配置
- [x] `urls.py` - 已添加 `path('videocourse/', include('oj_videocourse.urls'))`

### 🗑️ 数据库清理脚本
- [x] `cleanup_database.sh` - Bash 脚本（Linux/Mac）
- [x] `cleanup_database.py` - Python 脚本（跨平台）
- [x] `DATABASE_CLEANUP_GUIDE.md` - 完整指南

---

## 🚀 Linux 服务器部署步骤

### 第一步：同步代码到服务器

```bash
# 在本地
cd d:\Users\why\Downloads\WzyOJ

# 上传到 Linux 服务器
scp -r backend user@server:/path/to/wzyoj/
scp cleanup_database.py user@server:/path/to/wzyoj/
scp cleanup_database.sh user@server:/path/to/wzyoj/
scp DATABASE_CLEANUP_GUIDE.md user@server:/path/to/wzyoj/
```

或使用 Git：

```bash
# 本地
git add -A
git commit -m "feat: 分离直播课和录播课数据库"
git push

# 服务器
cd /path/to/wzyoj
git pull
```

### 第二步：执行清理脚本

```bash
# 连接到 Linux 服务器
ssh user@server

# 进入项目目录
cd /path/to/wzyoj

# 方案 1: 使用 Python 脚本（推荐，跨平台）
python3 cleanup_database.py

# 方案 2: 使用 Bash 脚本（仅 Linux/Mac）
bash cleanup_database.sh all

# 或分步执行
bash cleanup_database.sh backup    # 备份
bash cleanup_database.sh clean     # 清理
bash cleanup_database.sh migrate   # 迁移
bash cleanup_database.sh verify    # 验证
```

### 第三步：验证部署

```bash
cd /path/to/wzyoj/backend

# 检查数据库状态
python3 manage.py shell << 'EOF'
from oj_course.models import CourseChapter
from oj_videocourse.models import VideoCourseChapter

print("直播课 CourseChapter:", CourseChapter.objects.count())
print("录播课 VideoCourseChapter:", VideoCourseChapter.objects.count())
EOF

# 测试 API
curl -X GET http://localhost:8000/api/course-chapters/
curl -X GET http://localhost:8000/api/video-courses/
```

### 第四步：重启服务

```bash
# 如果使用 systemd
sudo systemctl restart wzyoj-backend

# 如果使用 Gunicorn
pkill -f "gunicorn.*oj_backend"
nohup gunicorn oj_backend.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  > /tmp/wzyoj-backend.log 2>&1 &

# 如果使用 Docker
docker-compose restart backend

# 如果使用开发服务器
python3 manage.py runserver 0.0.0.0:8000
```

### 第五步：监控日志

```bash
# 查看 Django 日志
tail -f /var/log/wzyoj/django.log

# 查看 Gunicorn 日志
tail -f /tmp/wzyoj-backend.log

# 查看 PostgreSQL 日志
sudo tail -f /var/log/postgresql/postgresql.log

# 查看 Celery 日志
tail -f /var/log/wzyoj/celery.log
```

---

## 🐛 故障排查

### 问题 1：找不到 oj_videocourse 模块

**原因**：Django 未识别新应用

**解决**：
```bash
# 确认 settings.py 已更新
grep "oj_videocourse" backend/oj_backend/settings.py

# 输出应该是：
# 'oj_videocourse.apps.OjVideocourseConfig',
```

### 问题 2：迁移失败 - "表已存在"

**原因**：数据库中已有旧的表

**解决**：
```bash
cd backend

# 查看迁移历史
python3 manage.py showmigrations oj_videocourse

# 如果需要重置
python3 manage.py migrate oj_videocourse zero  # 回滚
python3 manage.py migrate oj_videocourse       # 重新应用
```

### 问题 3：API 返回 404

**原因**：URL 路由未正确配置

**解决**：
```bash
# 检查 URLs 配置
grep -n "videocourse" backend/oj_backend/urls.py

# 应该看到：
# path('videocourse/', include('oj_videocourse.urls')),

# 测试路由
python3 manage.py shell << 'EOF'
from django.urls import get_resolver
urls = get_resolver().url_patterns
for pattern in urls:
    if 'video' in str(pattern):
        print(pattern)
EOF
```

### 问题 4：权限错误

**原因**：输出目录权限不足

**解决**：
```bash
# 检查权限
ls -la backend/judge_data/

# 修改权限
sudo chown -R www-data:www-data backend/judge_data/
chmod 755 backend/judge_data/videocourse_output
```

### 问题 5：Celery 任务失败

**原因**：Celery worker 未重启

**解决**：
```bash
# 杀死旧 worker
pkill -f "celery.*oj_backend"

# 启动新 worker
celery -A oj_backend worker --loglevel=info

# 或使用 Celery Beat
celery -A oj_backend beat --loglevel=info
```

---

## 📊 部署后验证

### 检查清单

```bash
cd backend

# ✅ 1. 检查应用注册
python3 manage.py shell << 'EOF'
from django.apps import apps
app = apps.get_app_config('oj_videocourse')
print(f"✓ oj_videocourse 应用已注册: {app.name}")
EOF

# ✅ 2. 检查数据库表
python3 manage.py shell << 'EOF'
from django.db import connection
tables = connection.introspection.table_names()
video_tables = [t for t in tables if 'videocourse' in t]
course_tables = [t for t in tables if 'course_' in t]
print(f"✓ 录播课表: {video_tables}")
print(f"✓ 直播课表: {course_tables}")
EOF

# ✅ 3. 检查 API 可访问性
curl -s http://localhost:8000/api/video-courses/ | python3 -m json.tool | head -20

# ✅ 4. 检查 Admin 后台
curl -s http://localhost:8000/admin/ | grep "videocourse"

# ✅ 5. 检查日志无错误
python3 manage.py runserver 0.0.0.0:8000 --nothreading &
sleep 5
curl -s http://localhost:8000/api/video-courses/
pkill -f "runserver"
```

---

## 📝 部署完成后

### 确认事项

- [ ] 数据库成功迁移
- [ ] API 端点正常工作
- [ ] 直播课数据保持不变
- [ ] 录播课系统独立运行
- [ ] 没有错误日志
- [ ] 性能无异常

### 通知相关人员

```markdown
## 📢 更新通知

### 数据库架构已更新

#### 变更内容
- 直播课（直播课堂）：保持原样，无任何更改
- 录播课（视频课程）：现在使用独立的数据库、API 和系统

#### 用户影响
- 直播课用户：无影响
- 录播课用户：数据已重置，需要重新上传视频

#### API 端点
- 直播课：/api/course-chapters/
- 录播课：/api/video-courses/（新）

#### 后续计划
- 日期：[填写]
- 迁移历史数据（如需要）
- 更新前端代码
```

---

## 🆘 紧急回滚方案

如果部署失败需要回滚：

```bash
cd /path/to/backend

# 1. 停止服务
sudo systemctl stop wzyoj-backend

# 2. 恢复备份
# PostgreSQL
psql -U postgres -h localhost < oj_backup_20260126.sql

# SQLite
cp db.sqlite3.backup_20260126 db.sqlite3

# 3. 移除新应用
# 编辑 settings.py，删除 'oj_videocourse.apps.OjVideocourseConfig'
# 编辑 urls.py，删除 path('videocourse/', include('oj_videocourse.urls'))

# 4. 重启服务
sudo systemctl start wzyoj-backend

# 5. 验证
curl -s http://localhost:8000/api/course-chapters/ | python3 -m json.tool | head -10
```

---

## 📞 支持

如遇到问题，参考：
- [DATABASE_CLEANUP_GUIDE.md](./DATABASE_CLEANUP_GUIDE.md) - 详细清理指南
- [DATABASE_SEPARATION_CHECKLIST.md](./DATABASE_SEPARATION_CHECKLIST.md) - 分离验证清单
- [DATABASE_SEPARATION_CORRECTION.md](./DATABASE_SEPARATION_CORRECTION.md) - 架构说明

---

## ✅ 部署完成标志

当你看到以下消息时，部署完成：

```
==== 所有步骤完成！ ====

数据库现在已：
  ✓ 备份到文件
  ✓ 清理混乱数据
  ✓ 创建 oj_videocourse 表
  ✓ 直播课和录播课完全分离

下一步：重启服务并测试 API
```

🎉 **恭喜！数据库分离部署完成！**
