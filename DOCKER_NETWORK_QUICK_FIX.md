# ⚡ Docker 网络超时 - 快速解决方案

## 🔴 问题症状

你看到这样的错误：
```
TimeoutError: The read operation timed out
ReadTimeoutError: HTTPSConnectionPool Read timed out
failed to resolve source metadata: dial tcp: i/o timeout
```

**原因**: 下载 Python 包或 Docker 镜像太慢导致超时

---

## ✅ 一键修复（最快方式）

### 在 Linux 服务器上执行：

```bash
# 进入项目目录
cd ~/WzyOJ

# 下载修复脚本
wget https://raw.githubusercontent.com/... fix_docker_network.sh
# 或直接从本地上传
scp fix_docker_network.sh user@server:~/WzyOJ/

# 执行修复脚本
bash fix_docker_network.sh

# 或使用 Python 脚本
python3 fix_docker_network.py
```

---

## 🚀 如果脚本失败，手动修复

### 步骤 1️⃣ : 配置 pip 镜像源

```bash
# 创建 pip 配置目录
mkdir -p ~/.pip

# 编辑或创建配置文件
cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
timeout = 600
retries = 5
EOF
```

### 步骤 2️⃣ : 配置 Docker 镜像加速

```bash
# 创建 Docker 配置目录
sudo mkdir -p /etc/docker

# 编辑或创建 daemon.json
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
```

### 步骤 3️⃣ : 重启 Docker

```bash
# 重启 Docker 服务
sudo systemctl restart docker

# 等待 3-5 秒
sleep 5

# 验证
docker info | grep registry-mirrors
```

### 步骤 4️⃣ : 清理旧镜像

```bash
# 清理所有未使用的镜像
docker system prune -a -f
```

---

## 🔄 重新部署

### 方案 A: 继续使用 Docker（推荐）

```bash
cd ~/WzyOJ/deploy

# 清除旧构建
docker-compose down

# 重新构建（现在会更快）
docker-compose build --no-cache

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend
```

### 方案 B: 跳过 Docker，直接部署（如果 Docker 仍有问题）

```bash
cd ~/WzyOJ/backend

# 安装依赖
pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --upgrade --default-timeout=600

# 进行数据库迁移
python3 manage.py migrate

# 启动开发服务器
python3 manage.py runserver 0.0.0.0:8000

# 或使用 Gunicorn（生产环境）
gunicorn oj_backend.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

## 🧪 测试网络速度

```bash
# 测试阿里云 PyPI 镜像
time pip3 install numpy -i https://mirrors.aliyun.com/pypi/simple/

# 测试 Docker 镜像拉取
time docker pull hello-world

# 显示详细进度
docker pull python:3.10-bullseye --progress=plain
```

---

## 📊 可用的镜像源

### PyPI 镜像源
| 镜像源 | URL | 速度 | 稳定性 |
|--------|-----|------|--------|
| 阿里云 | https://mirrors.aliyun.com/pypi/simple/ | 🚀🚀🚀 | ⭐⭐⭐⭐⭐ |
| 清华大学 | https://pypi.tuna.tsinghua.edu.cn/simple | 🚀🚀🚀 | ⭐⭐⭐⭐⭐ |
| 腾讯云 | https://mirrors.cloud.tencent.com/pypi/simple | 🚀🚀🚀 | ⭐⭐⭐⭐ |
| 豆瓣 | https://pypi.douban.com/simple | 🚀🚀 | ⭐⭐⭐ |
| 官方 PyPI | https://pypi.org/simple/ | 🐌 | ⭐⭐ |

### Docker 镜像源
| 镜像源 | URL | 速度 | 稳定性 |
|--------|-----|------|--------|
| 百度云 | https://mirror.baidubce.com | 🚀🚀🚀 | ⭐⭐⭐⭐⭐ |
| 腾讯云 | https://ccr.ccs.tencentyun.com | 🚀🚀🚀 | ⭐⭐⭐⭐⭐ |
| 阿里云 | http://mirror.aliyuncs.com | 🚀🚀 | ⭐⭐⭐⭐ |

---

## 💡 推荐配置

### 最快的组合
```bash
# pip 使用阿里云
pip3 install -i https://mirrors.aliyun.com/pypi/simple/ ...

# Docker 使用百度云
registry-mirrors: ["https://mirror.baidubce.com"]
```

### 备选配置（如果阿里云不稳定）
```bash
# pip 使用清华大学
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple ...

# Docker 使用腾讯云
registry-mirrors: ["https://ccr.ccs.tencentyun.com"]
```

---

## ❓ 常见问题

**Q: 我之前已经配置过，为什么还是超时？**  
A: 清除缓存并重新下载：
```bash
pip3 cache purge
docker system prune -a -f
```

**Q: 配置后仍然很慢？**  
A: 检查你的网络连接：
```bash
# 测试网速
speedtest-cli

# 测试延迟
ping mirrors.aliyun.com

# 追踪路由
traceroute mirrors.aliyun.com
```

**Q: Docker 容器能访问镜像源吗？**  
A: 需要在 Dockerfile 中指定：
```dockerfile
RUN pip3 install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
```

**Q: 如何在 docker-compose 中使用镜像源？**  
A: 在 Dockerfile 中配置（上面已说明）

---

## 🎯 下一步

1. ✅ 执行修复脚本或手动配置
2. ✅ 重启 Docker 服务
3. ✅ 重新部署应用
4. ✅ 检查日志确保成功

---

## 📝 部署完整流程（修复后）

```bash
# 1. 进入项目目录
cd ~/WzyOJ/deploy

# 2. 停止旧服务
docker-compose down

# 3. 清理旧镜像
docker system prune -a -f

# 4. 重新构建（会更快）
docker-compose build --no-cache

# 5. 启动新服务
docker-compose up -d

# 6. 查看日志
docker-compose logs -f

# 7. 验证服务
curl http://localhost:8000/api/course-chapters/
curl http://localhost:8000/api/video-courses/
```

---

**预期结果**: 下载速度提升 5-10 倍！🚀

现在就开始修复，预计 5-10 分钟完成！
