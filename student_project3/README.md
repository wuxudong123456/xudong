# 学生管理系统

基于 FastAPI + SQLAlchemy + MySQL 构建的学生管理系统，提供学生信息管理、成绩管理、班级管理、教师管理和就业管理等功能。

## 项目结构

```
student_project3/
├── api/                 # API路由层
│   ├── student_info.py  # 学生管理API
│   ├── score.py         # 成绩管理API
│   ├── employee1.py     # 就业管理API
│   ├── teacher.py       # 教师管理API
│   └── class_info_api.py # 班级管理API
├── service/             # 业务逻辑层
├── dao/                 # 数据访问层
├── models/              # 数据库模型
├── schemas/             # 数据验证模型
├── frontend/            # 前端静态页面
├── main.py              # 应用入口
└── database.py          # 数据库配置
```

## 技术栈

- **框架**: FastAPI
- **数据库**: MySQL + SQLAlchemy ORM
- **前端**: HTML + CSS + JavaScript
- **部署**: Uvicorn

## 环境要求

- Python 3.8+
- MySQL 5.7+

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env` 文件并修改数据库连接信息：

```bash
# 数据库配置
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=student

# 服务配置
HOST=127.0.0.1
PORT=8000
```

### 3. 创建数据库

在 MySQL 中创建数据库：

```sql
CREATE DATABASE student CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 启动服务

```bash
python main.py
```

### 5. 访问地址

- API文档: http://localhost:8000/docs
- 前端首页: http://localhost:8000/static/index.html

## API模块

| 模块 | 路径 | 功能 |
|------|------|------|
| 学生管理 | `/student/` | 学生信息增删改查 |
| 成绩管理 | `/score/` | 成绩信息管理 |
| 就业管理 | `/employment/` | 就业信息管理 |
| 教师管理 | `/teacher/` | 教师信息管理 |
| 班级管理 | `/class/` | 班级信息管理 |

## 前端页面

| 页面 | 路径 |
|------|------|
| 首页 | `/static/index.html` |
| 学生管理 | `/static/students.html` |
| 成绩管理 | `/static/score.html` |
| 就业管理 | `/static/employment.html` |
| 教师管理 | `/static/teacher.html` |
| 班级管理 | `/static/class.html` |

## 项目架构

```
┌─────────────────────────────────────────────────────┐
│                    Frontend                         │
│   (HTML/CSS/JavaScript - 静态页面)                  │
└────────────────────┬────────────────────────────────┘
                     │ HTTP请求
                     ▼
┌─────────────────────────────────────────────────────┐
│                    API Layer                        │
│   (FastAPI 路由 - 处理请求/响应)                    │
└────────────────────┬────────────────────────────────┘
                     │ 调用服务方法
                     ▼
┌─────────────────────────────────────────────────────┐
│                   Service Layer                     │
│   (业务逻辑处理 - 数据校验/业务规则)                 │
└────────────────────┬────────────────────────────────┘
                     │ 调用DAO方法
                     ▼
┌─────────────────────────────────────────────────────┐
│                    DAO Layer                        │
│   (数据访问层 - SQLAlchemy 操作)                    │
└────────────────────┬────────────────────────────────┘
                     │ SQL查询
                     ▼
┌─────────────────────────────────────────────────────┐
│                    Database                         │
│   (MySQL - 存储数据)                                │
└─────────────────────────────────────────────────────┘
```

## 核心功能

1. **学生管理**: 学生信息的增删改查、分页查询、条件搜索
2. **成绩管理**: 成绩录入、修改、查询、统计分析
3. **班级管理**: 班级信息管理、学生关联
4. **教师管理**: 教师信息管理、课程分配
5. **就业管理**: 就业信息录入、薪资统计、班级就业分析

## 开发规范

- 使用 Pydantic 进行数据验证
- 使用 SQLAlchemy ORM 进行数据库操作
- 遵循 RESTful API 设计规范
- 使用环境变量管理敏感配置