�'#!/bin/bash

# Genuine OJ 开发环境快速启动脚本

echo "======================================"
echo "  Genuine OJ 开发环境启动脚本"
echo "======================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Docker 服务
check_docker() {
    if ! docker ps > /dev/null 2>&1; then
        echo -e "${RED}错误: Docker 服务未运行${NC}"
        echo "请先启动 Docker 服务: sudo systemctl start docker"
        exit 1
    fi
}

# 启动基础服务
start_base_services() {
    echo -e "${YELLOW}启动基础服务 (PostgreSQL, Redis, RabbitMQ)...${NC}"
    cd /root/deploy
    docker-compose up -d postgres redis rabbitmq
    echo -e "${GREEN}✓ 基础服务已启动${NC}"
    echo ""
}

# 显示菜单
show_menu() {
    echo "请选择开发模式:"
    echo ""
    echo "1) 启动完整 Docker 环境 (生产模式)"
    echo "2) 启动基础服务 + 本地后端开发"
    echo "3) 启动基础服务 + 本地前端开发"
    echo "4) 启动基础服务 + 本地前后端开发"
    echo "5) 仅启动基础服务 (数据库、Redis、RabbitMQ)"
    echo "6) 停止所有 Docker 服务"
    echo "7) 查看服务状态"
    echo "8) 查看服务日志"
    echo "0) 退出"
    echo ""
    read -p "请输入选项 [0-8]: " choice
}

# 启动完整 Docker 环境
start_full_docker() {
    echo -e "${YELLOW}启动完整 Docker 环境...${NC}"
    cd /root/deploy
    docker-compose up -d
    echo -e "${GREEN}✓ 所有服务已启动${NC}"
    echo ""
    echo "访问地址:"
    echo "  前端: http://localhost:80"
    echo "  后端 API: http://localhost:8080"
    echo ""
    echo "查看日志: docker-compose logs -f"
}

# 本地后端开发
start_backend_dev() {
    start_base_services
    echo -e "${YELLOW}准备启动本地后端开发环境...${NC}"
    echo ""
    echo "请在新终端中执行以下命令:"
    echo ""
    echo -e "${GREEN}# 终端 1: 启动 Django 开发服务器${NC}"
    echo "cd /root/backend"
    echo "python3 manage.py runserver 0.0.0.0:8080"
    echo ""
    echo -e "${GREEN}# 终端 2: 启动 Celery 任务队列${NC}"
    echo "cd /root/backend"
    echo "celery -A oj_backend worker -l info"
    echo ""
}

# 本地前端开发
start_frontend_dev() {
    start_base_services
    echo -e "${YELLOW}准备启动本地前端开发环境...${NC}"
    echo ""
    echo "请在新终端中执行以下命令:"
    echo ""
    echo -e "${GREEN}# 启动前端开发服务器${NC}"
    echo "cd /root/frontend-naive"
    echo "yarn dev"
    echo ""
    echo "注意: 请确保后端服务正在运行 (Docker 或本地)"
}

# 本地前后端开发
start_full_dev() {
    start_base_services
    echo -e "${YELLOW}准备启动本地前后端开发环境...${NC}"
    echo ""
    echo "请在新终端中执行以下命令:"
    echo ""
    echo -e "${GREEN}# 终端 1: 启动 Django 开发服务器${NC}"
    echo "cd /root/backend"
    echo "python3 manage.py runserver 0.0.0.0:8080"
    echo ""
    echo -e "${GREEN}# 终端 2: 启动 Celery 任务队列${NC}"
    echo "cd /root/backend"
    echo "celery -A oj_backend worker -l info"
    echo ""
    echo -e "${GREEN}# 终端 3: 启动前端开发服务器${NC}"
    echo "cd /root/frontend-naive"
    echo "yarn dev"
    echo ""
}

# 停止所有服务
stop_services() {
    echo -e "${YELLOW}停止所有 Docker 服务...${NC}"
    cd /root/deploy
    docker-compose down
    echo -e "${GREEN}✓ 所有服务已停止${NC}"
}

# 查看服务状态
show_status() {
    echo -e "${YELLOW}服务状态:${NC}"
    cd /root/deploy
    docker-compose ps
}

# 查看日志
show_logs() {
    echo "请选择要查看的服务日志:"
    echo "1) Backend (后端)"
    echo "2) Frontend (前端)"
    echo "3) Judge Server (评测服务器)"
    echo "4) PostgreSQL (数据库)"
    echo "5) Redis"
    echo "6) RabbitMQ"
    echo "7) 所有服务"
    echo ""
    read -p "请输入选项 [1-7]: " log_choice
    
    cd /root/deploy
    case $log_choice in
        1) docker logs -f oj-backend ;;
        2) docker logs -f oj-frontend ;;
        3) docker logs -f oj-judge-server ;;
        4) docker logs -f oj-postgres ;;
        5) docker logs -f oj-redis ;;
        6) docker logs -f oj-rabbitmq ;;
        7) docker-compose logs -f ;;
        *) echo -e "${RED}无效选项${NC}" ;;
    esac
}

# 主程序
main() {
    check_docker
    
    while true; do
        show_menu
        
        case $choice in
            1) start_full_docker ;;
            2) start_backend_dev ;;
            3) start_frontend_dev ;;
            4) start_full_dev ;;
            5) start_base_services ;;
            6) stop_services ;;
            7) show_status ;;
            8) show_logs ;;
            0) 
                echo "退出"
                exit 0
                ;;
            *)
                echo -e "${RED}无效选项，请重新选择${NC}"
                ;;
        esac
        
        echo ""
        read -p "按 Enter 键继续..."
        clear
    done
}

# 运行主程序
main
�'*cascade082file:///root/start-dev.sh