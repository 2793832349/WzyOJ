# WZY OJ 开发环境

## 🎯 项目状态

✅ **已完成部署和源码下载**

所有组件已成功部署并运行在 Docker 容器中，同时源代码已下载到本地供二次开发使用。

---

## 📂 目录结构

```
/root/
├── backend/              # 后端源码 (Django + Python)
├── frontend-naive/       # 前端源码 (Vue3 + NaiveUI)
├── judger/              # 评测服务器源码 (Python)
├── deploy/              # Docker 部署配置
├── DEVELOPMENT_GUIDE.md # 详细开发指南 ⭐
├── PROJECT_OVERVIEW.md  # 项目概览和架构说明 ⭐
├── start-dev.sh         # 快速启动脚本 ⭐
└── README.md           # 本文件
```

---

## 🚀 快速开始

### 方式 1: 使用快速启动脚本（推荐）
```bash
/root/start-dev.sh
```

这个脚本提供了交互式菜单，可以选择不同的开发模式：
- 完整 Docker 环境
- 本地后端开发
- 本地前端开发
- 本地前后端开发
- 仅基础服务

### 方式 2: 手动启动

#### 查看当前运行的服务
```bash
cd /root/deploy
docker-compose ps
```

#### 停止所有服务
```bash
cd /root/deploy
docker-compose down
```

#### 启动所有服务
```bash
cd /root/deploy
docker-compose up -d
```

#### 启动基础服务（用于本地开发）
```bash
cd /root/deploy
docker-compose up -d postgres redis rabbitmq
```

---

## 🌐 访问地址

### 生产环境（Docker）
- **前端**: http://localhost:80
- **后端 API**: http://localhost:8080
- **管理员账号**: admin / 123456

### 开发环境（本地）
- **前端开发服务器**: http://localhost:3000 (或 Vite 指定的端口)
- **后端开发服务器**: http://localhost:8080

---

## 📖 文档导航

### 🔰 新手必读
1. **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - 了解项目架构和各模块功能
2. **[DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)** - 详细的开发环境设置和工作流

### 📚 各项目文档
- **后端**: `/root/backend/README.md`
- **前端**: `/root/frontend-naive/README.md`
- **评测服务器**: `/root/judger/README.md`
- **部署**: `/root/deploy/README.md`

---

## 🛠️ 常用命令

### Docker 相关
```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker logs -f oj-backend
docker logs -f oj-frontend
docker logs -f oj-judge-server

# 重启服务
docker-compose restart

# 停止服务
docker-compose stop

# 启动服务
docker-compose start

# 完全删除（包括数据）
docker-compose down -v
```

### 后端开发
```bash
cd /root/backend

# 安装依赖
pip3 install -r requirements.txt

# 数据库迁移
python3 manage.py makemigrations
python3 manage.py migrate

# 创建超级用户
python3 manage.py createsuperuser

# 启动开发服务器
python3 manage.py runserver 0.0.0.0:8080

# 启动 Celery（另开终端）
celery -A oj_backend worker -l info
```

### 前端开发
```bash
cd /root/frontend-naive

# 安装依赖
yarn install

# 启动开发服务器
yarn dev

# 构建生产版本
yarn build
```

### 评测服务器
```bash
cd /root/judger

# 安装依赖
sudo pip3 install -r requirements.txt

# 部署
sudo ./deploy.sh

# 启动服务器
sudo python3 server.py
```

---

## 🔧 开发模式选择

### 模式 1: 完全 Docker（生产模式）
适合：测试完整部署流程

```bash
cd /root/deploy
docker-compose up -d
```

### 模式 2: 混合开发（推荐）
适合：日常开发，快速看到修改效果

```bash
# 启动基础服务
cd /root/deploy
docker-compose up -d postgres redis rabbitmq

# 本地运行后端
cd /root/backend
python3 manage.py runserver 0.0.0.0:8080

# 本地运行前端
cd /root/frontend-naive
yarn dev
```

### 模式 3: 完全本地
适合：需要深度调试所有组件

需要在本机安装：PostgreSQL, Redis, RabbitMQ

---

## 🎨 技术栈

### 后端
- **框架**: Django 3.2
- **API**: Django REST Framework
- **数据库**: PostgreSQL
- **缓存**: Redis
- **消息队列**: RabbitMQ + Celery
- **WebSocket**: Django Channels

### 前端
- **框架**: Vue 3
- **构建工具**: Vite
- **UI 库**: NaiveUI
- **代码编辑器**: CodeMirror 6
- **Markdown**: md-editor-v3
- **状态管理**: Vuex
- **路由**: Vue Router

### 评测服务器
- **语言**: Python 3.8+
- **通信**: WebSocket
- **沙箱**: Linux seccomp

---

## 📊 系统架构

```
用户浏览器
    ↓
Nginx (前端静态文件)
    ↓
Django (后端 API)
    ↓
PostgreSQL (数据存储)
Redis (缓存)
RabbitMQ (消息队列)
    ↓
Judge Server (代码评测)
```

---

## 🐛 故障排查

### 服务无法启动
```bash
# 查看日志
docker logs oj-backend
docker logs oj-frontend

# 检查端口占用
netstat -tlnp | grep 80
netstat -tlnp | grep 8080
```

### 数据库连接失败
```bash
# 检查 PostgreSQL 是否运行
docker ps | grep postgres

# 进入数据库容器
docker exec -it oj-postgres psql -U onlinejudge
```

### 前端无法连接后端
检查前端配置中的 API 地址是否正确

### 评测服务器无法工作
检查后端配置中的 `OJ_JUDGE_HOST` 设置

---

## 📝 开发建议

1. **版本控制**: 为你的修改创建 Git 分支
2. **代码规范**: 遵循项目现有风格
3. **测试**: 充分测试后再提交
4. **文档**: 为新功能编写文档
5. **备份**: 定期备份数据库

---

## 🔐 安全提示

⚠️ **生产环境必须修改**:
- 修改默认管理员密码
- 修改 PostgreSQL 密码
- 修改 Django SECRET_KEY
- 配置防火墙规则
- 启用 HTTPS

---

## 📞 获取帮助

- 查看详细文档: `DEVELOPMENT_GUIDE.md`
- 查看项目概览: `PROJECT_OVERVIEW.md`

---

## 🎉 开始开发

现在你可以开始二次开发了！

**推荐流程**:
1. 阅读 `PROJECT_OVERVIEW.md` 了解系统架构
2. 阅读 `DEVELOPMENT_GUIDE.md` 设置开发环境
3. 运行 `/root/start-dev.sh` 启动开发环境
4. 开始编码！

祝开发顺利！🚀
