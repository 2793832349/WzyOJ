# 🔧 Docker 部署网络超时问题 - 解决方案

## 🎯 问题分析

你遇到的错误：
```
TimeoutError: The read operation timed out
ReadTimeoutError: HTTPSConnectionPool Read timed out
failed to resolve source metadata: dial tcp: i/o timeout
```

**根本原因**：
1. pip 下载 Python 包超时（numpy 等包太大）
2. Docker 拉取基础镜像超时
3. 服务器网络连接不稳定或速度慢

---

## ✅ 快速解决方案

### 方案 1️⃣：使用国内镜像源（推荐）

编辑 `deploy/Dockerfile.backend`：

```dockerfile
FROM python:3.10-bullseye

COPY ./backend /srv/server

# 使用国内镜像源加速 pip
RUN cd /srv/server && \
    pip3 install -i https://mirrors.aliyun.com/pypi/simple/ \
    -r requirements.txt --no-cache-dir && \
    pip3 install -i https://mirrors.aliyun.com/pypi/simple/ \
    psycopg2 uwsgi --no-cache-dir

RUN mkdir -p /data/problem_files /data/judge_data/submission /data/judge_data/test_data && \
    apt-get purge -y --auto-remove git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

CMD ["uwsgi", "--ini", "/srv/server/uwsgi.ini"]
```

### 方案 2️⃣：增加超时时间

编辑 `deploy/docker-compose.yml`，添加超时配置：

```yaml
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
      args:
        - USE_MIRROR=true
    environment:
      - PIP_DEFAULT_TIMEOUT=1000
      - PIP_RETRIES=5
    # ... 其他配置
```

### 方案 3️⃣：直接在服务器上安装依赖

```bash
# 1. 进入 backend 目录
cd ~/WzyOJ/backend

# 2. 设置 pip 超时和国内镜像
pip3 config set global.index-url https://mirrors.aliyun.com/pypi/simple/
pip3 config set global.timeout 600

# 3. 安装依赖
pip3 install -r requirements.txt --no-cache-dir

# 4. 安装额外包
pip3 install psycopg2 uwsgi --no-cache-dir
```

---

## 🚀 完整部署步骤（推荐）

### 第一步：配置 pip 镜像

```bash
# 创建或编辑 ~/.pip/pip.conf
cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
timeout = 600
retries = 5

[install]
extra-index-url = https://pypi.tuna.tsinghua.edu.cn/simple

trusted-host =
    mirrors.aliyun.com
    pypi.tuna.tsinghua.edu.cn
    pypi.org
EOF
```

### 第二步：配置 Docker 镜像加速

编辑 `/etc/docker/daemon.json`：

```json
{
  "registry-mirrors": [
    "https://mirror.baidubce.com",
    "https://ccr.ccs.tencentyun.com",
    "http://mirror.aliyuncs.com"
  ],
  "insecure-registries": [],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}
```

重启 Docker：
```bash
sudo systemctl restart docker
```

### 第三步：重新构建并部署

```bash
cd ~/WzyOJ/deploy

# 清除旧镜像
docker-compose down
docker system prune -a

# 重新构建（会更快）
docker-compose build --no-cache

# 启动服务
docker-compose up -d
```

---

## 📝 快速修复脚本

创建文件：`~/WzyOJ/fix_network.sh`

```bash
#!/bin/bash

echo "🔧 修复 Docker 部署网络问题..."

# 1. 配置 pip 镜像
echo "1️⃣ 配置 pip 镜像源..."
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
timeout = 600
retries = 5
EOF

# 2. 配置 Docker 镜像
echo "2️⃣ 配置 Docker 镜像加速..."
sudo mkdir -p /etc/docker
sudo cat > /etc/docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://mirror.baidubce.com",
    "https://ccr.ccs.tencentyun.com",
    "http://mirror.aliyuncs.com"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}
EOF

# 3. 重启 Docker
echo "3️⃣ 重启 Docker..."
sudo systemctl restart docker

# 4. 清理旧镜像
echo "4️⃣ 清理旧 Docker 镜像..."
docker system prune -a -f

echo "✅ 配置完成！现在可以重新构建了"
```

执行脚本：
```bash
bash ~/WzyOJ/fix_network.sh
```

---

## 📊 镜像源速度对比

| 镜像源 | 速度 | 稳定性 | 推荐度 |
|--------|------|--------|--------|
| PyPI 官方 | 慢 | 中 | ❌ |
| 阿里云 | 快 | 高 | ✅ |
| 清华大学 | 快 | 高 | ✅ |
| 腾讯云 | 快 | 高 | ✅ |
| 豆瓣 | 快 | 中 | ⚠️ |

---

## 🛠️ 分步部署（如果 Docker 仍有问题）

如果 Docker 构建仍然超时，可以：

```bash
# 1. 手动安装依赖
cd ~/WzyOJ/backend
pip3 install -r requirements.txt --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/
pip3 install psycopg2 uwsgi --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/

# 2. 跳过 Docker，直接运行
python3 manage.py runserver 0.0.0.0:8000

# 或使用 Gunicorn
gunicorn oj_backend.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

## 🎯 推荐操作步骤

### 立即行动（5 分钟）
```bash
# 1. 配置 pip 镜像
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
timeout = 600
retries = 5
EOF

# 2. 进入项目目录
cd ~/WzyOJ/deploy

# 3. 清理旧构建
docker-compose down
docker system prune -a -f

# 4. 重新构建
docker-compose build --no-cache
```

### 如果仍然超时（15 分钟）
```bash
# 1. 停止 Docker
docker-compose down

# 2. 手动安装依赖
cd ~/WzyOJ/backend
pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --upgrade --default-timeout=600

# 3. 直接启动后端
python3 manage.py runserver 0.0.0.0:8000
```

---

## ⚠️ 常见问题

**Q: 阿里云镜像源也很慢？**  
A: 尝试清华大学镜像：`https://pypi.tuna.tsinghua.edu.cn/simple`

**Q: Docker 仍然超时？**  
A: 考虑跳过 Docker，直接在服务器上运行 Python 应用

**Q: 如何检查网络连接？**  
A: 
```bash
# 测试到镜像源的连接
curl -I https://mirrors.aliyun.com/pypi/simple/
ping -c 3 mirrors.aliyun.com

# 测试 Docker 镜像拉取
docker pull hello-world
```

---

## 📞 获得更多帮助

- 查看 `QUICK_REFERENCE.md` - 快速部署命令
- 查看 `DEPLOYMENT_CHECKLIST.md` - 完整部署步骤
- 查看 `DATABASE_CLEANUP_GUIDE.md` - 数据库配置

---

**总结**：
1. ✅ 配置国内 pip 镜像源（最快）
2. ✅ 配置 Docker 镜像加速
3. ✅ 增加超时时间
4. ✅ 如果仍有问题，跳过 Docker 直接部署

**预期结果**：下载速度提升 5-10 倍！🚀
