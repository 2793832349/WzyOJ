# 将以下内容添加到 backend/oj_backend/settings.py 的 INSTALLED_APPS 中：

# 在现有的应用列表中添加
INSTALLED_APPS = [
    # ... 其他应用 ...
    'oj_videocourse',  # 新增：独立的录播课应用
    # ... 其他应用 ...
]

# 添加录播课输出目录配置（可选）
VIDEOCOURSE_OUTPUT_ROOT = os.path.join(BASE_DIR, 'judge_data/videocourse_output')

# Celery 任务路由（确保包含录播课任务）
CELERY_TASK_ROUTES = {
    'oj_videocourse.tasks.*': {'queue': 'videocourse'},
}
