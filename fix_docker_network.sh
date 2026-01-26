#!/bin/bash

# 🔧 Docker 部署网络超时快速修复脚本
# 用法: bash fix_docker_network.sh

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Docker 部署网络超时问题 - 快速修复脚本                  ║"
echo "╚════════════════════════════════════════════════════════════╝"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}==== $1 ====${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# 第一步：配置 pip 镜像
print_step "第一步: 配置 pip 镜像源"

mkdir -p ~/.pip
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

print_success "pip 镜像配置完成"

# 第二步：配置 Docker 镜像加速
print_step "第二步: 配置 Docker 镜像加速"

sudo mkdir -p /etc/docker

# 检查是否已存在 daemon.json
if [ -f /etc/docker/daemon.json ]; then
    print_warning "发现现有 daemon.json，正在备份..."
    sudo cp /etc/docker/daemon.json /etc/docker/daemon.json.backup
fi

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

print_success "Docker 镜像加速配置完成"

# 第三步：重启 Docker
print_step "第三步: 重启 Docker 服务"

if sudo systemctl restart docker; then
    print_success "Docker 已重启"
    sleep 3
else
    print_warning "无法重启 Docker，可能需要手动执行: sudo systemctl restart docker"
fi

# 第四步：清理旧镜像
print_step "第四步: 清理旧 Docker 镜像"

if docker system prune -a -f &>/dev/null; then
    print_success "旧镜像已清理"
else
    print_warning "清理镜像失败，可能已清理"
fi

# 第五步：验证配置
print_step "第五步: 验证镜像配置"

if docker info | grep -q "registry-mirrors"; then
    print_success "Docker 镜像加速已启用"
else
    print_warning "Docker 镜像加速配置可能未生效"
fi

# 第六步：测试网络
print_step "第六步: 测试网络连接"

if timeout 5 curl -s -I https://mirrors.aliyun.com/pypi/simple/ > /dev/null 2>&1; then
    print_success "阿里云 PyPI 镜像连接正常"
else
    print_warning "阿里云 PyPI 镜像连接失败，尝试其他镜像"
    if timeout 5 curl -s -I https://pypi.tuna.tsinghua.edu.cn/simple > /dev/null 2>&1; then
        print_success "清华大学 PyPI 镜像连接正常"
    else
        print_warning "所有 PyPI 镜像连接失败，请检查网络"
    fi
fi

echo ""
print_step "✅ 配置完成！"

echo ""
echo "现在可以执行以下命令重新部署："
echo ""
echo -e "${BLUE}cd ~/WzyOJ/deploy${NC}"
echo -e "${BLUE}docker-compose down${NC}"
echo -e "${BLUE}docker-compose build --no-cache${NC}"
echo -e "${BLUE}docker-compose up -d${NC}"
echo ""
echo "或者，如果 Docker 仍然有问题，使用以下命令直接在服务器运行："
echo ""
echo -e "${BLUE}cd ~/WzyOJ/backend${NC}"
echo -e "${BLUE}pip3 install -r requirements.txt${NC}"
echo -e "${BLUE}python3 manage.py runserver 0.0.0.0:8000${NC}"
echo ""
