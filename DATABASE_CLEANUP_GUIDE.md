# 🔧 数据库清理恢复指南

## 现状分析

当前问题：
- ❌ 旧数据库中 `course_coursechapter` 表混合了直播课和录播课数据
- ❌ `/api/course-chapters/` 端点同时提供直播课和录播课数据
- ❌ 前端无法区分两种课程类型
- ✅ 新的 `oj_videocourse` 应用已创建，等待配置

## 解决方案：数据库清理方案

### 方案 A：快速清理（推荐生产环境）

#### 步骤 1：备份旧数据
```bash
# 在 Linux 服务器上执行
cd /path/to/backend

# PostgreSQL 备份
pg_dump -U postgres -h localhost oj > oj_backup_$(date +%Y%m%d_%H%M%S).sql

# SQLite 备份
cp db.sqlite3 db.sqlite3.backup_$(date +%Y%m%d_%H%M%S)
```

#### 步骤 2：在 Django Shell 中清理数据

```bash
cd /path/to/backend
python manage.py shell
```

在 Django Shell 中执行：

```python
from oj_course.models import CourseChapter

# 方案 1：删除所有 CourseChapter（清除混乱数据）
# 💡 只有当你确认数据可以重新上传时使用
CourseChapter.objects.all().delete()

# 方案 2：只保留需要的直播课数据
# 找出需要保留的课程 ID（假设 ID 为 1, 2, 3）
keep_course_ids = [1, 2, 3]  # 修改为你要保留的课程 ID
CourseChapter.objects.exclude(course_id__in=keep_course_ids).delete()

# 验证
print(f"保留的 CourseChapter 数量: {CourseChapter.objects.count()}")
print(f"课程分布:")
for course_id in CourseChapter.objects.values('course_id').distinct():
    count = CourseChapter.objects.filter(course_id=course_id['course_id']).count()
    print(f"  课程 {course_id['course_id']}: {count} 个章节")
```

#### 步骤 3：执行新迁移

```bash
# 注册新应用
# 确保 settings.py 已更新（添加 'oj_videocourse.apps.OjVideocourseConfig'）

# 执行迁移
python manage.py migrate oj_videocourse

# 验证迁移
python manage.py showmigrations oj_videocourse
```

#### 步骤 4：创建输出目录

```bash
mkdir -p judge_data/videocourse_output
chmod 755 judge_data/videocourse_output
```

---

### 方案 B：完整重置（开发环境）

如果是开发环境且可以完全重置：

#### SQLite 数据库
```bash
cd /path/to/backend

# 删除旧数据库
rm -f db.sqlite3

# 删除所有迁移（保留 __init__.py）
find . -path "*/migrations/*.py" ! -name "__init__.py" -delete
find . -path "*/migrations/__pycache__" -type d -exec rm -rf {} + 2>/dev/null

# 创建新迁移
python manage.py makemigrations

# 执行迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser
```

#### PostgreSQL 数据库
```bash
# 连接到 PostgreSQL
psql -U postgres -h localhost

# 删除旧数据库
DROP DATABASE IF EXISTS oj;

# 创建新数据库
CREATE DATABASE oj OWNER postgres;

# 退出
\q

# 执行迁移
cd /path/to/backend
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser
```

---

### 方案 C：数据迁移脚本（如果需要保留数据）

创建文件：`backend/oj_course/migrations/0xxx_separate_courses.py`

```python
from django.db import migrations
from django.utils import timezone

def separate_courses(apps, schema_editor):
    """
    将混乱的 CourseChapter 分离为直播课和录播课
    
    假设直播课课程 ID: 1-100
    假设录播课课程 ID: 101+
    """
    CourseChapter = apps.get_model('oj_course', 'CourseChapter')
    
    # 获取所有章节
    chapters = CourseChapter.objects.all()
    
    recorded_chapters = []
    
    for chapter in chapters:
        # 判断是录播课还是直播课（按课程 ID 区分）
        if chapter.course_id > 100:  # 假设 101+ 是录播课
            recorded_chapters.append(chapter)
    
    # 删除录播课数据
    for chapter in recorded_chapters:
        chapter.delete()
    
    print(f"删除了 {len(recorded_chapters)} 个录播课章节")

def reverse_separate(apps, schema_editor):
    """反向操作（如果需要回滚）"""
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('oj_course', '0xxx_previous_migration'),
    ]
    
    operations = [
        migrations.RunPython(separate_courses, reverse_separate),
    ]
```

执行：
```bash
python manage.py migrate oj_course
```

---

## 完整恢复流程（Linux 服务器）

### 1️⃣ 首次配置 oj_videocourse

```bash
cd /path/to/backend

# 确保 settings.py 已更新
# 检查：grep "oj_videocourse" oj_backend/settings.py

# 确保 urls.py 已更新
# 检查：grep "oj_videocourse" oj_backend/urls.py
```

### 2️⃣ 备份现有数据

```bash
# PostgreSQL
pg_dump -U postgres -h localhost oj | gzip > oj_backup_$(date +%Y%m%d).sql.gz

# SQLite
cp db.sqlite3 db.sqlite3.backup_$(date +%Y%m%d)
```

### 3️⃣ 清理混乱数据

```bash
python manage.py shell << 'EOF'
from oj_course.models import CourseChapter

# 查看当前数据
print("清理前的数据:")
print(f"总 CourseChapter 数: {CourseChapter.objects.count()}")

# 删除所有 CourseChapter（因为它们是混乱的）
CourseChapter.objects.all().delete()

print("清理后的数据:")
print(f"总 CourseChapter 数: {CourseChapter.objects.count()}")
EOF
```

### 4️⃣ 执行新迁移

```bash
# 创建 oj_videocourse 迁移（如果尚未创建）
python manage.py makemigrations oj_videocourse

# 执行迁移
python manage.py migrate oj_videocourse

# 验证
python manage.py showmigrations | grep -A 5 "oj_videocourse"
```

### 5️⃣ 验证数据库分离

```bash
python manage.py shell << 'EOF'
from django.db import connection

cursor = connection.cursor()

# 检查直播课表
print("=== 直播课数据库表 ===")
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema='public' AND table_name LIKE 'course_%'
""")
for row in cursor.fetchall():
    print(f"  ✓ {row[0]}")

# 检查录播课表
print("\n=== 录播课数据库表 ===")
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema='public' AND table_name LIKE 'videocourse_%'
""")
for row in cursor.fetchall():
    print(f"  ✓ {row[0]}")

# 统计数据
from oj_course.models import Course, CourseChapter
from oj_videocourse.models import VideoCourse, VideoCourseChapter

print(f"\n=== 数据统计 ===")
print(f"直播课数: {Course.objects.count()}")
print(f"直播课章节数: {CourseChapter.objects.count()}")
print(f"录播课数: {VideoCourse.objects.count()}")
print(f"录播课章节数: {VideoCourseChapter.objects.count()}")
EOF
```

### 6️⃣ 创建输出目录

```bash
mkdir -p judge_data/videocourse_output
chmod 755 judge_data/videocourse_output
```

### 7️⃣ 重启服务

```bash
# 如果使用 systemd
sudo systemctl restart wzyoj-backend

# 如果使用 gunicorn
pkill -f "gunicorn.*oj_backend"
nohup gunicorn oj_backend.wsgi:application --bind 0.0.0.0:8000 > backend.log 2>&1 &

# 如果使用 Docker
docker-compose restart backend

# 如果使用开发服务器
python manage.py runserver 0.0.0.0:8000
```

### 8️⃣ 验证 API

```bash
# 检查直播课 API
curl -X GET http://localhost:8000/api/course-chapters/

# 检查录播课 API
curl -X GET http://localhost:8000/api/video-courses/

# 都应该返回正确的 JSON 响应
```

---

## 常见问题排查

### ❌ 错误：找不到表 `videocourse_videocourse`

```bash
# 解决：执行迁移
python manage.py migrate oj_videocourse
```

### ❌ 错误：`oj_videocourse` 不在 INSTALLED_APPS

```bash
# 解决：编辑 settings.py
# 在 LOCAL_APPS 中添加：
# 'oj_videocourse.apps.OjVideocourseConfig',
```

### ❌ 错误：API 路由冲突

```bash
# 检查 urls.py 中是否有重复的路由
grep -n "videocourse" oj_backend/urls.py
grep -n "course" oj_backend/urls.py

# 应该看到：
# path('course/', include('oj_course.urls')),
# path('videocourse/', include('oj_videocourse.urls')),
```

### ❌ 数据库仍然混乱

```bash
# 详细检查
python manage.py shell << 'EOF'
from oj_course.models import CourseChapter
from oj_videocourse.models import VideoCourseChapter

print("直播课 CourseChapter 数:", CourseChapter.objects.count())
print("录播课 VideoCourseChapter 数:", VideoCourseChapter.objects.count())

# 列出所有直播课章节
print("\n直播课章节:")
for ch in CourseChapter.objects.all()[:5]:
    print(f"  ID {ch.id}: {ch.name} (课程 {ch.course_id})")

# 列出所有录播课章节
print("\n录播课章节:")
for ch in VideoCourseChapter.objects.all()[:5]:
    print(f"  ID {ch.id}: {ch.name} (课程 {ch.video_course_id})")
EOF
```

---

## 安全建议

### ✅ 生产环境清理步骤

1. **备份备份备份** 三个备份副本
   ```bash
   pg_dump oj | gzip > backup_20260126_v1.sql.gz
   pg_dump oj | gzip > backup_20260126_v2.sql.gz
   pg_dump oj | gzip > backup_20260126_v3.sql.gz
   ```

2. **在从库测试** 先在测试数据库上执行清理

3. **制定回滚计划** 如出问题可立即回滚
   ```bash
   # 回滚命令
   dropdb oj
   createdb oj
   zcat backup_20260126_v1.sql.gz | psql oj
   ```

4. **维护时段执行** 在业务低谷时执行

5. **监控执行过程** 留意错误日志
   ```bash
   tail -f /var/log/postgresql/postgresql.log
   tail -f backend.log
   ```

---

## 总结

| 情景 | 推荐方案 |
|------|--------|
| 生产环境，需要保留历史数据 | 方案 A：快速清理 |
| 开发环境，可以完全重置 | 方案 B：完整重置 |
| 需要精细控制数据分离 | 方案 C：迁移脚本 |

选择方案后，按照"完整恢复流程"执行即可！
