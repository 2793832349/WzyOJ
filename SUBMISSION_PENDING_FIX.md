# 修复：提交总是待处理(Pending)状态

## 问题描述
用户提交代码后，提交状态一直显示为 **待处理(Pending)** 状态，不会被评测系统处理和更新。

## 根本原因
**数据库迁移文件缺失** - `oj_user` 等多个应用的 `migrations` 目录下都没有初始迁移文件，这导致了以下问题：

```
ValueError: Dependency on app with no migrations: oj_user
```

当启动后端容器时，Django 在执行数据库迁移时会失败，导致：
1. 数据库初始化不完整
2. 相关表可能没有正确创建
3. 虽然 Celery worker 仍然在运行，但 Celery 任务可能无法正确执行
4. 提交的状态更新任务无法完成

## 解决方案

### 1. 为所有应用生成迁移文件
```bash
cd backend
python3 manage.py makemigrations
```

这将为以下应用创建初始迁移文件：
- `oj_user` (必须有这个)
- `oj_announcement`
- `oj_battle`
- `oj_book`
- `oj_class`
- `oj_contest`
- `oj_course`
- `oj_discussion`
- `oj_live`
- `oj_objective`
- `oj_problem`
- `oj_submission`

### 2. 应用迁移到数据库
```bash
python3 manage.py migrate
```

### 3. 重启所有服务
```bash
docker-compose down
docker-compose up -d
```

或者使用开发脚本：
```bash
./start-dev.sh
# 选择选项 4 或 5 来启动基础服务
```

## 已应用的修复
以下迁移文件已经创建并提交到项目中：
- `backend/oj_user/migrations/0001_initial.py`
- `backend/oj_announcement/migrations/0001_initial.py`
- `backend/oj_battle/migrations/0001_initial.py`
- `backend/oj_book/migrations/0001_initial.py`
- `backend/oj_class/migrations/0001_initial.py`
- `backend/oj_contest/migrations/0001_initial.py`
- `backend/oj_course/migrations/0001_initial.py`
- `backend/oj_discussion/migrations/0001_initial.py`
- `backend/oj_live/migrations/0001_initial.py`
- `backend/oj_objective/migrations/0001_initial.py`
- `backend/oj_problem/migrations/0001_initial.py`
- `backend/oj_submission/migrations/0001_initial.py`

## 工作流程说明
提交处理流程需要以下组件正常工作：

```
用户提交代码
    ↓
Django: 创建 Submission 对象，状态设为 PENDING
    ↓
Celery: 触发 oj_submission.tasks.judge 任务
    ↓
Judge Server: WebSocket 连接，执行代码评测
    ↓
Judger: 编译→运行→比较输出
    ↓
Celery Worker: 接收评测结果，更新 Submission 状态
    ↓
前端: 显示最终评测结果
```

如果数据库迁移失败，整个流程都会受到影响。

## 验证修复
可以通过以下方式验证修复成功：

1. 查看容器日志，确保没有迁移错误：
```bash
docker logs oj-backend | grep -i migration
```

2. 提交代码并观察状态变化：
- 初始状态：Pending (-4)
- 评测中：Judging (-3)
- 最终状态：AC (0), WA (-1), CE (-2), TLE (1), MLE (2), RE (3), SE (4)

3. 检查 Celery worker 日志：
```bash
docker logs oj-backend | grep -i celery
```

## 相关文件
- [提交模型](backend/oj_submission/models.py)
- [提交评测任务](backend/oj_submission/tasks.py)
- [Django 设置](backend/oj_backend/settings.py)
- [Celery 配置](backend/oj_backend/celery.py)

## 预防措施
未来开发时，需要遵循以下规则：

1. **每改动模型就生成迁移**：
   ```bash
   python3 manage.py makemigrations
   ```

2. **提交迁移文件**：
   所有 `*/migrations/000X_*.py` 文件都应该被提交到版本控制中

3. **不要删除迁移文件**：
   即使觉得过时，也应该保留迁移文件的完整历史

4. **在部署前测试迁移**：
   ```bash
   python3 manage.py migrate --plan  # 查看将要执行的迁移
   python3 manage.py migrate --dry-run  # 模拟执行迁移
   ```

---
修复日期: 2026-02-22
修复人: 自动化修复脚本
