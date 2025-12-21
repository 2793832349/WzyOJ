�(# 班级管理功能使用指南

## 功能概述

班级管理系统已经基本实现，包含以下核心功能：

### ✅ 已完成功能

1. **班级管理**
   - 创建班级
   - 编辑班级信息
   - 删除班级
   - 班级列表查看（区分"我教的班级"和"我加入的班级"）

2. **成员管理**
   - 添加学生到班级
   - 移除学生
   - 查看班级成员列表
   - 区分教师和学生角色

3. **题目管理**
   - 引用主题库题目（计划实现）
   - 创建班级专属题目（计划实现）
   - 删除班级题目
   - 题目列表查看

4. **作业管理**
   - 创建作业
   - 设置截止时间
   - 删除作业
   - 作业列表查看
   - 隐藏/显示作业

## 快速开始

### 1. 访问班级页面

访问：`http://156.239.242.97/class/`

### 2. 创建班级（教师）

1. 点击"创建班级"按钮
2. 填写班级名称和描述
3. 选择是否隐藏
4. 点击"创建"

### 3. 添加学生

1. 进入班级详情页面
2. 切换到"学生管理"标签
3. 点击"添加学生"
4. 输入学生的用户ID
5. 点击"添加"

### 4. 创建作业

1. 进入班级详情页面
2. 在"作业"标签中点击"创建作业"
3. 填写作业标题、描述和截止时间
4. 点击"创建"

## API 接口

### 班级相关

- `GET /api/class/class/` - 获取班级列表
- `POST /api/class/class/` - 创建班级
- `GET /api/class/class/{id}/` - 获取班级详情
- `PUT /api/class/class/{id}/` - 更新班级信息
- `DELETE /api/class/class/{id}/` - 删除班级
- `GET /api/class/class/{id}/students/` - 获取班级学生列表
- `POST /api/class/class/{id}/add_student/` - 添加学生
- `POST /api/class/class/{id}/remove_student/` - 移除学生

### 题目相关

- `GET /api/class/class-problem/?class_id={id}` - 获取班级题目列表
- `POST /api/class/class-problem/` - 创建班级专属题目
- `POST /api/class/class-problem/reference/` - 引用主题库题目
- `DELETE /api/class/class-problem/{id}/` - 删除题目

### 作业相关

- `GET /api/class/assignment/?class_id={id}` - 获取作业列表
- `POST /api/class/assignment/` - 创建作业
- `GET /api/class/assignment/{id}/` - 获取作业详情
- `PUT /api/class/assignment/{id}/` - 更新作业
- `DELETE /api/class/assignment/{id}/` - 删除作业
- `GET /api/class/assignment/{id}/statistics/` - 获取作业统计

## 待完善功能

### 1. 题目功能
- [ ] 引用主题库题目的前端界面
- [ ] 创建班级专属题目的完整表单
- [ ] 题目详情页面
- [ ] 题目提交和判题（需要关联 submission 模块）

### 2. 作业功能
- [ ] 作业详情页面（显示包含的题目）
- [ ] 学生完成情况统计
- [ ] 排名功能
- [ ] 作业提交记录查看

### 3. 统计功能
- [ ] 学生提交统计
- [ ] 班级整体数据分析
- [ ] 导出成绩功能

### 4. 权限优化
- [ ] 更细粒度的权限控制
- [ ] 助教角色（可选）

## 数据库结构

### 核心表

1. **oj_class_class** - 班级表
   - title: 班级名称
   - description: 班级描述
   - teacher_id: 教师ID
   - is_hidden: 是否隐藏

2. **oj_class_classstudent** - 班级成员表
   - class_obj_id: 班级ID
   - user_id: 用户ID
   - role: 角色（teacher/student）

3. **oj_class_classproblem** - 班级题目表
   - class_obj_id: 班级ID
   - reference_problem_id: 引用的主题库题目ID（可选）
   - title: 题目标题（班级专属题目）
   - is_reference: 是否为引用题目

4. **oj_class_assignment** - 作业表
   - class_obj_id: 班级ID
   - title: 作业标题
   - deadline: 截止时间
   - is_hidden: 是否隐藏

5. **oj_class_assignmentproblem** - 作业题目关联表
   - assignment_id: 作业ID
   - problem_id: 题目ID
   - order: 顺序

## 使用建议

1. **创建班级后**，先添加学生成员
2. **添加题目**可以选择引用主题库或创建专属题目
3. **布置作业**时选择已有的班级题目
4. **设置截止时间**有助于学生时间管理
5. **使用统计功能**（待完善）查看学生完成情况

## 技术栈

### 后端
- Django 3.x
- Django REST Framework
- PostgreSQL

### 前端
- Vue 3
- Naive UI
- Axios

## 故障排查

### 如果页面无法访问
1. 检查后端容器是否运行：`docker ps | grep backend`
2. 检查前端容器是否运行：`docker ps | grep frontend`
3. 查看后端日志：`docker logs oj-backend`

### 如果 API 返回错误
1. 检查用户是否已登录
2. 检查用户权限（是否为班级教师）
3. 查看浏览器控制台的网络请求

### 如果数据库报错
1. 检查数据库容器：`docker ps | grep postgres`
2. 查看迁移状态：`docker exec oj-backend python3 manage.py showmigrations`

## 后续开发计划

1. **第一阶段**（已完成）
   - ✅ 数据库模型设计
   - ✅ 基础 API 接口
   - ✅ 基础前端页面

2. **第二阶段**（进行中）
   - 完善题目管理
   - 完善作业详情
   - 实现统计功能

3. **第三阶段**（计划中）
   - 成绩导出
   - 数据分析
   - 移动端适配

---

**开发时间**：2025年12月9日
**版本**：v1.0 基础版
�(*cascade082#file:///root/CLASS_FEATURE_GUIDE.md