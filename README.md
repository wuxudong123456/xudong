# 学生管理系统 + 猪八戒多智能体 AI 问答

## 项目简介

企业级前后端分离学生管理系统，内嵌猪八戒拟人多智能体 AI 应用。以四大名著（《西游记》《三国演义》《红楼梦》《水浒传》）为知识库，结合 NL2SQL 业务数据查询，打造集教务管理与 AI 智能问答于一体的综合性平台。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Python 3.10+ / FastAPI |
| ORM | SQLAlchemy 2.0 |
| 数据库 | MySQL 8.0 (库名: `student-mananger`) |
| 向量数据库 | Milvus 2.4 (端口: 19530) |
| AI 模型 | DeepSeek API (OpenAI 兼容) |
| 前端框架 | Vue 3.5 + Composition API |
| UI 组件库 | Element Plus 2.9 |
| 状态管理 | Pinia 2.3 |
| 图表可视化 | ECharts 5.5 |
| 认证 | JWT (python-jose) + bcrypt |
| Excel 处理 | openpyxl |

## 项目架构

```
┌──────────────────────────────────────────────────────┐
│                    Frontend (Vue3)                    │
│   Login │ Dashboard │ CRUD页面 │ 八戒AI │ 知识问答  │
└──────────────────┬───────────────────────────────────┘
                   │ HTTP/REST + SSE
┌──────────────────▼───────────────────────────────────┐
│               Backend (FastAPI)                       │
│                                                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────────┐  │
│  │ Controller│ │ Service  │ │   Multi-Agent        │  │
│  │ (薄层)    │ │ (业务)   │ │ ┌──────────────────┐ │  │
│  │           │ │          │ │ │ IntentClassifier │ │  │
│  │ auth      │ │ auth     │ │ │ NL2SQL │ RAG     │ │  │
│  │ student   │ │ student  │ │ │ Bajie  │ Emotion │ │  │
│  │ class     │ │ score    │ │ │ Social │ Poetry  │ │  │
│  │ score     │ │ rag      │ │ └──────────────────┘ │  │
│  │ ...       │ │ agent    │ └──────────────────────┘  │
│  └──────────┘ └────┬─────┘                            │
│                     │                                  │
│  ┌──────────┐ ┌─────▼──────┐ ┌──────────────────┐   │
│  │  DAO     │ │  Database   │ │  Milvus (向量库) │   │
│  │ (数据层) │ │  MySQL      │ │  4个Collection   │   │
│  └──────────┘ └────────────┘ └──────────────────┘   │
└──────────────────────────────────────────────────────┘
```

### 多智能体架构

采用**路由+专家模式**，通过 IntentClassifier 分类意图后路由到对应的专家 Agent：

| Agent | 职责 | 核心能力 |
|-------|------|----------|
| **IntentClassifier** | 意图分类 | 识别 7 种用户意图，路由到对应 Agent |
| **BusinessManagementAgent** | 数据查询 | NL2SQL 生成 SQL + 安全校验 + 只读执行 |
| **RAGKnowledgeAgent** | 四大名著问答 | 跨 4 个 Milvus 集合检索 + DeepSeek 生成 |
| **BajiePersonaAgent** | 角色扮演 | 八戒人设对话，默认兜底 |
| **EmotionalCounselingAgent** | 情绪疏导 | 共情五步法，深夜关怀 |
| **SocialAssistantAgent** | 社交僚机 | 话术生成、情书代写 |

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- MySQL 8.0 (root/123456, 数据库: `student-mananger`)
- Milvus 2.4 (127.0.0.1:19530)
- DeepSeek API Key

### 1. 安装后端依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
# 创建所有表 + 种子数据（角色权限、超级管理员等）
python scripts/init_db.py
```

### 3. 导入四大名著知识库

```bash
# 初始化 Milvus 四大名著集合
python scripts/init_milvus.py

# 导入全文（全部四本约280万字，预计30-60分钟）
python scripts/ingest_novel.py

# 或仅导入某一本
python scripts/ingest_novel.py --novel sanguo
```

### 4. 启动后端

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

访问 http://localhost:8000/docs 查看 Swagger API 文档。

### 5. 安装并启动前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173 进入系统。

## 登录账号

```
超级管理员:  super_admin / admin123   (拥有全部权限)
管理员:      admin1      / 123456     (管理权限)
教师:        teacher1    / 123456     (教学相关权限)
学生:        student1    / 123456     (查看权限)
```

## 功能模块

### 业务管理
| 模块 | 功能 | 权限码 |
|------|------|--------|
| 数据看板 | 总览统计、ECharts 可视化图表 | — |
| 学生管理 | 增删改查、模糊检索、Excel 导入导出、批量删除 | `student:*` |
| 班级管理 | 班级 CRUD、学生人数统计 | `class:*` |
| 成绩管理 | 成绩录入/编辑、统计分析、Excel 导入导出 | `score:*` |
| 就业管理 | 就业信息管理、就业率统计 | `employment:*` |
| 课程管理 | 课程信息 CRUD | `course:*` |
| 操作日志 | 多维度筛选查询 | `log:view` |
| 用户管理 | 用户 CRUD、角色管理、密码重置 | `user:manage` |

### AI 智能体
| 模块 | 功能 | 说明 |
|------|------|------|
| 八戒对话 | 猪八戒角色扮演聊天 | SSE 流式对话 |
| 四大名著问答 | RAG 知识检索 + DeepSeek 生成 | 支持章节溯源 |
| 八戒游戏 | 灯谜 (50+题) + 飞花令诗词对句 | 积分统计 |
| 社交助手 | 聊天话术生成 + 情书代写 | 社交僚机 |
| 情绪疏导 | 共情五步法 + 深夜关怀 | 心理抚慰 |

### RBAC 权限体系

系统包含 28 个细粒度权限码，覆盖 9 大模块的 view/create/update/delete/import/export 操作。超级管理员拥有全部权限，管理员/教师/学生按角色分配。

## API 路由一览

| 前缀 | 模块 | 主要端点 |
|------|------|----------|
| `/api/v1/auth` | 认证 | POST /login, GET /me, PUT /me/password |
| `/api/v1/students` | 学生管理 | CRUD + /batch-delete + /export + /import |
| `/api/v1/classes` | 班级管理 | CRUD |
| `/api/v1/scores` | 成绩管理 | CRUD + /stats + /export + /import |
| `/api/v1/employment` | 就业管理 | CRUD + /stats |
| `/api/v1/courses` | 课程管理 | CRUD |
| `/api/v1/logs` | 操作日志 | GET / |
| `/api/v1/users` | 用户管理 | CRUD + /reset-password |
| `/api/v1/dashboard` | 仪表盘 | GET /overview, /class-distribution, /score-trend |
| `/api/v1/rag` | 四大名著问答 | GET /qa, GET /qa/stream, GET /collection-info |
| `/api/v1/bajie` | 八戒功能 | /riddle, /poetry, /chat, /emotional, /chat-lines, /love-letter |
| `/api/v1/agent` | 多智能体 | POST /chat, POST /chat/stream, POST /classify |
| `/api/v1/system` | 系统 | GET /health |

## 目录结构

```
├── .env                     # 环境变量
├── .gitignore               # Git忽略规则
├── requirements.txt         # Python依赖
├── README.md                # 项目文档
├── code_review_result.md    # 代码审查报告
├── 《西游记》(1).txt         # 西游记全文 (83万字)
├── 《三国演义》(1).txt       # 三国演义全文 (65万字)
├── 《红楼梦》(1).txt         # 红楼梦全文 (100万字)
├── 《水浒传》(1).txt         # 水浒传全文 (100万字)
│
├── backend/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置管理
│   ├── database.py          # SQLAlchemy 引擎
│   ├── dependencies.py      # JWT/RBAC 依赖注入
│   ├── entity/              # ORM 模型 (15个实体)
│   ├── dao/                 # 数据访问层
│   ├── service/             # 业务逻辑层
│   ├── controller/          # 接口控制层 (12个模块)
│   ├── middleware/          # 中间件
│   ├── schema/              # Pydantic 请求/响应
│   ├── utils/               # 工具类
│   └── data/                # 静态数据 (人设/灯谜)
│
├── frontend/
│   └── src/
│       ├── main.js          # Vue 入口
│       ├── App.vue          # 根组件
│       ├── router/          # 路由 + 权限守卫
│       ├── store/           # Pinia 状态管理
│       ├── api/             # Axios 封装 (10个模块)
│       ├── components/      # 公共组件
│       └── views/           # 页面 (14个页面)
│
└── scripts/
    ├── init_db.py           # 数据库初始化
    ├── hash_passwords.py    # 密码哈希迁移
    ├── init_milvus.py       # Milvus 集合初始化
    └── ingest_novel.py      # 四大名著全文导入
```

## 部署建议

### 生产环境

```bash
# 后端 (Gunicorn + Uvicorn workers)
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

# 前端 (Nginx 静态部署)
cd frontend && npm run build
# 将 dist/ 目录部署到 Nginx，配置反向代理 /api 到后端
```

### 环境变量检查清单

- [ ] DB_USER / DB_PASSWORD / DB_NAME 指向正确的 MySQL
- [ ] DEEPSEEK_API_KEY 有效且有足够额度
- [ ] MILVUS_HOST / MILVUS_PORT 指向运行中的 Milvus
- [ ] JWT_SECRET_KEY 在生产环境使用随机强密钥
- [ ] CORS_ORIGINS 配置正确的域名

## 开发说明

### 后端代码规范

- 严格四层架构：Entity → DAO → Service → Controller
- Controller 薄层，不写业务逻辑
- 全局异常处理，统一 `{code, message, data}` 响应格式
- 所有数据操作包含 `is_deleted = 0` 软删除过滤
- 敏感配置从 .env 读取，不硬编码

### 前端代码规范

- Vue 3 Composition API + `<script setup>` 语法
- 路由权限守卫 + 按钮级 `v-if` 权限控制
- API 调用经 Axios 拦截器统一处理 401/403
- 使用 Element Plus 中文语言包

## 许可证

本项目仅用于教育目的。
