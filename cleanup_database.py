#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 数据库自动清理脚本
用法: python cleanup_database.py [backup|clean|migrate|verify|all]
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
import argparse

# 颜色定义
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

def print_info(msg):
    print(f"ℹ {msg}")

class DatabaseCleaner:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.backend_dir = self.script_dir / 'backend'
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if not self.backend_dir.exists():
            print_error(f"找不到 backend 目录: {self.backend_dir}")
            sys.exit(1)
        
        os.chdir(str(self.backend_dir))
    
    def check_dependencies(self):
        """检查依赖"""
        print_step("检查依赖")
        
        # 检查 Django
        try:
            import django
            print_success("Django 已安装")
        except ImportError:
            print_error("Django 未安装")
            return False
        
        # 检查 PostgreSQL psql（可选）
        if shutil.which('psql'):
            print_success("PostgreSQL 已安装")
        else:
            print_warning("PostgreSQL 未找到（SQLite 模式可用）")
        
        return True
    
    def backup_database(self):
        """备份数据库"""
        print_step("备份数据库")
        
        sqlite_db = self.backend_dir / 'db.sqlite3'
        
        if sqlite_db.exists():
            print_info("检测到 SQLite 数据库")
            backup_file = sqlite_db.parent / f"db.sqlite3.backup_{self.timestamp}"
            shutil.copy2(str(sqlite_db), str(backup_file))
            print_success(f"SQLite 数据库已备份到: {backup_file}")
            return True
        else:
            print_info("未找到 SQLite 数据库，假设使用 PostgreSQL")
            return self._backup_postgresql()
    
    def _backup_postgresql(self):
        """备份 PostgreSQL 数据库"""
        db_name = input("输入数据库名称 [oj]: ").strip() or "oj"
        db_user = input("输入数据库用户 [postgres]: ").strip() or "postgres"
        db_host = input("输入数据库主机 [localhost]: ").strip() or "localhost"
        
        backup_file = f"oj_backup_{self.timestamp}.sql.gz"
        
        try:
            cmd = f'pg_dump -U {db_user} -h {db_host} {db_name} | gzip > {backup_file}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print_success(f"PostgreSQL 数据库已备份到: {backup_file}")
                return True
            else:
                print_error(f"备份失败: {result.stderr}")
                return False
        except Exception as e:
            print_error(f"备份异常: {e}")
            return False
    
    def clean_data(self):
        """清理混乱数据"""
        print_step("清理混乱数据")
        
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj_backend.settings')
        
        try:
            import django
            django.setup()
            
            from oj_course.models import CourseChapter
            
            print_info("清理前的数据统计:")
            total_before = CourseChapter.objects.count()
            print_info(f"  总 CourseChapter 数: {total_before}")
            
            if total_before > 0:
                print_info("\n📊 CourseChapter 分布:")
                for course_data in CourseChapter.objects.values('course_id').distinct():
                    count = CourseChapter.objects.filter(
                        course_id=course_data['course_id']
                    ).count()
                    print_info(f"  课程 {course_data['course_id']}: {count} 个章节")
            
            # 删除所有混乱的 CourseChapter
            print_info("\n⚠️  删除所有 CourseChapter...")
            CourseChapter.objects.all().delete()
            
            print_info("\n清理后的数据统计:")
            total_after = CourseChapter.objects.count()
            print_info(f"  总 CourseChapter 数: {total_after}")
            print_success(f"删除了 {total_before - total_after} 个混乱的章节")
            
            return True
        except Exception as e:
            print_error(f"数据清理失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_migrations(self):
        """执行迁移"""
        print_step("执行数据库迁移")
        
        # 步骤 1: 创建迁移
        print_info("步骤 1: 创建 oj_videocourse 迁移")
        result = subprocess.run(
            [sys.executable, 'manage.py', 'makemigrations', 'oj_videocourse'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print_success("迁移文件创建成功")
        else:
            print_warning(f"迁移创建信息: {result.stdout}")
        
        # 步骤 2: 执行 oj_videocourse 迁移
        print_info("步骤 2: 执行 oj_videocourse 迁移")
        result = subprocess.run(
            [sys.executable, 'manage.py', 'migrate', 'oj_videocourse'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print_success("oj_videocourse 迁移完成")
        else:
            print_error(f"oj_videocourse 迁移失败: {result.stderr}")
            return False
        
        # 步骤 3: 执行所有迁移
        print_info("步骤 3: 执行所有迁移")
        result = subprocess.run(
            [sys.executable, 'manage.py', 'migrate'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print_success("所有迁移完成")
            return True
        else:
            print_error(f"迁移失败: {result.stderr}")
            return False
    
    def create_directories(self):
        """创建输出目录"""
        print_step("创建输出目录")
        
        videocourse_dir = self.backend_dir / 'judge_data' / 'videocourse_output'
        videocourse_dir.mkdir(parents=True, exist_ok=True)
        
        print_success("输出目录创建完成")
        return True
    
    def verify_separation(self):
        """验证数据库分离"""
        print_step("验证数据库分离")
        
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj_backend.settings')
        
        try:
            import django
            django.setup()
            
            from django.db import connection
            from oj_course.models import Course, CourseChapter
            from oj_videocourse.models import VideoCourse, VideoCourseChapter
            
            print_info("\n📊 数据库表检查:")
            
            # 检查直播课表
            print_info("\n  直播课数据库表:")
            cursor = connection.cursor()
            try:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema='public' AND table_name LIKE 'course_%'
                """)
                for row in cursor.fetchall():
                    print_info(f"    ✓ {row[0]}")
            except Exception:
                print_info("    ℹ️  使用 SQLite 数据库")
            
            # 检查录播课表
            print_info("\n  录播课数据库表:")
            try:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema='public' AND table_name LIKE 'videocourse_%'
                """)
                for row in cursor.fetchall():
                    print_info(f"    ✓ {row[0]}")
            except Exception:
                print_info("    ℹ️  使用 SQLite 数据库")
            
            # 检查数据
            print_info("\n📈 数据统计:")
            print_info(f"  直播课: {Course.objects.count()}")
            print_info(f"  直播课章节: {CourseChapter.objects.count()}")
            print_info(f"  录播课: {VideoCourse.objects.count()}")
            print_info(f"  录播课章节: {VideoCourseChapter.objects.count()}")
            
            # 验证分离
            if CourseChapter.objects.count() == 0:
                print_success("混乱数据已清理（CourseChapter 为空）")
            else:
                print_warning(f"仍有 {CourseChapter.objects.count()} 个混乱的 CourseChapter")
            
            try:
                VideoCourseChapter.objects.count()
                print_success("录播课表创建成功")
            except Exception as e:
                print_error(f"录播课表问题: {e}")
            
            return True
        except Exception as e:
            print_error(f"验证失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def execute_all(self):
        """执行所有步骤"""
        print_step("开始完整数据库清理流程")
        
        steps = [
            ("检查依赖", self.check_dependencies),
            ("备份数据库", self.backup_database),
            ("清理数据", self.clean_data),
            ("执行迁移", self.run_migrations),
            ("创建目录", self.create_directories),
            ("验证分离", self.verify_separation),
        ]
        
        for step_name, step_func in steps:
            try:
                if not step_func():
                    print_error(f"{step_name}失败，中止执行")
                    return False
            except Exception as e:
                print_error(f"{step_name}异常: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        print_step("✅ 所有步骤完成！")
        print(f"{Colors.GREEN}")
        print("数据库现在已：")
        print("  ✓ 备份到文件")
        print("  ✓ 清理混乱数据")
        print("  ✓ 创建 oj_videocourse 表")
        print("  ✓ 直播课和录播课完全分离")
        print(f"\n下一步：重启服务并测试 API{Colors.END}")
        
        return True

def main():
    parser = argparse.ArgumentParser(
        description='数据库自动清理脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python cleanup_database.py              # 执行所有步骤
  python cleanup_database.py --backup     # 只备份
  python cleanup_database.py --clean      # 只清理
        """
    )
    
    parser.add_argument('--backup', action='store_true', help='只备份数据库')
    parser.add_argument('--clean', action='store_true', help='只清理混乱数据')
    parser.add_argument('--migrate', action='store_true', help='只执行迁移')
    parser.add_argument('--verify', action='store_true', help='只验证数据库分离')
    
    args = parser.parse_args()
    
    cleaner = DatabaseCleaner()
    
    if args.backup:
        return cleaner.backup_database()
    elif args.clean:
        return cleaner.clean_data()
    elif args.migrate:
        return cleaner.run_migrations()
    elif args.verify:
        return cleaner.verify_separation()
    else:
        return cleaner.execute_all()

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_error("\n用户中止执行")
        sys.exit(1)
    except Exception as e:
        print_error(f"执行异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
