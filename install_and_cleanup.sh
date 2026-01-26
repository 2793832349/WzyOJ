#!/bin/bash

# 🔧 WzyOJ 依赖安装和数据库清理 - 完整脚本
# 用法: bash install_and_cleanup.sh

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     WzyOJ 依赖安装和数据库清理 - 完整脚本                 ║"
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

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# 检查 Python 版本
print_step "检查 Python 环境"

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 未安装"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_success "Python $PYTHON_VERSION 已安装"

# 进入 backend 目录
cd ~/WzyOJ/backend || exit 1
print_success "进入 backend 目录: $(pwd)"

# 升级 pip
print_step "升级 pip"
python3 -m pip install --upgrade pip setuptools wheel -q
print_success "pip 已升级"

# 安装依赖
print_step "安装项目依赖"

echo "这可能需要 2-5 分钟，请耐心等待..."
echo ""

# 检查是否有 requirements.txt
if [ ! -f "requirements.txt" ]; then
    print_error "找不到 requirements.txt 文件"
    exit 1
fi

# 使用国内镜像源安装（加快速度）
if python3 -m pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt --upgrade 2>&1 | tail -20; then
    print_success "项目依赖安装完成"
else
    print_warning "某些依赖安装可能失败，尝试使用官方源重新安装..."
    python3 -m pip install -r requirements.txt --upgrade
    print_success "项目依赖安装完成"
fi

echo ""

# 验证关键依赖
print_step "验证关键依赖"

for package in django djangorestframework psycopg2-binary; do
    if python3 -c "import ${package//-/_}" 2>/dev/null; then
        print_success "$package 已安装"
    else
        print_warning "$package 未找到，尝试安装..."
        python3 -m pip install $package -q
    fi
done

echo ""

# 检查数据库
print_step "检查数据库"

# 检查 SQLite 数据库
if [ -f "db.sqlite3" ]; then
    print_success "SQLite 数据库存在"
    DB_TYPE="sqlite"
else
    print_warning "SQLite 数据库不存在，检查 PostgreSQL..."
    DB_TYPE="postgres"
fi

echo ""

# 执行迁移前的准备
print_step "数据库迁移前检查"

# 检查迁移文件
if [ -d "oj_videocourse/migrations" ]; then
    print_success "oj_videocourse 迁移目录存在"
else
    print_warning "oj_videocourse 迁移目录不存在，创建中..."
    mkdir -p oj_videocourse/migrations
    touch oj_videocourse/migrations/__init__.py
    print_success "迁移目录已创建"
fi

echo ""

# 清理混乱数据（如果使用 SQLite）
if [ "$DB_TYPE" = "sqlite" ]; then
    print_step "清理混乱数据"
    
    python3 manage.py shell << 'PYTHON_EOF'
import sys
try:
    from oj_course.models import CourseChapter
    
    print("清理前的数据统计:")
    total_before = CourseChapter.objects.count()
    print(f"  总 CourseChapter 数: {total_before}")
    
    if total_before > 0:
        print("\n📊 CourseChapter 分布:")
        for course_data in CourseChapter.objects.values('course_id').distinct():
            count = CourseChapter.objects.filter(
                course_id=course_data['course_id']
            ).count()
            print(f"  课程 {course_data['course_id']}: {count} 个章节")
    
    # 删除所有混乱的 CourseChapter
    print("\n⚠️  删除所有 CourseChapter...")
    CourseChapter.objects.all().delete()
    
    print("\n清理后的数据统计:")
    total_after = CourseChapter.objects.count()
    print(f"  总 CourseChapter 数: {total_after}")
    print(f"\n✓ 删除了 {total_before - total_after} 个混乱的章节")
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYTHON_EOF

    if [ $? -eq 0 ]; then
        print_success "数据清理完成"
    else
        print_error "数据清理失败"
        exit 1
    fi
else
    print_warning "PostgreSQL 模式，跳过 Django 数据清理"
    print_step "如需清理 PostgreSQL 数据，请执行:"
    echo "  psql -U postgres -h localhost -d oj -c 'DELETE FROM course_coursechapter;'"
fi

echo ""

# 执行迁移
print_step "执行数据库迁移"

print_step "步骤 1: 创建 oj_videocourse 迁移"
if python3 manage.py makemigrations oj_videocourse 2>&1 | tail -5; then
    print_success "迁移文件创建成功"
else
    print_warning "迁移文件创建失败或已存在"
fi

echo ""
print_step "步骤 2: 执行所有迁移"
if python3 manage.py migrate 2>&1 | tail -10; then
    print_success "迁移执行完成"
else
    print_error "迁移执行失败"
    exit 1
fi

echo ""

# 创建输出目录
print_step "创建输出目录"
mkdir -p ../judge_data/videocourse_output
chmod 755 ../judge_data/videocourse_output
print_success "输出目录已创建"

echo ""

# 最终验证
print_step "最终验证"

python3 manage.py shell << 'PYTHON_EOF'
import sys
try:
    from django.db import connection
    from oj_course.models import Course, CourseChapter
    from oj_videocourse.models import VideoCourse, VideoCourseChapter
    
    print("✓ Django 导入成功")
    print("✓ 数据库连接正常")
    
    print("\n📈 数据统计:")
    print(f"  直播课: {Course.objects.count()}")
    print(f"  直播课章节: {CourseChapter.objects.count()}")
    print(f"  录播课: {VideoCourse.objects.count()}")
    print(f"  录播课章节: {VideoCourseChapter.objects.count()}")
    
except Exception as e:
    print(f"✗ 验证失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYTHON_EOF

if [ $? -eq 0 ]; then
    print_success "最终验证通过"
else
    print_error "最终验证失败"
    exit 1
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    ✅ 所有步骤完成！                      ║"
echo "╚════════════════════════════════════════════════════════════╝"

echo ""
echo "下一步:"
echo "  1. 重启后端服务: systemctl restart wzyoj-backend"
echo "  2. 或使用 gunicorn: gunicorn oj_backend.wsgi:application --bind 0.0.0.0:8000"
echo "  3. 验证 API: curl http://localhost:8000/api/course-chapters/"
echo "             curl http://localhost:8000/api/video-courses/"

exit 0
