# 视频课程模块 - 部署和运维指南

## 生产环境部署

### 1. 系统要求

**硬件需求:**
- CPU: 至少 4 核心（视频转换需要）
- 内存: 至少 8GB
- 存储: 取决于视频数量，建议 500GB+ SSD

**软件依赖:**
- Python 3.8+
- Django 3.2+
- FFmpeg 4.0+
- Redis 5.0+
- Celery 5.0+

### 2. 安装 FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
ffmpeg -version  # 验证安装
```

**CentOS/RHEL:**
```bash
sudo yum install -y ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows (使用 WSL2 或 Docker):**
```dockerfile
FROM python:3.9-slim

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
```

### 3. 配置 Django 设置

**production_settings.py:**
```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# 媒体文件配置
MEDIA_ROOT = '/var/www/oj/media'
MEDIA_URL = '/media/'

# 视频处理配置
VIDEO_CONFIG = {
    'max_size': 5 * 1024 * 1024 * 1024,  # 5GB
    'segment_duration': 10,  # 秒
    'encoding': {
        'video_codec': 'libx264',
        'audio_codec': 'aac',
        'crf': 23,
        'audio_bitrate': '128k'
    },
    'output_format': 'hls',
    'temp_dir': '/var/tmp/video_processing'
}

# Celery 配置
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/1'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Shanghai'

# Celery 任务配置
CELERY_TASK_COMPRESSION = 'gzip'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 3600 * 2  # 2小时
CELERY_TASK_SOFT_TIME_LIMIT = 3600 * 1.5  # 1.5小时

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/oj/video_processing.log',
            'maxBytes': 1024 * 1024 * 100,  # 100MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'celery_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/oj/celery.log',
            'maxBytes': 1024 * 1024 * 100,
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'oj_course': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['celery_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### 4. Docker 部署

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目
COPY . .

# 创建日志目录
RUN mkdir -p /var/log/oj

# 运行迁移和启动
CMD ["gunicorn", "oj_backend.wsgi:application", "--bind", "0.0.0.0:8000"]
```

**docker-compose.yml (补充):**
```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: oj
      POSTGRES_USER: oj
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  web:
    build: .
    command: gunicorn oj_backend.wsgi:application --bind 0.0.0.0:8000
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - OJ_MODE=PRODUCTION
      - OJ_REDIS_HOST=redis
      - OJ_SQL_HOST=db
    volumes:
      - ./media:/app/media
      - ./logs:/var/log/oj

  celery:
    build: .
    command: celery -A oj_backend worker -l info --concurrency=4
    depends_on:
      - db
      - redis
    environment:
      - OJ_MODE=PRODUCTION
      - OJ_REDIS_HOST=redis
      - OJ_SQL_HOST=db
    volumes:
      - ./media:/app/media
      - ./logs:/var/log/oj

  celery_beat:
    build: .
    command: celery -A oj_backend beat -l info
    depends_on:
      - redis
    environment:
      - OJ_REDIS_HOST=redis
    volumes:
      - ./logs:/var/log/oj

volumes:
  postgres_data:
  redis_data:
```

### 5. Nginx 配置

**nginx.conf:**
```nginx
upstream oj_backend {
    server web:8000;
}

server {
    listen 80;
    server_name example.com;
    client_max_body_size 5G;  # 允许 5GB 上传

    # 媒体文件缓存
    location /media/ {
        alias /var/www/oj/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 静态文件缓存
    location /static/ {
        alias /var/www/oj/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # API 代理
    location / {
        proxy_pass http://oj_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;  # 上传超时
    }

    # WebSocket 支持（如果有）
    location /ws/ {
        proxy_pass http://oj_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
```

## 运维指南

### 1. 监控

**监控关键指标:**
- Celery 任务队列长度
- 视频处理成功率
- 平均处理时间
- 磁盘空间使用率
- 视频转换耗时

**监控脚本:**
```python
# monitoring.py
import os
import psutil
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta
from oj_course.models import CourseChapter, VideoProcessingStatus

def get_monitoring_stats():
    """获取监控统计数据"""
    
    # 磁盘空间
    disk_usage = psutil.disk_usage('/var/www/oj/media')
    
    # 视频处理统计
    one_hour_ago = timezone.now() - timedelta(hours=1)
    
    stats = {
        'disk': {
            'total_gb': disk_usage.total / (1024**3),
            'used_gb': disk_usage.used / (1024**3),
            'free_gb': disk_usage.free / (1024**3),
            'percent': disk_usage.percent
        },
        'video_processing': {
            'pending': CourseChapter.objects.filter(
                video_status=VideoProcessingStatus.PENDING
            ).count(),
            'processing': CourseChapter.objects.filter(
                video_status=VideoProcessingStatus.PROCESSING
            ).count(),
            'completed': CourseChapter.objects.filter(
                video_status=VideoProcessingStatus.COMPLETED
            ).count(),
            'failed': CourseChapter.objects.filter(
                video_status=VideoProcessingStatus.FAILED
            ).count(),
        },
        'recent_failures': CourseChapter.objects.filter(
            video_status=VideoProcessingStatus.FAILED,
            updated_at__gte=one_hour_ago
        ).values('id', 'error_message')
    }
    
    return stats

# 定期运行（cron）
# 每小时检查一次
# 0 * * * * python manage.py shell < monitoring.py
```

### 2. 日志管理

**查看日志:**
```bash
# 实时日志
tail -f /var/log/oj/video_processing.log

# 查看最近 100 行
tail -100 /var/log/oj/video_processing.log

# 搜索错误
grep "ERROR" /var/log/oj/video_processing.log

# 查看特定日期的日志
grep "2024-01-15" /var/log/oj/video_processing.log
```

**日志轮转配置 (logrotate):**
```
/var/log/oj/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload nginx > /dev/null 2>&1 || true
    endscript
}
```

### 3. 数据库维护

**清理失败的任务:**
```python
from oj_course.models import CourseChapter, VideoProcessingStatus
from django.utils import timezone
from datetime import timedelta

# 删除 7 天前失败的处理记录
seven_days_ago = timezone.now() - timedelta(days=7)
CourseChapter.objects.filter(
    video_status=VideoProcessingStatus.FAILED,
    updated_at__lt=seven_days_ago
).delete()
```

**数据库备份:**
```bash
# PostgreSQL 备份
pg_dump -U oj -h localhost oj > /backup/oj_$(date +%Y%m%d_%H%M%S).sql

# 压缩备份
tar -czf /backup/oj_media_$(date +%Y%m%d).tar.gz /var/www/oj/media/

# 定期备份（cron）
# 每天 2 点备份
0 2 * * * pg_dump -U oj -h localhost oj | gzip > /backup/oj_$(date +\%Y\%m\%d).sql.gz
```

### 4. 性能优化

**启用 CDN:**
```nginx
# 在 Nginx 配置中添加 CDN 后端
upstream cdn {
    server cdn.example.com;
}

location /media/ {
    # 如果本地有缓存，直接返回
    try_files $uri @cdn;
    expires 30d;
}

location @cdn {
    proxy_pass http://cdn;
    add_header X-Cache-Status "MISS";
}
```

**视频预转换:**
```python
# 预先转换热点课程视频
from oj_course.models import CourseChapter
from oj_course.video_processor import VideoProcessor

# 找出观看次数最多的章节
popular_chapters = CourseChapter.objects.filter(
    video_status='pending'
).order_by('-enrollments__count')[:10]

for chapter in popular_chapters:
    processor = VideoProcessor(chapter)
    processor.process()
```

### 5. 故障恢复

**检查 Celery 队列:**
```bash
# 进入 Redis CLI
redis-cli

# 检查队列
LLEN celery

# 清空队列（谨慎使用）
DEL celery

# 检查 worker 状态
celery -A oj_backend inspect active
celery -A oj_backend inspect stats
```

**重新启动 Celery worker:**
```bash
# 优雅关闭
celery -A oj_backend control shutdown

# 启动新 worker
celery -A oj_backend worker -l info --concurrency=4
```

**清理临时文件:**
```bash
# 定期清理临时目录
find /var/tmp/video_processing -type f -mtime +7 -delete

# 添加到 cron（每天运行）
0 0 * * * find /var/tmp/video_processing -type f -mtime +7 -delete
```

### 6. 容量规划

**计算存储需求:**
```
视频大小 = 原始视频大小 × 1.2（HLS 转换后通常比原文件大）

例如：
- 1小时高清视频（720p）：约 500MB
- 转换后 HLS：约 600MB
- 保存原始文件：500MB
- 单个视频总占用：约 1.1GB
```

**Celery worker 并发数建议:**
```
并发数 = CPU核心数 - 1

例如：
- 4 核 CPU → 3 个 worker
- 8 核 CPU → 7 个 worker

可调整命令：
celery -A oj_backend worker -l info --concurrency=7
```

## 故障排查

### 问题 1: 视频转换一直失败

**诊断:**
```bash
# 查看错误日志
grep "failed" /var/log/oj/video_processing.log

# 检查 Celery worker 日志
tail -100 /var/log/oj/celery.log

# 验证 FFmpeg
which ffmpeg
ffmpeg -version
```

**解决:**
```bash
# 重新安装 FFmpeg
sudo apt-get install --reinstall ffmpeg

# 检查磁盘空间
df -h /var/tmp/

# 检查用户权限
chmod 755 /var/tmp/video_processing
chown www-data:www-data /var/tmp/video_processing
```

### 问题 2: 转换很慢

**优化方案:**
```python
# 调整编码参数（settings.py）
VIDEO_CONFIG = {
    'encoding': {
        'crf': 28,  # 降低质量（更快）
        'preset': 'faster'  # 加快转换速度
    }
}
```

```bash
# 增加 worker 数量
celery -A oj_backend worker -l info --concurrency=8

# 启用多线程
ffmpeg -i input.mp4 -threads 4 ...
```

### 问题 3: Redis 连接失败

```bash
# 检查 Redis 状态
redis-cli ping

# 检查 Redis 日志
tail -f /var/log/redis/redis-server.log

# 重启 Redis
sudo systemctl restart redis-server

# 检查连接
redis-cli info stats
```

## 扩展部署

### 1. 水平扩展

**多个 Celery worker:**
```bash
# worker1
celery -A oj_backend worker -l info --concurrency=4 -n worker1@%h

# worker2
celery -A oj_backend worker -l info --concurrency=4 -n worker2@%h

# worker3
celery -A oj_backend worker -l info --concurrency=4 -n worker3@%h
```

### 2. 分布式存储

**使用 S3/MinIO 存储视频:**
```python
# settings.py
USE_S3 = os.getenv('USE_S3', False)

if USE_S3:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_STORAGE_BUCKET_NAME = 'oj-videos'
    AWS_S3_ENDPOINT_URL = 'https://s3.amazonaws.com'
```

### 3. 流媒体分发

**配置 CDN 加速:**
```
原始文件 → 服务器 → CDN 边缘节点 → 用户
```

## 定期维护任务

| 任务 | 频率 | 命令/脚本 |
|------|------|---------|
| 清理临时文件 | 每天 | `find /var/tmp/video_processing -mtime +7 -delete` |
| 数据库备份 | 每天 | `pg_dump ... \| gzip > backup.sql.gz` |
| 日志轮转 | 自动 | logrotate 配置 |
| 检查磁盘空间 | 每小时 | monitoring.py |
| 清理旧视频 | 每周 | 数据库清理脚本 |
| 更新 FFmpeg | 按需 | `apt-get update && apt-get upgrade ffmpeg` |

