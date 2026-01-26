#!/bin/bash

# 🔧 数据库自动清理脚本
# 用法: bash cleanup_database.sh [backup|clean|migrate|verify|all]

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_step() {
    echo -e "${BLUE}==== $1 ====${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# 检查依赖
check_dependencies() {
    print_step "检查依赖"
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 未安装"
        exit 1
    fi
    print_success "Python 3 已安装"
    
    if ! command -v psql &> /dev/null; then
        print_warning "PostgreSQL 未安装或不在 PATH 中（SQLite 模式可用）"
    else
        print_success "PostgreSQL 已安装"
    fi
}

# 备份数据库
backup_database() {
    print_step "备份数据库"
    
    cd "$BACKEND_DIR"
    
    # 检查数据库类型
    SQLITE_DB="$BACKEND_DIR/db.sqlite3"
    
    if [ -f "$SQLITE_DB" ]; then
        print_step "检测到 SQLite 数据库"
        BACKUP_FILE="db.sqlite3.backup_$TIMESTAMP"
        cp "$SQLITE_DB" "$BACKUP_FILE"
        print_success "SQLite 数据库已备份到: $BACKUP_FILE"
    else
        print_step "检测到 PostgreSQL 数据库"
        # PostgreSQL 备份
        # 需要配置 PG 连接参数
        read -p "输入 PostgreSQL 数据库名称 [oj]: " DB_NAME
        DB_NAME=${DB_NAME:-oj}
        
        read -p "输入 PostgreSQL 用户名 [postgres]: " DB_USER
        DB_USER=${DB_USER:-postgres}
        
        read -p "输入 PostgreSQL 主机 [localhost]: " DB_HOST
        DB_HOST=${DB_HOST:-localhost}
        
        BACKUP_FILE="oj_backup_${TIMESTAMP}.sql.gz"
        pg_dump -U "$DB_USER" -h "$DB_HOST" "$DB_NAME" | gzip > "$BACKUP_FILE"
        print_success "PostgreSQL 数据库已备份到: $BACKUP_FILE"
    fi
}

# 清理混乱数据
clean_data() {
    print_step "清理混乱数据"
    
    cd "$BACKEND_DIR"
    
    python3 manage.py shell << 'PYTHON_SCRIPT'
import sys
from oj_course.models import CourseChapter

print("清理前的数据统计:")
total_before = CourseChapter.objects.count()
print(f"  总 CourseChapter 数: {total_before}")

if total_before > 0:
    print("\n📊 CourseChapter 分布:")
    for course_id in CourseChapter.objects.values('course_id').distinct():
        count = CourseChapter.objects.filter(course_id=course_id['course_id']).count()
        print(f"  课程 {course_id['course_id']}: {count} 个章节")

# 删除所有混乱的 CourseChapter
print("\n⚠️  删除所有 CourseChapter...")
CourseChapter.objects.all().delete()

print("\n清理后的数据统计:")
total_after = CourseChapter.objects.count()
print(f"  总 CourseChapter 数: {total_after}")
print(f"\n✓ 删除了 {total_before - total_after} 个混乱的章节")

PYTHON_SCRIPT
    
    if [ $? -eq 0 ]; then
        print_success "数据清理完成"
    else
        print_error "数据清理失败"
        return 1
    fi
}

# 执行迁移
run_migrations() {
    print_step "执行数据库迁移"
    
    cd "$BACKEND_DIR"
    
    print_step "步骤 1: 创建 oj_videocourse 迁移"
    python3 manage.py makemigrations oj_videocourse
    if [ $? -eq 0 ]; then
        print_success "迁移文件创建成功"
    fi
    
    print_step "步骤 2: 执行迁移"
    python3 manage.py migrate oj_videocourse
    if [ $? -eq 0 ]; then
        print_success "oj_videocourse 迁移完成"
    else
        print_error "迁移执行失败"
        return 1
    fi
    
    print_step "步骤 3: 执行所有迁移"
    python3 manage.py migrate
    if [ $? -eq 0 ]; then
        print_success "所有迁移完成"
    else
        print_error "迁移执行失败"
        return 1
    fi
}

# 创建输出目录
create_directories() {
    print_step "创建输出目录"
    
    mkdir -p "$BACKEND_DIR/judge_data/videocourse_output"
    chmod 755 "$BACKEND_DIR/judge_data/videocourse_output"
    
    print_success "输出目录创建完成"
}

# 验证数据库分离
verify_separation() {
    print_step "验证数据库分离"
    
    cd "$BACKEND_DIR"
    
    python3 manage.py shell << 'PYTHON_SCRIPT'
from django.db import connection
from oj_course.models import Course, CourseChapter
from oj_videocourse.models import VideoCourse, VideoCourseChapter

# 检查数据库表
print("📊 数据库表检查:")
cursor = connection.cursor()

print("\n  直播课数据库表:")
try:
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public' AND table_name LIKE 'course_%'
    """)
    for row in cursor.fetchall():
        print(f"    ✓ {row[0]}")
except Exception as e:
    # SQLite 不支持 information_schema
    print(f"    ℹ️  使用 SQLite 数据库")

print("\n  录播课数据库表:")
try:
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public' AND table_name LIKE 'videocourse_%'
    """)
    for row in cursor.fetchall():
        print(f"    ✓ {row[0]}")
except Exception as e:
    print(f"    ℹ️  使用 SQLite 数据库")

# 检查数据
print("\n📈 数据统计:")
print(f"  直播课: {Course.objects.count()}")
print(f"  直播课章节: {CourseChapter.objects.count()}")
print(f"  录播课: {VideoCourse.objects.count()}")
print(f"  录播课章节: {VideoCourseChapter.objects.count()}")

# 验证分离
if CourseChapter.objects.count() == 0:
    print("\n✓ 混乱数据已清理（CourseChapter 为空）")
else:
    print(f"\n⚠️  仍有 {CourseChapter.objects.count()} 个混乱的 CourseChapter")

try:
    VideoCourseChapter.objects.count()
    print("✓ 录播课表创建成功")
except Exception as e:
    print(f"✗ 录播课表问题: {e}")

PYTHON_SCRIPT
}

# 显示使用说明
show_usage() {
    cat << 'USAGE'
用法: bash cleanup_database.sh [命令]

命令:
    backup      - 只备份数据库
    clean       - 只清理混乱数据
    migrate     - 只执行迁移
    verify      - 只验证数据库分离
    all         - 执行所有步骤（默认）
    help        - 显示此帮助信息

示例:
    bash cleanup_database.sh                  # 执行所有步骤
    bash cleanup_database.sh backup           # 只备份
    bash cleanup_database.sh clean            # 只清理
    bash cleanup_database.sh all              # 完整流程

USAGE
}

# 执行所有步骤
execute_all() {
    print_step "开始完整数据库清理流程"
    
    check_dependencies || return 1
    backup_database || return 1
    clean_data || return 1
    run_migrations || return 1
    create_directories || return 1
    verify_separation || return 1
    
    print_step "✅ 所有步骤完成！"
    echo -e "${GREEN}"
    echo "数据库现在已：${NC}"
    echo "  ✓ 备份到文件"
    echo "  ✓ 清理混乱数据"
    echo "  ✓ 创建 oj_videocourse 表"
    echo "  ✓ 直播课和录播课完全分离"
    echo ""
    echo "下一步：重启服务并测试 API"
}

# 主程序
main() {
    local cmd="${1:-all}"
    
    case "$cmd" in
        backup)
            check_dependencies
            backup_database
            ;;
        clean)
            clean_data
            ;;
        migrate)
            run_migrations
            ;;
        verify)
            verify_separation
            ;;
        all)
            execute_all
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "未知命令: $cmd"
            show_usage
            exit 1
            ;;
    esac
}

main "$@"
