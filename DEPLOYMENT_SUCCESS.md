# WzyOJ 部署成功 ✅

## 部署时间
2025-12-21 06:27 UTC

## 部署状态
所有服务已成功部署并运行！

## 服务状态

### 运行中的容器
- ✅ **oj-frontend** (nginx) - 前端服务
- ✅ **oj-backend** (Django) - 后端 API 服务
- ✅ **oj-judge-server** - 代码评测服务器
- ✅ **oj-postgres** - PostgreSQL 数据库
- ✅ **oj-redis** - Redis 缓存
- ✅ **oj-rabbitmq** - RabbitMQ 消息队列

所有容器状态：**健康运行中 (Healthy)**

## 访问信息

### 🌐 前端访问地址
- **URL**: http://localhost:80
- **状态**: ✅ 可访问

### 🔧 后端 API
- **URL**: http://localhost:8080 (容器内部)
- **状态**: ✅ 运行中

### 👤 默认管理员账号
- **用户名**: admin
- **密码**: 123456
- **邮箱**: admin@genuine.og
- **状态**: ✅ 已创建并可用
- ⚠️ **重要**: 生产环境请立即修改默认密码！

## 技术栈

### 后端
- Django 3.2
- Django REST Framework
- PostgreSQL 15
- Redis 6
- RabbitMQ 3
- Celery

### 前端
- Vue 3
- Vite
- NaiveUI
- CodeMirror 6

### 评测服务器
- Python 3.8+
- WebSocket
- Linux seccomp 沙箱

## 常用命令

### 查看服务状态
```bash
cd /root/WzyOJ/deploy
docker compose ps
```

### 查看日志
```bash
# 查看所有服务日志
docker compose logs -f

# 查看特定服务日志
docker logs -f oj-backend
docker logs -f oj-frontend
docker logs -f oj-judge-server
```

### 重启服务
```bash
cd /root/WzyOJ/deploy
docker compose restart
```

### 停止服务
```bash
cd /root/WzyOJ/deploy
docker compose down
```

### 启动服务
```bash
cd /root/WzyOJ/deploy
docker compose up -d
```

## 数据持久化

所有数据存储在 `/root/WzyOJ/deploy/data/` 目录下：
- `backend/` - 后端数据和配置
- `frontend/` - 前端静态文件
- `postgres/` - 数据库数据
- `redis/` - Redis 数据
- `rabbitmq/` - RabbitMQ 数据
- `judge_server/` - 评测服务器运行数据

## 安全建议

⚠️ **生产环境必须执行以下操作**:

1. 修改默认管理员密码
2. 修改 PostgreSQL 密码（在 docker-compose.yml 中）
3. 修改 Django SECRET_KEY（在 `/root/WzyOJ/deploy/data/backend/secret.key`）
4. 配置防火墙规则
5. 启用 HTTPS
6. 定期备份数据库

## 下一步

1. 访问 http://localhost:80 查看系统
2. 使用默认账号登录（admin / 123456）
3. 修改管理员密码
4. 开始使用或二次开发

## 故障排查

如果遇到问题，请查看：
- 服务日志: `docker compose logs`
- 详细文档: `/root/WzyOJ/README.md`
- 开发指南: `/root/WzyOJ/DEVELOPMENT_GUIDE.md`

## 项目位置
- 项目根目录: `/root/WzyOJ/`
- 部署配置: `/root/WzyOJ/deploy/`
- 后端源码: `/root/WzyOJ/backend/`
- 前端源码: `/root/WzyOJ/frontend-naive/`
- 评测服务器: `/root/WzyOJ/judger/`

---

🎉 **部署完成！祝使用愉快！**
