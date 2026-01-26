#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 Docker 部署网络超时快速修复脚本
用法: python3 fix_docker_network.py
"""

import os
import sys
import json
import subprocess
from pathlib import Path

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'

def print_step(msg):
    print(f"{Colors.BLUE}==== {msg} ===={Colors.END}")

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def run_command(cmd, sudo=False):
    """执行 Shell 命令"""
    if sudo:
        cmd = f"sudo {cmd}"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def setup_pip_config():
    """配置 pip 镜像源"""
    print_step("第一步: 配置 pip 镜像源")
    
    pip_config = """[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
timeout = 600
retries = 5

[install]
extra-index-url = https://pypi.tuna.tsinghua.edu.cn/simple

trusted-host =
    mirrors.aliyun.com
    pypi.tuna.tsinghua.edu.cn
    pypi.org
"""
    
    pip_dir = Path.home() / ".pip"
    pip_dir.mkdir(exist_ok=True)
    
    config_file = pip_dir / "pip.conf"
    config_file.write_text(pip_config)
    
    print_success("pip 镜像配置完成")
    return True

def setup_docker_config():
    """配置 Docker 镜像加速"""
    print_step("第二步: 配置 Docker 镜像加速")
    
    docker_config = {
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
    
    daemon_json = Path("/etc/docker/daemon.json")
    
    # 备份现有配置
    if daemon_json.exists():
        backup_file = daemon_json.with_suffix('.backup')
        os.system(f"sudo cp {daemon_json} {backup_file}")
        print_warning(f"现有配置已备份到 {backup_file}")
    
    # 写入新配置
    config_text = json.dumps(docker_config, indent=2)
    with open("/tmp/daemon.json", "w") as f:
        f.write(config_text)
    
    os.system("sudo mv /tmp/daemon.json /etc/docker/daemon.json")
    print_success("Docker 镜像加速配置完成")
    
    return True

def restart_docker():
    """重启 Docker 服务"""
    print_step("第三步: 重启 Docker 服务")
    
    success, _, _ = run_command("systemctl restart docker", sudo=True)
    
    if success:
        print_success("Docker 已重启")
        import time
        time.sleep(3)
        return True
    else:
        print_warning("无法自动重启 Docker，请手动执行: sudo systemctl restart docker")
        return False

def clean_docker():
    """清理旧 Docker 镜像"""
    print_step("第四步: 清理旧 Docker 镜像")
    
    success, _, _ = run_command("docker system prune -a -f")
    
    if success:
        print_success("旧镜像已清理")
        return True
    else:
        print_warning("清理镜像失败或已清理")
        return False

def verify_config():
    """验证 Docker 配置"""
    print_step("第五步: 验证镜像配置")
    
    success, output, _ = run_command("docker info")
    
    if success and "registry-mirrors" in output:
        print_success("Docker 镜像加速已启用")
        return True
    else:
        print_warning("Docker 镜像加速配置可能未生效")
        return False

def test_network():
    """测试网络连接"""
    print_step("第六步: 测试网络连接")
    
    # 测试阿里云
    success, _, _ = run_command("timeout 5 curl -s -I https://mirrors.aliyun.com/pypi/simple/")
    if success:
        print_success("阿里云 PyPI 镜像连接正常")
        return True
    
    # 测试清华大学
    success, _, _ = run_command("timeout 5 curl -s -I https://pypi.tuna.tsinghua.edu.cn/simple")
    if success:
        print_success("清华大学 PyPI 镜像连接正常")
        return True
    
    print_warning("所有 PyPI 镜像连接失败，请检查网络")
    return False

def print_next_steps():
    """打印后续步骤"""
    print("")
    print_step("✅ 配置完成！")
    print("")
    print(f"现在可以执行以下命令重新部署：")
    print("")
    print(f"{Colors.BLUE}cd ~/WzyOJ/deploy{Colors.END}")
    print(f"{Colors.BLUE}docker-compose down{Colors.END}")
    print(f"{Colors.BLUE}docker-compose build --no-cache{Colors.END}")
    print(f"{Colors.BLUE}docker-compose up -d{Colors.END}")
    print("")
    print(f"或者，如果 Docker 仍然有问题，使用以下命令直接在服务器运行：")
    print("")
    print(f"{Colors.BLUE}cd ~/WzyOJ/backend{Colors.END}")
    print(f"{Colors.BLUE}pip3 install -r requirements.txt{Colors.END}")
    print(f"{Colors.BLUE}python3 manage.py runserver 0.0.0.0:8000{Colors.END}")
    print("")

def main():
    """主程序"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   Docker 部署网络超时问题 - 快速修复脚本                  ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print("")
    
    try:
        # 执行各步骤
        setup_pip_config()
        setup_docker_config()
        restart_docker()
        clean_docker()
        verify_config()
        test_network()
        
        print_next_steps()
        
    except Exception as e:
        print_error(f"执行出错: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
