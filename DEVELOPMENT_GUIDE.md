# Genuine OJ 二次开发指南

## 📁 项目结构

```
/root/
├── backend/           # 后端代码 (Django + Python)
├── frontend-naive/    # 前端代码 (Vue3 + NaiveUI)
├── judger/           # 评测服务器代码 (Python)
└── deploy/           # Docker 部署配置
```

## 🚀 开发环境设置

### 1. 后端开发 (Backend)

#### 环境要求
- Python ≥ 3.7
- Redis
- RabbitMQ
- PostgreSQL

#### 安装依赖
```bash
cd /root/backend
pip3 install -r requirements.txt
```

#### 配置数据库
创建 `config.py` 文件（可参考 `/root/deploy/config/backend-config.py`）：
```python
# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'onlinejudge',
        'USER': 'onlinejudge',
        'PASSWORD': 'onlinejudge',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Redis 配置
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

# RabbitMQ 配置
MQ_HOST = 'localhost'
MQ_PORT = 5672
```

#### 初始化数据库
```bash
# 生成密钥
echo $(python3 -c "from django.core.management import utils;print(utils.get_random_secret_key())") > secret.key

# 数据库迁移
python3 manage.py makemigrations oj_user
python3 manage.py migrate
python3 manage.py makemigrations oj_problem oj_submission oj_contest oj_discussion
python3 manage.py migrate

# 创建超级用户
python3 manage.py createsuperuser
```

#### 启动开发服务器
```bash
# 启动 Django 开发服务器
python3 manage.py runserver 0.0.0.0:8080

# 另开一个终端，启动 Celery 任务队列
celery -A oj_backend worker -l info
```

#### 后端目录结构
```
backend/
├── oj_contest/        # 比赛模块
├── oj_problem/        # 题目模块
├── oj_submission/     # 提交和评测模块
├── oj_user/          # 用户管理模块
├── oj_discussion/    # 讨论模块
├── oj_backend/       # 主配置
├── media/            # 媒体文件
└── judge_data/       # 评测数据
    ├── spj/          # 特殊评测程序
    ├── test_data/    # 测试数据
    └── submission/   # 用户提交输出
```

#### API 文档
- [API Fox 文档](https://genuine-oj.apifox.cn/)

---

### 2. 前端开发 (Frontend)

#### 环境要求
- Node.js ≥ 16
- yarn

#### 安装依赖
```bash
cd /root/frontend-naive
yarn install
```

#### 配置后端 API 地址
编辑 `src/config.js` 或相关配置文件，设置后端 API 地址：
```javascript
export const API_BASE_URL = 'http://localhost:8080'
```

#### 启动开发服务器
```bash
yarn dev
```
前端开发服务器会在 `http://localhost:3000` 启动（具体端口查看终端输出）

#### 构建生产版本
```bash
yarn build
```
构建后的文件会输出到 `dist/` 目录

#### 前端技术栈
- Vue 3
- NaiveUI (UI 组件库)
- Vite (构建工具)
- Vue Router
- Pinia (状态管理)

---

### 3. 评测服务器开发 (Judger)

#### 环境要求
- Python ≥ 3.8
- Linux 环境（需要 root 权限）

#### 安装
```bash
cd /root/judger
sudo chmod 777 deploy.sh
sudo ./deploy.sh
sudo pip3 install -r requirements.txt
```

#### 配置
创建 `config.py` 文件：
```python
# 评测服务器配置
BACKEND_URL = 'http://localhost:8080'
TEST_CASE_DIR = '/srv/test_data'
SPJ_DIR = '/srv/spj'
```

#### 启动评测服务器
```bash
sudo python3 server.py
```

⚠️ **注意**: 评测服务器需要 root 权限运行，因为需要创建用户和访问特定目录

---

## 🔧 使用已部署的服务进行开发

如果你想使用已经部署的 Docker 服务（数据库、Redis、RabbitMQ）进行开发：

### 查看运行中的服务
```bash
cd /root/deploy
docker-compose ps
```

### 服务端口映射
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- RabbitMQ: `localhost:5672`
- Backend API: `localhost:8080`
- Frontend: `localhost:80`

### 连接到容器内的数据库
```bash
# 进入 PostgreSQL 容器
docker exec -it oj-postgres psql -U onlinejudge -d onlinejudge

# 进入 Redis 容器
docker exec -it oj-redis redis-cli

# 查看后端日志
docker logs -f oj-backend

# 查看评测服务器日志
docker logs -f oj-judge-server
```

### 停止 Docker 服务（开发时）
```bash
cd /root/deploy
docker-compose stop
```

### 重启 Docker 服务
```bash
cd /root/deploy
docker-compose start
```

---

## 📝 开发工作流建议

### 方案 1: 完全本地开发
1. 安装所有依赖（PostgreSQL, Redis, RabbitMQ）
2. 在本地运行后端、前端和评测服务器
3. 适合需要频繁修改所有组件的情况

### 方案 2: 混合开发（推荐）
1. 使用 Docker 运行基础服务（数据库、Redis、RabbitMQ）
2. 在本地运行你要修改的服务（前端或后端）
3. 修改代码后可以立即看到效果

```bash
# 只启动基础服务
cd /root/deploy
docker-compose up -d postgres redis rabbitmq

# 然后在本地运行后端和前端
cd /root/backend
python3 manage.py runserver 0.0.0.0:8080

cd /root/frontend-naive
yarn dev
```

### 方案 3: 容器化开发
1. 修改代码后重新构建 Docker 镜像
2. 适合测试部署流程

```bash
cd /root/deploy
docker-compose build
docker-compose up -d
```

---

## 🐛 调试技巧

### 后端调试
```bash
# 启用 Django Debug 模式
# 在 config.py 中设置
DEBUG = True

# 查看详细日志
python3 manage.py runserver --verbosity 3
```

### 前端调试
- 使用浏览器开发者工具
- Vue DevTools 扩展
- 查看 Vite 开发服务器输出

### 数据库调试
```bash
# 进入 Django shell
python3 manage.py shell

# 查看数据库查询
python3 manage.py dbshell
```

---

## 📚 常用命令速查

### 后端
```bash
# 创建新的 Django app
python3 manage.py startapp app_name

# 数据库迁移
python3 manage.py makemigrations
python3 manage.py migrate

# 创建超级用户
python3 manage.py createsuperuser

# 收集静态文件
python3 manage.py collectstatic
```

### 前端
```bash
# 安装新依赖
yarn add package-name

# 开发模式
yarn dev

# 构建
yarn build

# 代码检查
yarn lint
```

### Docker
```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f [service_name]

# 重启服务
docker-compose restart [service_name]

# 停止所有服务
docker-compose down

# 停止并删除数据
docker-compose down -v
```

---

## 🔐 默认账号信息

- **管理员账号**: admin
- **密码**: 123456
- **邮箱**: admin@genuine.oj

⚠️ **生产环境请务必修改默认密码！**

---

## 📖 更多资源

- [Backend GitHub](https://github.com/genuine-oj/backend)
- [Frontend GitHub](https://github.com/genuine-oj/frontend-naive)
- [Judger GitHub](https://github.com/genuine-oj/judger)
- [Deploy GitHub](https://github.com/genuine-oj/deploy)

---

## 💡 开发建议

1. **版本控制**: 为你的修改创建新的 Git 分支
2. **代码规范**: 遵循项目现有的代码风格
3. **测试**: 修改后进行充分测试
4. **文档**: 为新功能编写文档
5. **备份**: 定期备份数据库和重要文件

祝开发顺利！🎉
