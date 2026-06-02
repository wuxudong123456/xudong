# 学生管理系统 + 猪八戒多智能体AI平台 完整技术文档

> **项目名称**: 学生管理系统 + 猪八戒多智能体AI问答平台
> **文档版本**: v2.0.0
> **文档日期**: 2026-06-01
> **文档状态**: 完整技术文档，基于全项目文件浏览 + 全对话历史综合生成
> **涵盖范围**: 项目概述 / 系统架构 / 文件清单 / 功能矩阵 / 多智能体架构 / 记忆框架 / 核心能力诊断 / 功能增强方案 / 前端布局升级 / 角色动图动画 / 实施路线图 / Claude提示词 / 风险与注意事项

---

## 目录

1. [项目概述](#1-项目概述)
2. [系统架构](#2-系统架构)
3. [完整文件清单](#3-完整文件清单)
4. [当前已实现功能矩阵](#4-当前已实现功能矩阵)
5. [多智能体协同架构详解](#5-多智能体协同架构详解)
6. [记忆框架详解](#6-记忆框架详解)
7. [八项核心能力诊断](#7-八项核心能力诊断)
8. [七大功能增强方案](#8-七大功能增强方案)
9. [前端布局升级方案](#9-前端布局升级方案)
10. [角色动图过渡动画方案](#10-角色动图过渡动画方案)
11. [完整实施路线图](#11-完整实施路线图)
12. [Claude提示词汇总](#12-claude提示词汇总)
13. [风险与注意事项](#13-风险与注意事项)
14. [对话历史全记录](#14-对话历史全记录)

---

## 1. 项目概述

### 1.1 项目定位

**学生管理系统 + 猪八戒多智能体AI问答平台** 是一个融合型Web应用，将传统学生信息管理系统（CRUD/数据看板/智能问数）与四大名著角色AI（猪八戒/鲁智深/林黛玉/诸葛亮）无缝整合在同一平台中。平台支持多角色智能对话、RAG知识问答、灯谜/飞花令游戏、知识图谱可视化、语音交互、主动对话、个性化学习推荐等功能。

### 1.2 项目初始创意与构思

| 构思 | 描述 |
|------|------|
| **角色IP融合** | 以猪八戒为核心IP，融合鲁智深、林黛玉、诸葛亮四大名著经典角色，每人有独立人设、口吻、知识背景 |
| **人设系统** | 每个角色配置emoji、头像、名言、性格描述、说话风格、专属提示词，通过`system_prompts.py`统一管理 |
| **多智能体协同** | 8个专家Agent（数据/知识/情绪/社交/游戏/角色/天气/运势）+ 编排器 + ReAct推理 + 学习推荐 |
| **记忆框架** | LLM自动提取用户关键信息 → 去重 → 向量化 → 双写MySQL+Milvus → 检索注入system prompt |
| **四大名著知识库** | 四本原著全文导入Milvus向量库，支持跨书联合检索 + 智能书籍路由 + 图谱融合查询 |
| **古典视觉主题** | 朱红/黛蓝/墨黑/宣纸黄/金色/竹青/石青/藕荷 八大古典色系，楷体标题 + 印章按钮 + 宣纸卡片 |
| **语音多模态** | 前端录音/播放组件 + 后端阿里云TTS/ASR接口，支持"能听能说" |
| **主动对话** | 基于SSE的AI主动搭话推送，模拟角色"想找人聊天"的趣味体验 |
| **知识图谱** | Neo4j人物关系图谱 + ECharts力导向图可视化，支持人物查询/关系路径/阵营分析/因果推理 |

### 1.3 完整技术栈

| 层级 | 技术 | 版本 | 用途 |
|------|------|------|------|
| **前端框架** | Vue 3 (Composition API) + Vite | 3.5+ / 6.0+ | SPA 单页应用 |
| **UI组件库** | Element Plus | 2.9+ | 全局UI组件，中文语言包 |
| **状态管理** | Pinia | 2.3+ | auth认证模块 + character角色模块(规划) |
| **路由** | Vue Router 4 (Hash模式) | 4.5+ | 16个路由 + 全局权限守卫 |
| **图表** | ECharts | 5.5+ | 仪表盘4图表 + 知识图谱力导向图 |
| **HTTP客户端** | Axios | 1.7+ | API请求封装，自动注入JWT |
| **CSS预处理** | SCSS | 1.83+ | 古典主题变量系统 + Element Plus全局覆盖 |
| **图标** | @element-plus/icons-vue | 2.3+ | 全局注册Element Plus图标 |
| **自动导入** | unplugin-auto-import / unplugin-vue-components | 0.18+ | Element Plus按需导入 |
| **后端框架** | FastAPI | 0.115+ | RESTful + SSE流式 |
| **ORM** | SQLAlchemy | 2.0+ | MySQL数据库操作 |
| **数据库** | MySQL (PyMySQL) | - | 业务数据 + 对话记忆存储 |
| **向量数据库** | Milvus (pymilvus) | 2.4+ | 四大名著文本向量 + 记忆片段向量 |
| **图数据库** | Neo4j | 5.28+ | 四大名著人物关系图谱 |
| **LLM** | DeepSeek API (OpenAI兼容) | deepseek-chat | 对话生成/意图分类/记忆提取/SQL生成 |
| **Embedding** | DeepSeek text-embedding-3-small | - | 文本向量化 |
| **备用LLM** | 阿里云 DashScope (Qwen) | qwen-turbo | 备用对话模型 |
| **TTS** | 阿里云 DashScope | sambert-zhichu | 文本转语音 |
| **ASR** | 阿里云 DashScope | qwen-audio-asr | 语音转文本 |
| **认证** | JWT (python-jose + passlib) | HS256 | access_token(120min) + refresh_token(7天) |
| **配置** | Pydantic Settings (.env) | - | 环境变量统一管理 |
| **天气API** | 和风天气 | - | 实时天气查询 |
| **机器学习** | scikit-learn (规划) | - | 朴素贝叶斯意图分类 + BKT知识追踪 |

---

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        前端 (Vue 3 + Vite + Element Plus)             │
│                                                                       │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌──────────────────┐   │
│  │AppLayout │  │ Sidebar  │  │HeaderBar  │  │   16 Views       │   │
│  │ 主布局    │  │ 12菜单    │  │ 面包屑用户  │  │   Dashboard      │   │
│  │ +TabBar  │  │ +Logo    │  │ +全屏通知  │  │   StudentList    │   │
│  │ +过渡动画 │  │ +底部用户 │  │           │  │   ClassList      │   │
│  └──────────┘  └──────────┘  └───────────┘  │   ScoreList      │   │
│                                               │   EmploymentList │   │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  │   CourseList     │   │
│  │VoiceInput│  │VoiceOutput│  │GraphView  │  │   OperationLogs  │   │
│  │ 录音按钮  │  │ 播放按钮  │  │ECharts图谱 │  │   UserManage     │   │
│  └──────────┘  └──────────┘  └───────────┘  │   BajieChat      │   │
│                                               │   KnowledgeQA    │   │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  │   BajieGames     │   │
│  │SmartQuery│  │ Pinia    │  │ Axios 14  │  │   SocialAssistant│   │
│  │NL2SQL输入 │  │Auth Store│  │ API模块   │  │   Login          │   │
│  └──────────┘  └──────────┘  └───────────┘  └──────────────────┘   │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │           Classical Theme SCSS (八大古典色系)                      │ │
│  │  variables.scss + classical.scss + global.scss                  │ │
│  └────────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTP REST / SSE
┌────────────────────────────▼────────────────────────────────────────┐
│                        后端 FastAPI (Python)                          │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │    main.py → 生命周期管理(lifespan) → CORS → 全局异常处理       │   │
│  │    config.py → Pydantic Settings (.env)                        │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    18 Controller (路由层)                       │   │
│  │  agent / auth / audio / bajie / class / course / dashboard    │   │
│  │  employment / fortune / graph / log / memory / proactive      │   │
│  │  rag / score / smart_query / student / user / weather         │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                   Agent 编排层 (16个文件)                        │   │
│  │                                                                  │   │
│  │  OrchestratorAgent (核心编排器)                                  │   │
│  │  ├── execute() → Function Calling → 任务分解 → 并行 → 单Agent   │   │
│  │  ├── execute_single() → 原路由表 (一行未删,作为fallback)        │   │
│  │  ├── _execute_function_calling() → LLM自主决定调用工具(3轮)     │   │
│  │  ├── _execute_parallel() → asyncio.gather 并行执行              │   │
│  │  ├── _merge_results() → LLM合并多Agent结果                      │   │
│  │  └── AgentMessageBus → Agent间消息总线                           │   │
│  │                                                                  │   │
│  │  8个专家Agent:                                                   │   │
│  │  DataAgent / KnowledgeAgent / EmotionalAgent / SocialAgent      │   │
│  │  GameAgent / PersonaAgent / WeatherAgent / FortuneAgent         │   │
│  │                                                                  │   │
│  │  扩展Agent:                                                      │   │
│  │  ReactAgent (ReAct推理循环) / RecommendationAgent (学习推荐)    │   │
│  │                                                                  │   │
│  │  基础设施:                                                        │   │
│  │  BaseAgent (抽象基类) / TaskDecomposer (任务分解器)              │   │
│  │  ToolRegistry (工具注册表,单例) / system_prompts (角色人设)      │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    Service 层 (20个文件)                         │   │
│  │  agent_service (意图分类+编排入口+SSE流式)                      │   │
│  │  rag_service (Milvus检索+图谱融合+书籍路由)                     │   │
│  │  graph_service (Neo4j人物查询+关系+路径+可视化)                 │   │
│  │  graph_reasoning (因果链+阵营分析+事件时间线+深度问答)          │   │
│  │  nl2sql_service (自然语言→SQL→安全校验→执行)                    │   │
│  │  memory_service (会话管理+消息存取+历史检索)                     │   │
│  │  proactive_service (主动搭话+定时检测)                           │   │
│  │  bayesian_classifier (朴素贝叶斯意图分类+自我学习)              │   │
│  │  bkt_service (贝叶斯知识追踪+掌握概率计算)                      │   │
│  │  recommendation_service (薄弱点诊断+LLM学习计划生成)            │   │
│  │  其他: auth/bajie/class/course/dashboard/employment/           │   │
│  │        fortune/score/student/weather                           │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                     Utils 层 (20个文件)                          │   │
│  │  deepseek_util (chat+stream) / qwen_util (备用LLM)             │   │
│  │  embedding_util (向量嵌入) / llm_router (LLM路由切换)          │   │
│  │  milvus_util (向量库操作) / neo4j_util (图库操作)              │   │
│  │  tts_util (阿里云TTS) / asr_util (阿里云ASR)                   │   │
│  │  memory_extractor (LLM提取→去重→向量化→双写)                   │   │
│  │  memory_retriever (Milvus语义+MySQL结构化+排序衰减)            │   │
│  │  book_router (四大名著书籍智能路由)                              │   │
│  │  weather_util (和风天气) / fortune_util (运势)                 │   │
│  │  jwt_util / password_util / excel_util / text_chunker          │   │
│  │  logger / response_util                                        │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐                    │
│  │ Entity │  │ Schema │  │  DAO   │  │Middleware│                   │
│  │15个ORM │  │Pydantic│  │数据访问 │  │异常处理  │                   │
│  └────────┘  └────────┘  └────────┘  └────────┘                    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
   ┌──────────┐        ┌──────────┐        ┌──────────┐
   │  MySQL   │        │  Milvus  │        │  Neo4j   │
   │ 业务+记忆 │        │ 向量检索  │        │ 人物图谱  │
   └──────────┘        └──────────┘        └──────────┘
        │                    │                    │
        ▼                    ▼                    ▼
   ┌─────────────────────────────────────────────────────┐
   │                   外部 API 调用                       │
   │  DeepSeek (LLM+Embedding)                            │
   │  阿里云 DashScope (TTS+ASR+备用Qwen)                 │
   │  和风天气 (实时天气)                                  │
   └─────────────────────────────────────────────────────┘
```

### 2.2 数据流向图

```
用户输入 (文字/语音)
    │
    ▼
┌─────────────────────────────────────────────────────┐
│                 前端处理层                            │
│  VoiceInput.vue (录音→blob→后端ASR→text)             │
│  BajieChat.vue (文字输入→SSE流式→打字机效果渲染)       │
│  SmartQueryInput.vue (NL2SQL自然语言→表格展示)        │
│  GraphView.vue (图谱JSON→ECharts力导向图渲染)        │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP POST/GET + SSE
                       ▼
┌─────────────────────────────────────────────────────┐
│                 后端处理层                            │
│                                                       │
│  1. agent_controller.py 接收请求                       │
│  2. agent_service.py → classify_intent_hybrid()       │
│     ├── 贝叶斯前置分类 (置信度≥0.85直接用)              │
│     └── LLM回退分类 (置信度<0.85时DeepSeek分类)        │
│  3. OrchestratorAgent.execute()                       │
│     ├── Function Calling (data_query/knowledge_question)│
│     ├── 任务分解 (TaskDecomposer.decompose)             │
│     ├── 并行执行 (_execute_parallel)                   │
│     └── 单Agent路由 (execute_single)                   │
│  4. 记忆提取 (MemoryExtractor, fire-and-forget)        │
│  5. 对话存档 (MemoryService.save_exchange)             │
│                                                       │
│  返回: SSE流式 / JSON同步 → 前端渲染                    │
└─────────────────────────────────────────────────────┘
```

---

## 3. 完整文件清单

### 3.1 前端完整文件清单 (frontend/)

```
frontend/
├── index.html                              # HTML入口文件
├── package.json                            # 项目依赖 (vue3/pinia/element-plus/echarts)
├── vite.config.js                          # Vite构建配置 + 代理转发
├── package-lock.json                       # 依赖锁定文件
│
└── src/
    ├── main.js                             # Vue3应用入口 (Pinia+Router+ElementPlus+全局样式)
    ├── App.vue                             # 根组件 (<router-view />)
    │
    ├── router/
    │   └── index.js                        # 路由配置 (16个路由+全局权限守卫)
    │
    ├── store/
    │   └── modules/
    │       └── auth.js                     # Pinia认证Store (token/userInfo/permissions)
    │   # character.js                      # [规划] 全局角色Store (activeCharacter/GIF)
    │
    ├── api/                                # 14个API模块
    │   ├── request.js                      # Axios基类封装 (baseURL/api/v1, JWT注入, 统一错误处理)
    │   ├── agent.js                        # 多智能体对话 (SSE流式+非流式)
    │   ├── audio.js                        # 语音识别/合成
    │   ├── auth.js                         # 认证 (登录/登出/刷新Token/修改密码)
    │   ├── bajie.js                        # 八戒功能 (灯谜/飞花令/社交/情绪)
    │   ├── class.js                        # 班级管理 CRUD
    │   ├── course.js                       # 课程管理 CRUD
    │   ├── dashboard.js                    # 仪表盘统计图表数据
    │   ├── employment.js                   # 就业管理 CRUD
    │   ├── graph.js                        # 知识图谱 (人物查询/关系路径/可视化数据)
    │   ├── log.js                          # 操作日志查询
    │   ├── memory.js                       # 记忆管理 (会话列表/历史/创建/删除)
    │   ├── score.js                        # 成绩管理 CRUD
    │   ├── student.js                      # 学生管理 CRUD+导入导出
    │   └── user.js                         # 用户管理 CRUD
    │
    ├── assets/
    │   ├── gifs/                           # [规划] 角色GIF动图目录
    │   │   ├── bajie.gif                   # 猪八戒吃西瓜/背媳妇
    │   │   ├── luzhishen.gif               # 鲁智深倒拔垂杨柳/喝酒
    │   │   ├── lindaiyu.gif                # 林黛玉葬花/抚琴
    │   │   └── zhugeliang.gif              # 诸葛亮摇扇/抚琴
    │   └── styles/
    │       ├── variables.scss              # 古典色彩系统+排版+间距+阴影+Mixins
    │       ├── classical.scss              # Element Plus全局覆盖 (宣纸背景/印章按钮/金色滚动条)
    │       └── global.scss                 # Body背景色
    │
    ├── components/
    │   ├── layout/                         # 布局组件
    │   │   ├── AppLayout.vue              # 主布局 (侧边栏+TabBar+顶栏+主内容+fade-slide过渡)
    │   │   ├── Sidebar.vue                # 侧边导航 (Logo+12菜单项+底部用户区+折叠)
    │   │   └── HeaderBar.vue              # 顶部栏 (折叠按钮+面包屑+用户下拉)
    │   ├── voice/                          # 语音组件
    │   │   ├── VoiceInput.vue             # 录音按钮 (MediaRecorder API+15秒倒计时)
    │   │   └── VoiceOutput.vue            # 播放按钮 (浏览器TTS优先+后端TTS回退)
    │   ├── GraphView.vue                   # ECharts知识图谱力导向图
    │   └── SmartQueryInput.vue             # 智能问数NL2SQL输入组件
    │
    └── views/                              # 16个页面视图
        ├── Login.vue                       # 登录页 (4种预设账号一键填充)
        ├── Dashboard.vue                   # 仪表盘 (5统计卡片+4 ECharts图表)
        ├── student/
        │   └── StudentList.vue             # 学生管理 (搜索+分页+CRUD+Excel导入导出+批量删除)
        ├── class/
        │   └── ClassList.vue               # 班级管理 (CRUD+分页)
        ├── score/
        │   └── ScoreList.vue               # 成绩管理 (按学号考试查询+CRUD)
        ├── employment/
        │   └── EmploymentList.vue          # 就业管理 (CRUD+班级筛选)
        ├── course/
        │   └── CourseList.vue              # 课程管理 (CRUD)
        ├── logs/
        │   └── OperationLogs.vue           # 操作日志 (操作人/类型/时间筛选)
        ├── system/
        │   └── UserManage.vue              # 用户管理 (CRUD+角色权限)
        └── bajie/                          # 猪八戒AI模块
            ├── BajieChat.vue               # 八戒对话 (4角色切换+SSE流式+记忆+语音+主动对话)
            ├── KnowledgeQA.vue             # 知识问答 (四大名著RAG检索)
            ├── BajieGames.vue              # 八戒游戏 (灯谜+飞花令)
            └── SocialAssistant.vue         # 社交助手 (社交话术/情书)
```

### 3.2 后端完整文件清单 (backend/)

```
backend/
├── main.py                                 # FastAPI应用入口
│   ├── lifespan (启动:建表→检查Milvus→检查Neo4j; 关闭:释放连接池)
│   ├── CORS中间件 (localhost:5173/3000)
│   ├── 全局异常处理 (HTTP/参数验证/通用)
│   └── 18个路由注册
│
├── config.py                               # Pydantic Settings (.env配置)
│   ├── MySQL (user/password/host/port/name)
│   ├── DeepSeek API (key/url/model/embedding_model)
│   ├── 阿里云DashScope (key/url/chat_model/embedding_model/tts_model/asr_model)
│   ├── Milvus (host/port)
│   ├── Neo4j (uri/user/password)
│   ├── JWT (secret_key/algorithm/expire)
│   ├── 应用 (name/version/debug)
│   ├── 文件上传 (dir/max_size)
│   └── CORS Origins + 和风天气API Key
│
├── database.py                             # SQLAlchemy配置
│   └── 连接池(pool_size=20, max_overflow=40) + get_db依赖注入
│
├── dependencies.py                         # FastAPI依赖注入
│   └── get_db() + get_current_user()
│
├── controller/                             # 18个控制器
│   ├── agent_controller.py                 # 多智能体编排 (POST /chat + /chat/stream + /classify)
│   ├── auth_controller.py                  # 认证 (login/logout/refresh/change_password)
│   ├── student_controller.py               # 学生管理 CRUD + 导入导出
│   ├── class_controller.py                 # 班级管理 CRUD
│   ├── score_controller.py                 # 成绩管理 CRUD + 统计
│   ├── employment_controller.py            # 就业管理 CRUD + 统计
│   ├── course_controller.py                # 课程管理 CRUD
│   ├── log_controller.py                   # 操作日志查询
│   ├── dashboard_controller.py             # 仪表盘 (统计卡片+图表数据)
│   ├── user_controller.py                  # 用户管理 (CRUD+角色权限)
│   ├── rag_controller.py                   # RAG四大名著知识问答
│   ├── bajie_controller.py                 # 八戒功能 (灯谜/飞花令/社交/情绪)
│   ├── graph_controller.py                 # 知识图谱 (人物查询/关系/可视化)
│   ├── smart_query_controller.py           # 智能问数 (NL2SQL)
│   ├── memory_controller.py                # 记忆管理 (会话CRUD+历史)
│   ├── proactive_controller.py             # 主动对话SSE
│   ├── audio_controller.py                 # 语音交互 (recognize/synthesize)
│   ├── weather_controller.py               # 天气查询
│   └── fortune_controller.py               # 运势占卜
│
├── service/                                # 20个服务层
│   ├── agent_service.py                    # 多智能体编排服务 (意图分类+编排入口+SSE流式)
│   │   ├── classify_intent()              # DeepSeek LLM意图分类 (9种意图)
│   │   ├── classify_intent_hybrid()       # 贝叶斯前置+LLM回退混合分类
│   │   └── AgentService.process_message() # 编排入口
│   │   └── AgentService.process_message_stream() # SSE流式入口
│   ├── auth_service.py                     # 认证服务 (JWT生成/验证)
│   ├── bajie_service.py                    # 八戒功能业务
│   ├── bayesian_classifier.py              # 朴素贝叶斯意图分类器
│   │   ├── BayesianClassifier             # MultinomialNB + TF-IDF (char_wb, 1-3 gram)
│   │   ├── classify()                     # 分类→(intent, confidence)
│   │   ├── add_sample()                   # 增量训练
│   │   ├── _retrain()                     # 累计20条自动重训练
│   │   └── 种子关键词兜底                  # conversation_history无数据时使用
│   ├── bkt_service.py                      # 贝叶斯知识追踪服务
│   │   └── calculate_mastery_probability() # P(掌握) = P_known + (1-P_known)*P_learn
│   ├── class_service.py                    # 班级管理业务
│   ├── course_service.py                   # 课程管理业务
│   ├── dashboard_service.py                # 仪表盘统计业务
│   ├── employment_service.py               # 就业管理业务
│   ├── fortune_service.py                  # 运势占卜业务
│   ├── graph_reasoning.py                  # 图谱深度推理服务
│   │   ├── event_causal_chain()           # 事件因果链 (e.g. "大闹天宫→被压五行山")
│   │   ├── faction_analysis()             # 阵营分析 (e.g. "蜀阵营人物")
│   │   ├── story_timeline()               # 事件时间线 (e.g. "西游记按章回排序")
│   │   └── deep_query()                   # LLM解析问题→自动调度推理方法
│   ├── graph_service.py                    # 图谱基础服务
│   │   ├── get_person_info()              # 人物详细信息
│   │   ├── get_person_relations()         # 人物关系网络
│   │   ├── find_relation_path()           # 两人间关系路径
│   │   ├── get_book_characters()          # 某书人物列表
│   │   ├── get_graph_visualization_data() # ECharts可视化数据
│   │   ├── search_person()                # 模糊搜索人物
│   │   └── deep_query()                   # 深度问答 (委托给GraphReasoningService)
│   ├── memory_service.py                   # 记忆存储服务
│   │   ├── create_session()               # 创建会话
│   │   ├── list_sessions()                # 会话列表
│   │   ├── delete_session()               # 删除会话
│   │   ├── save_exchange()                # 保存对话 (user+assistant两条)
│   │   ├── save_query()                   # 保存查询记录
│   │   ├── save_game_record()             # 保存游戏记录
│   │   ├── load_history()                 # 加载会话历史
│   │   └── get_query_history()            # 查询历史
│   ├── nl2sql_service.py                   # NL2SQL自然语言查数据库
│   │   ├── generate_sql()                 # DeepSeek生成SQL
│   │   ├── validate_sql()                 # SQL安全校验 (仅SELECT/表白名单/禁止关键词)
│   │   ├── execute_nl2sql()               # 安全执行SQL
│   │   └── nl2sql_query()                 # 完整流程 (生成→校验→执行→结果)
│   ├── proactive_service.py                # 主动对话服务 (SSE推送)
│   ├── rag_service.py                      # RAG知识问答服务
│   │   ├── answer_question_async()        # 增强版异步问答
│   │   ├── _detect_query_mode()           # 自动检测查询模式 (rag/graph/hybrid)
│   │   ├── _rag_only_query()              # 纯RAG查询 (书籍路由+跨集合联合检索)
│   │   ├── _graph_only_query()            # 纯图谱查询
│   │   └── _hybrid_query()                # RAG+图谱融合查询
│   ├── recommendation_service.py           # 学习推荐服务
│   │   ├── diagnose_weak_points()         # 薄弱点诊断 (趋势分析+下降检测+BKT)
│   │   └── generate_learning_plan()       # LLM学习计划生成
│   ├── score_service.py                    # 成绩管理业务
│   ├── student_service.py                  # 学生管理业务
│   └── weather_service.py                  # 天气服务
│
├── agent/                                  # 16个Agent文件
│   ├── base_agent.py                       # Agent抽象基类
│   │   ├── @abstractmethod execute()       # 抽象方法 (所有Agent必须实现)
│   │   ├── @abstractmethod agent_name      # 抽象属性
│   │   ├── self.tools: List[dict]          # 工具列表
│   │   └── self.tool_registry: dict        # 工具注册
│   ├── orchestrator_agent.py               # ★ 核心编排器 (多智能体协同)
│   │   ├── execute()                       # 新入口 (FC→分解→并行→单Agent)
│   │   ├── _execute_function_calling()     # Function Calling循环 (最多3轮)
│   │   ├── _execute_parallel()             # asyncio.gather并行执行
│   │   ├── _merge_results()                # LLM合并多Agent结果
│   │   ├── execute_single()                # 原路由表 (一行未删, fallback)
│   │   └── AgentMessageBus                 # Agent间消息总线
│   ├── system_prompts.py                   # 4角色人设Prompt系统
│   │   ├── get_system_prompt(character)    # 获取角色系统提示词
│   │   ├── CHARACTER_NAMES                 # 角色名称映射
│   │   └── 4角色完整人设 (身份/口吻/语言风格/知识背景)
│   ├── data_agent.py                       # 数据查询Agent (BusinessManagementAgent)
│   │   └── nl2sql_query→LLM总结+记忆注入
│   ├── knowledge_agent.py                  # 知识问答Agent (RAGKnowledgeAgent)
│   │   └── RAGService.answer_question()
│   ├── emotional_agent.py                  # 情绪疏导Agent (EmotionalCounselingAgent)
│   ├── social_agent.py                     # 社交僚机Agent (SocialAssistantAgent)
│   ├── game_agent.py                       # 游戏Agent (GameAgent: 灯谜+飞花令)
│   ├── persona_agent.py                    # 角色扮演Agent (PersonaAgent, 4角色版本)
│   ├── weather_agent.py                    # 天气Agent (WeatherQueryAgent)
│   ├── fortune_agent.py                    # 运势Agent (FortuneTellingAgent)
│   ├── react_agent.py                      # ★ ReAct推理循环Agent (ReActReasoningAgent)
│   │   ├── Thought→Action→Observation循环 (最多5轮)
│   │   ├── _build_tools()                  # 动态构建工具列表 (nl2sql/rag/graph)
│   │   ├── _execute_tool()                 # 执行工具调用
│   │   ├── _tool_nl2sql()                  # NL2SQL工具
│   │   ├── _tool_rag()                     # RAG检索工具
│   │   └── _tool_graph()                   # 图谱查询工具
│   ├── recommendation_agent.py             # ★ 学习推荐Agent (LearningRecommendationAgent)
│   │   ├── _extract_student_no()           # 正则提取学号
│   │   ├── 计划请求→generate_learning_plan()
│   │   └── 诊断请求→diagnose_weak_points()
│   ├── task_decomposer.py                  # ★ 任务分解器 (TaskDecomposer)
│   │   └── LLM分析→拆分最多3个子任务
│   ├── agent_message_bus.py                # ★ Agent间消息总线 (线程安全字典+Lock)
│   └── tool_registry.py                    # ★ 工具注册表 (单例, 6个工具)
│       ├── nl2sql (数据库查询)
│       ├── rag_search (四大名著检索)
│       ├── graph_query (人物关系查询)
│       ├── calculate (数学计算)
│       ├── get_weather (天气查询)
│       └── get_fortune (运势占卜)
│
├── utils/                                  # 20个工具模块
│   ├── deepseek_util.py                    # DeepSeek API (chat_completion + chat_completion_stream)
│   ├── qwen_util.py                        # 阿里云Qwen API
│   ├── llm_router.py                       # LLM路由 (DeepSeek/Qwen自动切换)
│   ├── embedding_util.py                   # 向量嵌入 (DeepSeek embedding)
│   ├── milvus_util.py                      # Milvus向量数据库工具
│   │   ├── connect_milvus()                # 连接
│   │   ├── search_all_novels()             # 跨4本书检索
│   │   ├── search_specific_novels()        # 指定书检索
│   │   └── get_all_collections()           # 所有集合状态
│   ├── neo4j_util.py                       # Neo4j图数据库工具
│   │   ├── neo4j_client                    # Neo4j客户端封装
│   │   ├── get_person()                    # 查询人物
│   │   ├── get_person_relations()          # 查询关系
│   │   ├── find_path()                     # 最短路径
│   │   ├── get_book_characters()           # 某书人物
│   │   ├── get_graph_data()                # ECharts数据
│   │   ├── query_event_chain()             # 事件因果链
│   │   ├── query_faction_members()         # 阵营成员
│   │   └── query_story_timeline()          # 故事时间线
│   ├── tts_util.py                         # 阿里云TTS (文本→音频bytes)
│   ├── asr_util.py                         # 阿里云ASR (音频bytes→文本)
│   ├── memory_extractor.py                 # ★ 记忆提取器
│   │   ├── extract_memories()              # fire-and-forget入口
│   │   ├── _llm_extract()                  # LLM提取4类记忆(fact/preference/event/emotion)
│   │   ├── _load_existing()                # MySQL去重 (Jaccard>0.3视为重复)
│   │   ├── _insert_milvus()                # 向量化写入Milvus
│   │   └── _update_profile()               # 更新用户画像 (user_profile表)
│   ├── memory_retriever.py                 # ★ 记忆检索器
│   │   ├── retrieve()                      # Milvus语义搜索+MySQL结构补充+排序衰减
│   │   └── build_memory_prompt()           # 构建记忆提示词注入system prompt
│   ├── book_router.py                      # 四大名著书籍智能路由 (关键词匹配→目标书籍)
│   ├── weather_util.py                     # 和风天气API
│   ├── fortune_util.py                     # 运势工具
│   ├── jwt_util.py                         # JWT认证工具
│   ├── password_util.py                    # 密码加密 (bcrypt)
│   ├── excel_util.py                       # Excel读写 (openpyxl)
│   ├── text_chunker.py                     # 文本分块工具
│   ├── logger.py                           # 日志系统
│   └── response_util.py                    # 统一响应封装
│
├── entity/                                 # 15个ORM实体模型
│   ├── base.py                             # 基类 (TimestampMixin + SoftDeleteMixin)
│   ├── student.py                          # student表
│   ├── class_info.py                       # class_info表
│   ├── score.py                            # score表 (student_no+exam_order唯一约束)
│   ├── employment.py                       # employment表
│   ├── course.py                           # course_info表
│   ├── user.py                             # users表
│   ├── teacher.py                          # teacher表
│   ├── operation_log.py                    # operation_log表
│   ├── conversation_history.py             # conversation_history表
│   ├── memory_fragment.py                  # memory_fragment表 (含chunk_id向量索引)
│   ├── user_profile.py                     # user_profile表 (用户画像)
│   ├── permission.py                       # permissions表
│   ├── document_chunk.py                   # document_chunk表 (RAG文档索引)
│   ├── lantern_riddle.py                   # lantern_riddle表 (灯谜题库)
│   └── qa_pair.py                          # qa_pair表 (问答对)
│
├── schema/                                 # Pydantic Schema
│   ├── student_schema.py
│   ├── class_schema.py
│   ├── score_schema.py
│   ├── employment_schema.py
│   └── course_schema.py
│
├── dao/                                    # 数据访问层
│   ├── base_dao.py                         # BaseDAO通用CRUD
│   ├── memory_dao.py                       # MemoryDAO
│   ├── student_dao.py                      # StudentDAO
│   └── user_dao.py                         # UserDAO
│
├── middleware/                             # 中间件
│   ├── global_exception_handler            # 通用异常
│   ├── http_exception_handler              # HTTP异常
│   └── validation_exception_handler        # 参数验证异常
│
├── data/                                   # 数据文件
│   ├── bajie_persona.json                  # 猪八戒人设数据
│   └── riddles.json                        # 灯谜题库
│
└── logs/                                   # 日志文件
    └── student-manager.log.2026-05-28
```

### 3.3 根目录文件清单

```
项目根目录/
├── .gitignore                              # Git忽略配置
├── .codebuddy/                             # CodeBuddy配置
├── requirements.txt                        # Python后端依赖 (19个包)
├── 0416-finally_create_db.sql              # 数据库初始化SQL
├── README.md                               # 项目说明
├── code_review_result.md                   # 代码审查结果
├── api_test_output.txt                     # API测试输出
├── test_output.txt                         # 测试输出
│
├── 《西游记》(1).txt                        # 四大名著原文文件
├── 《三国演义》(1).txt
├── 《水浒传》(1).txt
├── 《红楼梦》(1).txt
│
├── 猪八戒.png                              # 角色图片 (用于文档展示)
├── 鲁智深.png
├── 林黛玉.png
├── 诸葛亮.jpg
│
├── scripts/                                # 脚本工具
│   ├── init_db.py                          # 初始化数据库表结构
│   ├── init_milvus.py                      # 初始化Milvus向量集合 (4个集合)
│   ├── init_neo4j.py                       # 初始化Neo4j人物关系图谱
│   ├── ingest_novel.py                     # 导入四大名著全文到Milvus
│   ├── hash_passwords.py                   # 密码哈希加密工具
│   └── fix_users_table.sql                 # 用户表修复SQL
│
└── docs/
    └── superpowers/
        ├── plans/                          # 5个实施计划文档
        │   ├── 2026-05-27-phase1-cleanup.md
        │   ├── 2026-05-27-phase2-aliyun-integration.md
        │   ├── 2026-05-27-phase3-frontend-api.md
        │   ├── 2026-05-27-phase4-8-advanced.md
        │   ├── 2026-05-27-phase-new-features.md
        │   └── 2026-05-27-rag-neo4j-implementation.md
        └── specs/                          # 5个设计规范文档
            ├── 2026-05-27-ai-agent-enhancement-design.md
            ├── 2026-05-27-rag-neo4j-enhancement-design.md
            ├── 2026-05-29-memory-framework-design.md
            ├── 2026-05-31-full-system-enhancement-design.md
            └── 2026-06-01-full-system-technical-documentation.md (本文档)
```

---

## 4. 当前已实现功能矩阵

### 4.1 管理系统功能 (8个模块)

| 模块 | 功能 | 路由 | 权限 | 状态 |
|------|------|------|------|:--:|
| **仪表盘** | 5个统计卡片 (学生总数/班级数量/教师人数/平均成绩/就业率) | `/dashboard` | 登录即可 | ✅ |
| | 4个ECharts图表 (班级分布柱状图/成绩趋势折线图/就业情况/分数段分布) | | | ✅ |
| **学生管理** | 列表搜索 (学号/姓名/班级) + 分页 | `/students` | student:view | ✅ |
| | 新增/编辑/删除 (弹窗表单) | | | ✅ |
| | Excel导入/导出 + 批量删除 | | | ✅ |
| **班级管理** | CRUD + 分页 | `/classes` | class:view | ✅ |
| **成绩管理** | 按学生查询 (student_no + exam_order) | `/scores` | score:view | ✅ |
| | 新增/编辑/删除 | | | ✅ |
| **就业管理** | CRUD + 按班级筛选 | `/employment` | employment:view | ✅ |
| **课程管理** | CRUD | `/courses` | course:view | ✅ |
| **操作日志** | 日志查询 (操作人/操作类型/时间范围) | `/logs` | log:view | ✅ |
| **用户管理** | CRUD + 角色权限 (超管/管理员/教师/学生) | `/system/users` | user:manage | ✅ |
| **智能问数** | NL2SQL 自然语言查询业务数据 | 内嵌组件 | 登录即可 | ✅ |

### 4.2 AI功能 (6个模块)

| 模块 | 子功能 | 实现关键技术点 | 状态 |
|------|------|------|:--:|
| **八戒对话** | 4角色切换 (猪八戒/鲁智深/林黛玉/诸葛亮) | 每人独立emoji/头像/名言/性格/说话风格/系统提示词 | ✅ |
| | 9种意图路由 | classify_intent_hybrid (贝叶斯+LLM) + OrchestratorAgent路由表 | ✅ |
| | SSE流式回复 + 打字机效果 | agentChatStream + asyncio.AsyncGenerator | ✅ |
| | 会话管理 (左侧列表+创建/切换/删除) | memory_service CRUD | ✅ |
| | 对话记忆 (自动存档+记忆提取) | memory_extractor fire-and-forget + MySQL+Milvus双写 | ✅ |
| | 主动对话 (AI主动搭话,SSE推送) | proactive_service + SSE事件流 | ✅ |
| | 语音输入/输出 | VoiceInput(MediaRecorder) + VoiceOutput(TTS) + audio_controller | ✅ |
| **知识问答** | RAG四大名著知识库检索 | Milvus 4个集合(西游记/三国/水浒/红楼)联合检索 + Top-K | ✅ |
| | 书籍智能路由 | book_router 关键词匹配→自动选择目标书籍 | ✅ |
| | 图谱融合查询 | rag + graph hybrid模式 (人物关系+原文内容) | ✅ |
| **八戒游戏** | 灯谜 (出题/猜谜/提示) | lantern_riddle表 + GameAgent | ✅ |
| | 飞花令 (对诗) | GameAgent + DeepSeek诗词生成 | ✅ |
| **社交助手** | 社交话术/情书生成 | SocialAgent + DeepSeek | ✅ |
| **知识图谱** | 人物信息查询 + 关系网络 + 路径查找 | Neo4j Cypher查询 + GraphService | ✅ |
| | ECharts力导向图可视化 | GraphView.vue + 分类颜色渲染 | ✅ |
| **天气查询** | 实时天气查询 | 和风天气API + WeatherAgent | ✅ |
| **运势占卜** | 运势占卜 (综合/爱情/事业/财运) | FortuneAgent + DeepSeek | ✅ |

### 4.3 记忆系统功能 (5个组件)

| 功能 | 实现文件 | 关键技术点 | 状态 |
|------|------|------|:--:|
| 记忆提取 | `memory_extractor.py` | LLM提取→Jaccard去重(>0.3)→向量化→MySQL+Milvus双写→更新user_profile | ✅ |
| 记忆检索 | `memory_retriever.py` | Milvus COSINE语义搜索+MySQL结构化补充→importance排序衰减→构建提示词 | ✅ |
| 记忆片段 | `memory_fragment.py` | ORM实体 (含chunk_id向量索引/importance/access_count) | ✅ |
| 用户画像 | `user_profile.py` | ORM实体 (interaction_count/last_emotion/preferred_topics/personality_tags) | ✅ |
| 注入Agent | `data_agent.py` / `persona_agent.py` | execute()中调用MemoryRetriever.build_memory_prompt()注入system prompt | ✅ |

### 4.4 认证与安全

| 功能 | 实现 | 状态 |
|------|------|:--:|
| 4种角色登录 (超级管理员/管理员/教师/学生) | auth_controller + auth_service + JWT | ✅ |
| 预设账号一键填充 | Login.vue 预设4种账号信息 | ✅ |
| JWT access_token (120分钟) + refresh_token (7天) | python-jose HS256 + passlib bcrypt | ✅ |
| 全局路由守卫 (未登录→/login) | router.beforeEach | ✅ |
| 权限控制 (前端v-if + 后端接口验证) | auth store hasPermission() + get_current_user Depends | ✅ |
| 修改密码 | HeaderBar.vue 弹窗表单 + 密码确认 | ✅ |
| SQL安全校验 (仅SELECT/表白名单/禁止关键词) | nl2sql_service.validate_sql() | ✅ |

---

## 5. 多智能体协同架构详解

### 5.1 整体架构

```
用户消息
    │
    ▼
┌──────────────────────────────┐
│  agent_service.py             │
│                               │
│  classify_intent_hybrid()     │
│  ├── 贝叶斯置信度≥0.85 → 直接用│
│  └── 置信度<0.85 → LLM分类    │
│       └── 9种意图代码          │
│                               │
│  AgentService.process_message()│
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│  OrchestratorAgent.execute()  │  ★ 核心编排入口
│                               │
│  ┌─────────────────────────┐ │
│  │ Function Calling 分支    │ │  ← data_query/knowledge_question
│  │ _execute_function_calling│ │     LLM自主决定调用工具(3轮)
│  │ ToolRegistry 6个工具     │ │     nl2sql/rag/graph/calculate
│  │                         │ │     /weather/fortune
│  └─────────────────────────┘ │
│                               │
│  ┌─────────────────────────┐ │
│  │ 任务分解                 │ │  ← 其他意图
│  │ TaskDecomposer.decompose │ │     LLM分析复合问题
│  │ 拆分最多3个子任务        │ │     判断是否需要分解
│  └────────┬────────────────┘ │
│           │                   │
│     ┌─────┴─────┐            │
│     │ 子任务>1?  │            │
│     └─────┬─────┘            │
│     Yes    │    No           │
│     ▼      │    ▼            │
│  _execute_parallel   execute_single    │
│  asyncio.gather      路由表            │
│  并行执行8个Agent    8个Agent路由       │
│     │                │                │
│     ▼                ▼                │
│  _merge_results    直接返回            │
│  LLM合并多Agent结果                    │
└──────────────────────────────┘
```

### 5.2 路由表详情

| 意图代码 | Agent类 | Agent标识 | 工具/服务 |
|------|------|------|------|
| `data_query` | DataAgent | BusinessManagementAgent | NL2SQL + 记忆注入 |
| `knowledge_question` | KnowledgeAgent | RAGKnowledgeAgent | RAG服务 (Milvus+图谱融合) |
| `emotional_support` | EmotionalAgent | EmotionalCounselingAgent | DeepSeek情绪疏导 |
| `social_help` | SocialAgent | SocialAssistantAgent | DeepSeek社交话术 |
| `weather_query` | WeatherAgent | WeatherQueryAgent | 和风天气API |
| `fortune_telling` | FortuneAgent | FortuneTellingAgent | DeepSeek运势生成 |
| `game_riddle` | GameAgent | GameAgent | 灯谜数据库 |
| `game_poetry` | GameAgent | GameAgent | DeepSeek诗词对仗 |
| `chat_greet` | PersonaAgent | 4角色版本 | DeepSeek角色扮演 |
| `deep_reasoning` | ReactAgent | ReActReasoningAgent | ReAct循环推理 |
| `learning_recommendation` | RecommendationAgent | LearningRecommendationAgent | BKT+学习计划 |

### 5.3 任务分解详解

**TaskDecomposer** 基于LLM分析用户消息是否为复合问题：

- **单一问题示例**:
  - "你好" → `{"subtasks": []}`
  - "今天天气怎么样" → `{"subtasks": []}`

- **复合问题示例**:
  - "查一下张三的成绩，再分析他的学习状态" → 2个子任务
  - "帮我算一卦，然后再查一下就业率" → 2个子任务

- **约束**: 最多拆3个子任务，过滤非法意图

### 5.4 Function Calling详解

**OrchestratorAgent._execute_function_calling()** 实现LLM自主工具调用：

```
用户问题: "孙悟空大闹天宫后怎么样了？同时帮我查有多少学生"
    │
    ▼
┌──────────────────────────────────────────┐
│  Round 1: LLM分析 → 决定调用rag_search  │
│  参数: {"question": "孙悟空大闹天宫"}      │
│  Observation: [检索到的原文片段...]        │
│                                          │
│  Round 2: LLM分析 → 决定调用nl2sql       │
│  参数: {"query": "有多少学生"}            │
│  Observation: [{"row_count": 150}]       │
│                                          │
│  Round 3: LLM综合所有信息 → 直接回复      │
│  回复: "俺老猪告诉你..."                  │
└──────────────────────────────────────────┘
```

**ToolRegistry 注册的6个工具**:

| 工具名 | 描述 | 参数 | 实现 |
|------|------|------|------|
| `nl2sql` | 查询业务数据库 | query: string | _tool_nl2sql |
| `rag_search` | 四大名著知识检索 | question: string | _tool_rag |
| `graph_query` | 人物关系图谱查询 | name: string | _tool_graph |
| `calculate` | 数学计算 | expression: string | _tool_calculate |
| `get_weather` | 城市天气查询 | city: string | _tool_weather |
| `get_fortune` | 运势占卜 | - | _tool_fortune |

### 5.5 ReAct推理循环详解

**ReactAgent** 实现 Thought→Action→Observation 循环推理：

```
用户问题: "分析张三最近成绩趋势，如果下降了帮我查是否缺课"
    │
    ▼
┌──────────────────────────────────────────────┐
│  Step 1:                                      │
│    Thought: 需要先查询张三的成绩数据           │
│    Action: {"tool": "nl2sql",                 │
│             "input": "张三最近3次考试成绩"}     │
│    Observation: [75分, 68分, 62分, 呈下降趋势] │
│                                               │
│  Step 2:                                      │
│    Thought: 成绩下降，需要查考勤找原因         │
│    Action: {"tool": "nl2sql",                 │
│             "input": "张三近期的考勤记录"}      │
│    Observation: [缺勤3次, 迟到5次]             │
│                                               │
│  Step 3:                                      │
│    Thought: 信息已足够，可以给出结论了         │
│    Final Answer: "张三的成绩从75下降到62，     │
│                  主要原因是缺勤3次、迟到5次..." │
└──────────────────────────────────────────────┘
```

- **最大次数**: 5轮 (防止死循环)
- **超5轮**: 强制LLM总结所有观察结果
- **可用工具**: nl2sql (数据库查询) / rag_search (知识检索) / graph_query (图谱查询)

### 5.6 Agent间消息总线

**AgentMessageBus** 是一个轻量级线程安全的共享上下文字典，使用 `threading.Lock` 保证并发安全：

```python
class AgentMessageBus:
    context = {}       # 共享字典
    _lock = Lock()     # 线程安全锁

    def set(key, value):  # 写入共享上下文
    def get(key, default): # 读取共享上下文
```

**使用场景**: 在并行执行时，各Agent可通过 `self.bus` 读写共享上下文，实现Agent间数据传递和状态同步。

---

## 6. 记忆框架详解

### 6.1 记忆提取流程

```
对话结束 (用户消息 + AI回复)
    │
    ▼
MemoryExtractor.extract_memories()  ← fire-and-forget (异步,不阻塞回复)
    │
    ├── Step 1: LLM提取
    │   _llm_extract(conversation)
    │   分类为4种类型:
    │   ├── fact:       用户客观事实 (姓名/身份/学校/专业)
    │   ├── preference: 用户偏好 (喜欢/不喜欢什么)
    │   ├── event:      用户经历的或即将发生的事件
    │   └── emotion:    用户情绪状态
    │   重要性评分: 姓名=1.0, 临时情绪=0.5
    │
    ├── Step 2: 去重
    │   _load_existing() 加载已有记忆 → Jaccard相似度比较
    │   >0.3 → 视为重复, 丢弃
    │
    ├── Step 3: 向量化 + 双写
    │   get_embedding(content) → MemoryFragment(MySQL) + Milvus插入
    │   chunk_id = "mem_{user_id}_{uuid[:8]}"
    │
    └── Step 4: 更新用户画像
        _update_profile()
        ├── interaction_count += 1
        ├── last_active_time 更新
        ├── emotion → last_emotion
        ├── preference → preferred_topics (最多10个)
        └── fact → personality_tags (最多8个)
```

### 6.2 记忆检索流程

```
用户发送新消息
    │
    ▼
MemoryRetriever.retrieve(user_id, query, top_k=5)
    │
    ├── Step 1: Milvus语义搜索
    │   query → embedding → Milvus COSINE搜索 (user_id过滤)
    │   nprobe=16, 返回top_k=10
    │
    ├── Step 2: MySQL补充检索
    │   按importance降序查询 memory_fragment表
    │   取前5条
    │
    ├── Step 3: 混合排序
    │   final_score = score×0.6 + importance×0.3 + source_bonus×0.1
    │   Milvus语义结果权重更高 (bonus=0.3)
    │   MySQL结构结果权重较低 (bonus=0)
    │
    └── Step 4: 更新访问统计
        更新 access_count + last_accessed_at
```

### 6.3 记忆注入流程

```
Agent.execute() 被调用
    │
    ▼
MemoryRetriever.build_memory_prompt(user_id, query)
    │
    ▼
构建记忆提示词:
"[关于用户的已知信息]
- 你是张三，就读计算机科学专业
- 你喜欢篮球和编程
- 上次你说在准备期末考试
请自然地在回答中运用这些信息，不要刻意罗列。"
    │
    ▼
注入 System Prompt → DeepSeek LLM → 个性化回复
```

### 6.4 记忆类型与重要性

| 类型 | 描述 | 重要性范围 | 示例 |
|------|------|------|------|
| `fact` | 用户客观事实 | 0.7-1.0 | "张三, 计算机科学专业大三学生" |
| `preference` | 用户偏好 | 0.5-0.8 | "喜欢篮球和编程" |
| `event` | 事件信息 | 0.4-0.7 | "下周五有期末考试" |
| `emotion` | 情绪状态 | 0.3-0.6 | "最近压力很大" |

---

## 7. 八项核心能力诊断

> 此章节记录了用户对项目核心能力的8个疑问及逐项诊断结果

### 7.1 多智能体协同 — 🟢 已实现

**问题**: 多智能体协同已经创建好了是吗？

**诊断结论**: **是的，已创建完毕。** 包含以下关键模块：

| 模块 | 文件 | 状态 |
|------|------|:--:|
| 编排器 | `orchestrator_agent.py` | ✅ |
| 基类 | `base_agent.py` | ✅ |
| 8个专家Agent | `data_agent.py` 等 | ✅ |
| ReAct推理Agent | `react_agent.py` | ✅ |
| 学习推荐Agent | `recommendation_agent.py` | ✅ |
| 任务分解器 | `task_decomposer.py` | ✅ |
| 工具注册表 | `tool_registry.py` (单例, 6个工具) | ✅ |
| 消息总线 | `agent_message_bus.py` (线程安全) | ✅ |
| 角色人设 | `system_prompts.py` (4角色) | ✅ |

**已实现的协同模式**:
- ✅ 任务分解 (TaskDecomposer: LLM分析→拆分子任务→限制3个)
- ✅ 并行调度 (asyncio.gather 并行执行多个Agent)
- ✅ 结果合并 (_merge_results: LLM整合多Agent输出)
- ✅ Agent间通信 (AgentMessageBus: 线程安全共享上下文)
- ✅ Function Calling (ToolRegistry: LLM自主决定调用6个工具)
- ✅ 原有路由表保留 (execute_single 一行未删, 作为fallback)

### 7.2 记忆框架 — 🟢 完整且可执行

**问题**: 记忆框架是否还存在？且还能执行？

**诊断结论**: **完整存在且可正常执行。** 由以下5个组件构成：

| 组件 | 文件 | 功能 | 依赖 |
|------|------|------|------|
| 记忆提取 | `memory_extractor.py` | LLM提取→去重→向量→双写 | DeepSeek + MySQL + Milvus |
| 记忆检索 | `memory_retriever.py` | 语义搜索+结构排序 | Milvus + MySQL |
| 记忆片段 | `memory_fragment.py` | ORM实体 | MySQL |
| 用户画像 | `user_profile.py` | ORM实体 | MySQL |
| 注入使用 | `data_agent.py` / `persona_agent.py` | execute中调用检索 | - |

**执行条件**:
- ✅ MySQL正常运行 (对话记忆 + 用户画像存储)
- ✅ Milvus正常运行 (记忆片段向量索引)
- ✅ DeepSeek API可用 (LLM提取 + 向量嵌入)
- ✅ Milvus中需要有 `memory_vectors` 集合 (运行 `scripts/init_milvus.py` 创建)

**触发时机**: 每次对话流结束后自动触发 (fire-and-forget, 不阻塞用户回复)

### 7.3 Agent自主调用数据库/RAG/图谱 — 🟢 已实现

**问题**: 智能体是否能自主调用数据库和RAG和图谱？

**诊断结论**: **是的，已实现。** 通过两层机制：

**机制一: OrchestratorAgent._execute_function_calling()** (编排器层面)
- 在 `data_query` 和 `knowledge_question` 意图下触发
- LLM在3轮内自主决定调用哪个工具
- ToolRegistry 提供6个工具 (nl2sql/rag_search/graph_query/calculate/weather/fortune)

**机制二: ReactAgent** (Agent层面)
- `react_agent.py` 内置 _build_tools() 动态构建工具列表
- 支持 nl2sql / rag_search / graph_query 三个工具
- 5轮 Think→Act→Observe 循环推理

**必要性分析**: 这个功能非常有必要实现：

1. **提升智能**: 智能体不再只是"路由到固定Agent"，而是能根据问题复杂度自主决定是否调用额外工具
2. **减少延迟**: 不需要预先定义所有可能的工具调用链路
3. **更灵活**: 用户问题可能跨多个领域，自主调用可以动态组合工具
4. **降级优雅**: FC失败→回退到路由表模式,不影响核心功能

### 7.4 ReAct推理循环 — 🟡 文件已创建，待业务验证

**问题**: 是否还能实现ReAct推理循环？

**诊断结论**: `react_agent.py` 已创建，代码逻辑完整，但在实际业务流程中尚未进行全面的端到端测试验证。

**已有基础**:
- ✅ `react_agent.py` 文件已存在 (Thought→Action→Observation循环, 最多5轮)
- ✅ 支持3个工具: nl2sql (数据库查询) / rag_search (知识检索) / graph_query (图谱查询)
- ✅ `orchestrator_agent.py` 中已挂载 `self.react_agent` (含try/except兜底)
- ✅ 路由表新增 `"deep_reasoning": (self.react_agent, "ReActReasoningAgent")`

**缺失能力**:
- ❌ 没有 `deep_reasoning` 意图的识别逻辑 (classify_intent没有对应分类提示词)
- ❌ 没有触发入口 (用户无法通过正常对话触发ReAct推理)

### 7.5 贝叶斯意图分类 — 🟡 文件已创建，与LLM并存

**问题**: 能否实现贝叶斯意图分类？会不会影响已有LLM意图识别？

**诊断结论**: `bayesian_classifier.py` 已创建，"贝叶斯前置 + LLM兜底"方案已实现。**不会影响已有LLM意图识别，二者完全兼容**。

**实现原理**:
```
用户消息
    │
    ▼
classify_intent_hybrid()
    │
    ├── BayesianClassifier.classify()
    │   ├── 置信度 ≥ 0.85 → 直接使用 (跳过LLM, 更快更省)
    │   └── 置信度 < 0.85 → 回退 LLM classify_intent()
    │       └── LLM结果加入训练缓冲区 add_training_sample()
    │
    ▼
返回意图代码
```

**已有基础**:
- ✅ MultinomialNB + TF-IDF (char_wb, ngram 1-3, max_features=5000)
- ✅ 种子关键词兜底 (conversation_history无数据时自动使用)
- ✅ 自我学习机制 (累计20条→自动重训练)
- ✅ 混合分类逻辑完整 (agent_service.classify_intent_hybrid)

**缺失能力**:
- ❌ 预训练数据不足 (需要约500条标注语料覆盖9种意图)
- ❌ 缺少模型持久化 (每次重启需重新训练)

### 7.6 知识图谱深度推理 — 🟡 逻辑就绪，数据待扩展

**问题**: 能否实现知识图谱深度推理 (事件因果推理/人物阵营分析/剧情时间线)？

**诊断结论**: `graph_reasoning.py` 已创建，实现了推理函数逻辑框架和LLM解释，但Neo4j数据模型尚未扩展。

**已有基础**:
- ✅ `graph_reasoning.py` 文件已存在
- ✅ `event_causal_chain()` — 事件因果链查询 + LLM解释
- ✅ `faction_analysis()` — 阵营分析 (查faction属性)
- ✅ `story_timeline()` — 事件时间线 (按chapter排序)
- ✅ `deep_query()` — LLM解析问题→自动调度推理方法
- ✅ `graph_service.py` 基础查询就绪 (get_person/get_relations/find_path)
- ✅ Neo4j连接已就绪

**缺失能力 (需Neo4j数据扩展)**:
- ❌ Neo4j中只有Person节点，没有Event节点
- ❌ Person节点没有faction属性 (阵营: 蜀/魏/吴/佛/道)
- ❌ Person节点没有chapter属性 (首次出场章回)
- ❌ 没有CAUSES关系边 (事件因果链)
- ❌ 推理逻辑在graph_reasoning.py中定义好了，但对应Neo4j数据需手动导入

### 7.7 个性化学习推荐 — 🟡 文件就绪，待数据验证

**问题**: 能否实现个性化学习推荐 (BKT + 薄弱点诊断 + 学习计划)？

**诊断结论**: 三个文件已创建完毕，但在真实学生数据上尚未验证。

**已有基础**:
- ✅ `bkt_service.py` — BKT算法 (P_learn=0.2 / P_guess=0.1 / P_slip=0.1 / P_init=0.5)
- ✅ `recommendation_service.py` — 薄弱点诊断 (趋势分析+下降检测) + LLM学习计划生成
- ✅ `recommendation_agent.py` — 学号提取+计划/诊断两种请求处理
- ✅ `orchestrator_agent.py` 中已挂载 `self.recommendation_agent`
- ✅ `score.py` 实体有 `student_no`、`exam_order`、`score` 字段，可用于成绩分析

**缺失能力**:
- ❌ 没有 `learning_recommendation` 意图 (无法通过对话触发)
- ❌ 缺少知识点体系定义 (知识点的映射关系，如三角函数/概率论/几何/代数)
- ❌ BKT结果不写入user_profile (未与用户画像联动)

### 7.8 多模态交互 — 🟢 已实现，能听能说

**问题**: 项目是否实现多模态交互？是否做到能听能说？

**诊断结论**: **多模态交互已完整实现，能做到"能听能说"。**

**已有能力**:
- ✅ `tts_util.py` → `text_to_speech()` → 阿里云 DashScope 语音合成 (sambert-zhichu)
- ✅ `asr_util.py` → `speech_to_text()` → 阿里云 DashScope 语音识别 (qwen-audio-asr)
- ✅ `audio_controller.py` → `POST /api/v1/audio/recognize` — 语音识别接口 (上传音频→返回文本)
- ✅ `audio_controller.py` → `POST /api/v1/audio/synthesize` — 语音合成接口 (文本→返回base64音频)
- ✅ `VoiceInput.vue` — 前端录音按钮 (MediaRecorder API, 15秒倒计时, 脉冲动画)
- ✅ `VoiceOutput.vue` — 前端播放按钮 (优先浏览器Web Speech API TTS, 回退后端阿里云TTS)
- ✅ 已集成到 `BajieChat.vue` 聊天流程中 (每条AI回复下方有语音播放按钮, 输入区有录音按钮)

**缺失能力**:
- ❌ 连续对话模式 (语音→自动回复→自动TTS播放, 无需手动点击)
- ❌ 不同角色使用不同TTS音色 (当前所有角色使用同一音色)

---

## 8. 七大功能增强方案

> 此章节记录了用户提出的7大功能增强需求及其完整实现方案

### 8.1 架构影响分析总结

**核心结论: 全部实现不会改乱项目。**

| 功能 | 改动文件 | 新增文件 | 破坏性 | 原因 |
|------|:--:|:--:|:--:|------|
| ① 多智能体协同 | `orchestrator_agent.py` | `task_decomposer.py` / `agent_message_bus.py` | 🟡 中 | 重写核心编排逻辑，但旧路由表完整保留 |
| ② Function Calling | `base_agent.py` (+2属性) / `orchestrator_agent.py` (+方法) | `tool_registry.py` | 🟡 中 | 基类加属性，编排器加分支，不影响旧逻辑 |
| ③ ReAct 循环 | `classify_intent` (+意图) / `orchestrator_agent` (+路由) | `react_agent.py` | 🟢 低 | 纯增量，新增路由条目 |
| ④ 贝叶斯分类 | `agent_service.py` (+函数引用) | `bayesian_classifier.py` | 🟢 极低 | 4行改动，if/else分支切换 |
| ⑤ 图谱深度推理 | `graph_service.py` (+方法调用) | `graph_reasoning.py` | 🟢 低 | 追加方法，不删旧代码 |
| ⑥ BKT 学习推荐 | `classify_intent` (+意图) / `orchestrator_agent` (+路由) | `bkt_service.py` / `recommendation_service.py` / `recommendation_agent.py` | 🟢 低 | 纯增量 |
| ⑦ 多模态交互 | 无 (已实现) | 无 (已实现) | 🟢 零 | 功能已就绪 |

### 8.2 功能①: 多智能体协同全面升级

**目标**: 补齐协同管理面板、Agent状态监控看板、任务日志等前端可视化能力

**当前状态**: 后端协同逻辑已完整实现 (任务分解/并行执行/结果合并/Agent间通信/Function Calling)，前端缺少协同管理看板

**实现要点**:
1. 前端新增协同管理看板页面 (Agent状态可视化、任务实时监控)
2. 后端为编排器补充WebSocket状态广播接口 (向管理面板推送Agent执行状态)
3. Agent间消息总线补充消息持久化日志 (记录每次Agent间通信)

**改动范围**:
- 新增: `frontend/src/views/agent/AgentDashboard.vue` (协同管理看板)
- 新增: `backend/controller/agent_monitor_controller.py` (WebSocket状态接口)
- 修改: `backend/agent/orchestrator_agent.py` (添加状态广播)
- 修改: `frontend/src/router/index.js` (新增路由)
- 修改: `frontend/src/components/layout/Sidebar.vue` (新增菜单项)

### 8.3 功能②: Agent自主工具调用级联

**目标**: 让每个Agent独立拥有Function Calling决策能力，而非仅由编排器集中决策

**当前状态**: Function Calling已实现，但由 `OrchestratorAgent._execute_function_calling()` 集中决策

**实现要点**:
1. 将 `graph_query` 工具注册到 `ToolRegistry` (当前6个工具，graph_query待验证)
2. 为每个Agent的 `execute()` 添加独立的Function Calling决策分支
3. 补充工具调用日志统计 (调用了哪个工具、返回了什么结果、耗时多少)

**改动范围**:
- 修改: `backend/agent/base_agent.py` (添加 `_try_function_calling()` 方法)
- 修改: `backend/agent/tool_registry.py` (添加调用日志)
- 修改: `backend/agent/data_agent.py` / `knowledge_agent.py` (添加FC分支)

### 8.4 功能③: ReAct推理循环端到端打通

**目标**: 完成ReactAgent的实际业务流程验证与集成，让用户能在对话中触发ReAct推理

**当前状态**: `react_agent.py` 代码逻辑完整，但缺少意图识别和触发入口

**实现要点**:
1. 在 `classify_intent` 中增加 `deep_reasoning` 意图识别逻辑
2. 在 `BajieChat` 中增加ReAct推理触发入口 (如"分析一下"、"帮我推理"等关键词)
3. 验证 Thought→Act→Observe→Think 循环在真实对话场景中的稳定性

**改动范围**:
- 修改: `backend/service/agent_service.py` (INTENT_CLASSIFIER_PROMPT 增加 `deep_reasoning` 意图)
- 修改: `backend/agent/react_agent.py` (增加错误重试和超时保护)
- 修改: `frontend/src/views/bajie/BajieChat.vue` (增加ReAct推理快捷入口)

**触发示例**:
- "分析一下张三的成绩趋势，如果有问题帮我查查原因"
- "帮我推理为什么班级就业率下降了"
- "查一下孙悟空的战绩，然后分析他的战斗力变化"

### 8.5 功能④: 贝叶斯意图分类完善

**目标**: 完善贝叶斯分类器的预训练和模型持久化，让贝叶斯前置分类真正发挥作用

**当前状态**: `bayesian_classifier.py` 代码完整，但缺少预训练数据和模型持久化

**实现要点**:
1. 准备预训练数据 (约500条标注语料，覆盖9种意图)
2. 添加模型持久化和加载机制 (pickle/joblib保存和加载)
3. 启动时自动加载预训练模型，避免每次重启重新训练

**改动范围**:
- 修改: `backend/service/bayesian_classifier.py` (添加 `save_model()` / `load_model()` 方法)
- 新增: `backend/data/intent_training_samples.json` (预训练语料)
- 修改: `backend/service/agent_service.py` (启动时加载预训练模型)

**预期效果**:
- 贝叶斯分类命中率提升至70%+ (有足够训练数据后)
- 减少LLM调用次数，降低延迟和成本
- 自我学习机制持续优化分类准确率

### 8.6 功能⑤: 知识图谱深度推理上线

**目标**: Neo4j数据模型扩展 + 因果推理/阵营分析/时间线上线

**当前状态**: `graph_reasoning.py` 推理逻辑完整，但Neo4j数据模型未扩展

**实现要点**:

**1. 事件因果推理**:
```
问题: "为什么孙悟空被压五行山？"
→ Cypher: MATCH (e:Event {name:"大闹天宫"})-[:CAUSES]->(e2:Event {name:"被压五行山"})
→ 返回因果链: 大闹天宫 → 如来出手 → 被压五行山
需要: 新增Event节点 + CAUSES关系边
```

**2. 人物阵营分析**:
```
问题: "三国里刘备阵营有哪些人？"
→ Cypher: MATCH (p:Person {faction:"蜀"}) RETURN p.name
→ 返回: 刘备、关羽、张飞、诸葛亮、赵云...
需要: 给Person节点加faction属性
```

**3. 剧情时间线**:
```
问题: "西游记的时间线"
→ Cypher: MATCH (e:Event) WHERE e.book="novel_xiyou" RETURN e ORDER BY e.chapter
→ 返回: 按章回排序的事件列表
需要: 新增Event节点 + chapter属性
```

**改动范围**:
- 修改: `scripts/init_neo4j.py` (扩展数据模型: Event节点 + CAUSES关系 + faction属性 + chapter属性)
- 修改: `backend/utils/neo4j_util.py` (新增Cypher查询方法: query_event_chain / query_faction_members / query_story_timeline)
- 新增: `backend/scripts/import_events.py` (导入四大名著事件数据)
- 修改: `frontend/src/components/GraphView.vue` (支持事件类型节点渲染)

### 8.7 功能⑥: 个性化学习推荐上线

**目标**: BKT + 薄弱点诊断 + 学习计划生成端到端上线

**当前状态**: 后端三个文件完整，缺少意图触发和知识点体系

**BKT算法详解**:
```
输入: 学生多次考试成绩
模型: P(掌握) = P(已知) + (1 - P(已知)) × P(学习)

示例: 学生A, 3次考试, 数学成绩: 75→68→62
  → BKT分析: 三角函数掌握概率0.85, 概率论掌握概率0.40
  → 推荐: 优先复习概率论
```

**实现要点**:
1. 定义知识点体系 (三角函数/概率论/几何/代数/微积分等)
2. BKT算法基于真实学生成绩数据计算掌握概率
3. 在 `classify_intent` 中增加 `learning_recommendation` 意图
4. BKT结果联动 `user_profile` 写入

**改动范围**:
- 修改: `backend/service/agent_service.py` (INTENT_CLASSIFIER_PROMPT 增加 `learning_recommendation` 意图)
- 修改: `backend/service/bkt_service.py` (扩展知识点体系定义)
- 修改: `backend/service/recommendation_service.py` (BKT结果写入user_profile)
- 新增: `backend/data/knowledge_points.json` (知识点体系配置文件)

**触发示例**:
- "S2024001的学习计划" → 自动提取学号→BKT诊断→LLM生成计划
- "帮我诊断S2024001的薄弱知识点" → 成绩趋势分析+下降点检测
- "分析一下S2024001的学习情况" → 综合诊断报告

### 8.8 功能⑦: 多模态交互强化

**当前状态**: 语音交互已基本就绪，以下为增强方向

**增强方向**:
1. **连续对话模式**: 语音输入 → 自动发送 → AI回复 → 自动TTS播放 → 等待下一次语音输入
2. **角色音色切换**: 不同角色使用不同TTS音色:
   - 猪八戒 → 憨厚男声 (sambert-zhichu)
   - 鲁智深 → 粗犷男声 (sambert-zhilang)
   - 林黛玉 → 温柔女声 (sambert-zhifei)
   - 诸葛亮 → 沉稳男声 (sambert-zhixiang)
3. **语音输入按钮突出**: 在BajieChat输入区将语音按钮做得更显眼

**改动范围**:
- 修改: `frontend/src/views/bajie/BajieChat.vue` (连续对话模式 + 音色切换)
- 修改: `frontend/src/components/voice/VoiceInput.vue` (连续录音模式)
- 修改: `backend/utils/tts_util.py` (支持多角色音色映射)

---

## 9. 前端布局升级方案

### 9.1 升级目标

提升用户体验和视觉品质，保持古典四大名著主题氛围不变，不改变项目构造和代码结构。

### 9.2 升级清单

| 升级项 | 优先级 | 描述 | 涉及文件 |
|------|:--:|------|------|
| TabBar 标签页栏 | ⭐⭐⭐ | 记录打开的页面，点击切换，右键关闭 | AppLayout.vue |
| 页面过渡动画 | ⭐⭐⭐ | fade-slide 淡入滑动效果 (250ms) | AppLayout.vue |
| Sidebar Logo 增强 | ⭐⭐ | 增大图标 + "猪八戒智能平台"副标题 | Sidebar.vue |
| Sidebar 菜单 hover 动效 | ⭐⭐ | hover 时金色竖条 + 背景渐变过渡 | Sidebar.vue |
| Sidebar 底部用户区 | ⭐⭐ | 显示当前用户头像 + 用户名 + 角色 + 退出按钮 | Sidebar.vue |
| Sidebar 折叠 tooltip | ⭐ | 折叠时 hover 图标弹出菜单名称 | Sidebar.vue |
| HeaderBar 完整面包屑 | ⭐⭐ | 从"首页/当前页"升级为完整路径 | HeaderBar.vue |
| HeaderBar 全屏按钮 | ⭐ | 右侧加全屏图标按钮 | HeaderBar.vue |
| HeaderBar 通知铃铛 | ⭐ | 预留通知图标按钮 (badge显示0) | HeaderBar.vue |
| HeaderBar 用户下拉增强 | ⭐ | 增加"个人设置"选项 (预留) | HeaderBar.vue |
| HeaderBar 视觉升级 | ⭐⭐ | 渐变背景 + 细金色底边 | HeaderBar.vue |
| 卡片 hover 微交互 | ⭐ | 上浮2px + 阴影加深 | classical.scss |
| 按钮 hover 放大 | ⭐ | 1.02倍 + 过渡动画 | classical.scss |
| 表格行 hover | ⭐ | 藕荷色系背景 | classical.scss |
| 输入框 focus 动效 | ⭐ | 边框颜色过渡动画 | classical.scss |

### 9.3 改动范围

**仅改3个文件 + 1个追加**:

| 文件 | 改动类型 | 说明 |
|------|------|------|
| `AppLayout.vue` | 重写 | 新增TabBar + fade-slide过渡 + 动图层 |
| `Sidebar.vue` | 增强 | Logo升级 + hover动效 + 底部用户信息 |
| `HeaderBar.vue` | 增强 | 完整面包屑 + 全屏按钮 + 通知铃铛 |
| `classical.scss` | 末尾追加 | 全局微交互样式 |

**绝对不碰 (30+文件)**:
- ❌ `router/index.js` — 路由path/name/meta不变
- ❌ `store/modules/auth.js` — 认证逻辑不变
- ❌ `main.js` / `App.vue` — 入口不变
- ❌ `api/` 目录全部14个文件
- ❌ `views/` 目录全部14个业务页面
- ❌ `SmartQueryInput.vue` / `GraphView.vue`
- ❌ `VoiceInput.vue` / `VoiceOutput.vue`
- ❌ `variables.scss` — 变量值不变
- ❌ `classical.scss` — 现有覆盖不删除

### 9.4 布局改造前后对比

**改造前 (当前)**:
```
┌──────────────────────────────────────────────┐
│ el-aside (220px)        │  el-header (60px)  │
│ ┌──────────────┐       │  ┌───────────────┐ │
│ │   Sidebar    │       │  │  HeaderBar    │ │
│ │   - Logo     │       │  │  - 折叠按钮    │ │
│ │   - 12菜单   │       │  │  - 面包屑      │ │
│ │              │       │  │  - 用户下拉    │ │
│ │              │       │  └───────────────┘ │
│ │              │       │  el-main           │
│ │              │       │  ┌───────────────┐ │
│ │              │       │  │  <router-view>│ │
│ │              │       │  │  (fade-slide) │ │
│ └──────────────┘       │  └───────────────┘ │
└──────────────────────────────────────────────┘
```

**改造后 (目标)**:
```
┌──────────────────────────────────────────────────────┐
│ el-aside (220px)          │  el-header (60px)         │
│ ┌──────────────┐         │  ┌─────────────────────┐  │
│ │   Sidebar    │         │  │  HeaderBar          │  │
│ │   - Logo🐷   │         │  │  - 折叠 + 面包屑     │  │
│ │   - 12菜单   │         │  │  - 全屏 + 通知 + 用户│  │
│ │   - hover动效│         │  └─────────────────────┘  │
│ │   - 底部用户 │         │  TabBar                   │
│ │              │         │  ┌─────────────────────┐  │
│ └──────────────┘         │  │ tab1 | tab2 | tab3  │  │
│                          │  └─────────────────────┘  │
│                          │  el-main                  │
│                          │  ┌─────────────────────┐  │
│                          │  │  transition动画层    │  │
│                          │  │  <router-view>      │  │
│                          │  │  (fade-slide)       │  │
│                          │  │                     │  │
│                          │  │  teleport动图层      │  │
│                          │  │  (角色GIF)          │  │
│                          │  └─────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

---

## 10. 角色动图过渡动画方案

### 10.1 需求描述

在页面切换的 fade-slide 过渡动画中，屏幕中央显示当前选中角色的GIF动图，让"猪八戒智能平台"更生动有趣。支持4个角色切换时动态切换对应动图。

### 10.2 四角色与动图对应

| 角色 | Key | 推荐动图主题 | 文件名 | 经典来源 |
|------|------|------|------|------|
| 猪八戒 | bajie | 猪八戒吃西瓜 / 背媳妇 | `bajie.gif` | 86版《西游记》 |
| 鲁智深 | luzhishen | 倒拔垂杨柳 / 喝酒 | `luzhishen.gif` | 98版《水浒传》 |
| 林黛玉 | lindaiyu | 葬花 / 抚琴 | `lindaiyu.gif` | 87版《红楼梦》 |
| 诸葛亮 | zhugeliang | 摇扇 / 抚琴 | `zhugeliang.gif` | 94版《三国演义》 |

### 10.3 GIF规格建议

| 参数 | 推荐值 |
|------|------|
| 尺寸 | 200×200 至 300×300 像素 (正方形) |
| 时长 | 2-4秒循环 |
| 大小 | ≤ 500KB |
| 背景 | 透明或宣纸黄色系 |
| 格式 | GIF (支持透明背景) |

### 10.4 技术方案

**新建文件**:

| 文件 | 说明 |
|------|------|
| `frontend/src/store/modules/character.js` | Pinia全局角色Store (activeCharacter / currentGif / currentName) |

**character.js Store设计**:
```javascript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCharacterStore = defineStore('character', () => {
  const activeCharacter = ref('bajie')

  const characters = {
    bajie:   { key: 'bajie',      name: '猪八戒', gif: 'bajie.gif' },
    luzhishen:{ key: 'luzhishen',  name: '鲁智深', gif: 'luzhishen.gif' },
    lindaiyu: { key: 'lindaiyu',   name: '林黛玉', gif: 'lindaiyu.gif' },
    zhugeliang:{ key: 'zhugeliang',name: '诸葛亮', gif: 'zhugeliang.gif' },
  }

  const currentGif  = computed(() => characters[activeCharacter.value]?.gif  || 'bajie.gif')
  const currentName = computed(() => characters[activeCharacter.value]?.name || '猪八戒')

  function setCharacter(key) { activeCharacter.value = key }

  return { activeCharacter, currentGif, currentName, setCharacter, characters }
})
```

**修改文件**:

| 文件 | 改动 | 说明 |
|------|------|------|
| `BajieChat.vue` | +2处 | 导入characterStore + 切换角色时调用 `characterStore.setCharacter()` |
| `AppLayout.vue` | 重写 `<router-view>` 区域 | 新增 `<teleport to="body">` 动图层 |

**AppLayout.vue 动图层设计**:
```vue
<teleport to="body">
  <div v-if="showTransitionGif" class="transition-gif-overlay">
    <div class="transition-gif-box">
      <img :src="getGifUrl(characterStore.currentGif)"
           :alt="characterStore.currentName"
           class="transition-gif-img" />
      <span class="transition-gif-label">{{ characterStore.currentName }}</span>
    </div>
  </div>
</teleport>
```

**视觉效果**:
- 页面切换触发 → 半透明宣纸色遮罩 (毛玻璃背景模糊效果)
- 角色GIF弹跳放大出现 (scale 0.5 → 1.15 → 1.0, 250ms弹性动画)
- GIF带金色边框 + 古典阴影 + 角色名称 (楷体朱红色)
- 角色名称显示在GIF下方
- 250ms后自动消失 (与fade-slide过渡同步)
- `pointer-events: none` 不阻挡点击，不阻塞页面交互

### 10.5 GIF文件获取方式

用户需自行获取GIF文件到 `frontend/src/assets/gifs/` 目录:

| 方式 | 说明 |
|------|------|
| 百度图片搜索 | 搜索"猪八戒吃西瓜 gif"、"林黛玉 葬花 gif"、"鲁智深 倒拔垂杨柳 gif"、"诸葛亮 摇扇 gif" |
| 花瓣网/Pinterest | 搜索"西游记 表情包"、"红楼梦 经典镜头" |
| 自制 | 截取电视剧/动画片段 → ezgif.com 转GIF → 裁切到200×200 |
| 86版西游记素材 | 猪八戒吃西瓜、背媳妇、偷懒睡觉等经典镜头 |
| 87版红楼梦素材 | 林黛玉葬花、抚琴、焚稿等经典镜头 |

**文件存放路径**:
```
frontend/src/assets/gifs/
├── bajie.gif          # 猪八戒动图
├── luzhishen.gif      # 鲁智深动图
├── lindaiyu.gif       # 林黛玉动图
└── zhugeliang.gif     # 诸葛亮动图
```

---

## 11. 完整实施路线图

### 11.1 阶段一: 前端布局升级 (3-4天)

```
Day 1: classical.scss 末尾追加全局微交互样式
  ├── 卡片hover上浮2px+阴影加深
  ├── 按钮hover 1.02倍放大
  ├── 表格行hover藕荷色背景
  └── 输入框focus边框颜色过渡

Day 2: AppLayout.vue 重写
  ├── 新增TabBar标签页栏 (open/close/switch)
  ├── fade-slide过渡动画 (250ms)
  └── 角色动图过渡图层 (teleport)

Day 3: Sidebar.vue + HeaderBar.vue 增强
  ├── Sidebar: Logo升级+副标题+hover金色竖条+底部用户区
  └── HeaderBar: 完整面包屑+全屏按钮+通知铃铛+渐变背景

Day 4: 角色动图过渡动画 + 全局角色Store
  ├── 新建 store/modules/character.js
  ├── BajieChat.vue 集成角色Store
  └── 下载/准备4个角色GIF动图文件
```

### 11.2 阶段二: 后端AI增强验证 (7天)

```
Day 5: 贝叶斯分类完善
  ├── 准备预训练数据 (500条标注语料, 9种意图)
  ├── 添加模型持久化 (pickle save/load)
  └── 启动时自动加载预训练模型

Day 6: ReAct推理循环端到端打通
  ├── classify_intent增加deep_reasoning意图
  ├── BajieChat增加ReAct推理触发入口
  └── 验证Think→Act→Observe循环稳定性

Day 7-8: 多智能体协同前端管理面板
  ├── 新增AgentDashboard.vue (状态可视化)
  ├── WebSocket状态广播接口
  └── 任务执行日志 + Agent间消息日志

Day 9: Function Calling增强
  ├── graph_query工具注册验证
  ├── Agent独立FC决策能力
  └── 工具调用日志统计

Day 10: 知识图谱深度推理上线
  ├── Neo4j数据模型扩展 (Event节点+CAUSES边+faction+chapter)
  ├── 导入四大名著事件数据
  └── graph_reasoning.py与真实数据对接

Day 11: BKT学习推荐上线
  ├── 知识点体系定义 (knowledge_points.json)
  ├── classify_intent增加learning_recommendation意图
  └── BKT结果联动user_profile写入

Day 12: 多模态交互强化
  ├── 连续对话模式 (语音→自动回复→自动TTS)
  └── 角色音色切换 (4角色不同TTS音色)
```

### 11.3 阶段三: 联调测试 (2天)

```
Day 13: 前后端联调 + 功能验证
  ├── 前端布局升级后所有页面功能正常
  ├── 角色动图过渡动画正常
  ├── ReAct推理循环功能验证
  ├── 贝叶斯分类准确性验证
  ├── 图谱深度推理结果验证
  ├── BKT学习推荐结果验证
  └── 多模态交互端到端验证

Day 14: 修复Bug + 文档更新
  ├── 修复联调中发现的Bug
  ├── 更新技术文档
  └── 最终功能验收
```

### 11.4 实施优先级矩阵

```
                    重要程度
                    高        中        低
               ┌─────────┬─────────┬─────────┐
          高   │ 布局升级 │ 动图动画 │ 通知铃铛 │
               │ TabBar  │ ReAct   │ 全屏按钮 │
实       ──────┼─────────┼─────────┼─────────┤
施          中 │ 贝叶斯  │ FC增强  │ 个人设置 │
难              │ 图谱推理│ BKT推荐 │ 音色切换 │
度       ──────┼─────────┼─────────┼─────────┤
          低   │ 微交互  │ 菜单动效│ 连续对话 │
               │         │         │         │
               └─────────┴─────────┴─────────┘
```

---

## 12. Claude提示词汇总

> 以下提示词可直接复制给Claude进行对应功能的开发实现

### 12.1 前端布局升级提示词

```
你是一个资深前端开发工程师。请帮我升级一个Vue3+Element Plus项目的前端布局。

项目背景：
- 学生管理系统+四大名著角色AI平台
- 古典主题色系 (朱红/黛蓝/墨黑/宣纸黄/金色)
- 已有侧边栏(Sidebar)、顶部栏(HeaderBar)、主内容区

需要改动的文件：
1. AppLayout.vue - 重写主布局
2. Sidebar.vue - 增强侧边栏
3. HeaderBar.vue - 增强顶部栏
4. classical.scss - 末尾追加全局微交互样式

具体要求：
1. AppLayout.vue新增TabBar标签页栏（记录打开的页面，点击切换，右键关闭），fade-slide过渡动画
2. Sidebar.vue增强Logo（增大图标+副标题"猪八戒智能平台"），hover金色竖条动效，底部用户信息区
3. HeaderBar.vue完整面包屑，全屏按钮，通知铃铛，渐变背景+金色底边
4. classical.scss追加卡片hover上浮、按钮hover放大、表格行hover藕荷色、输入框focus动效

绝对不要修改：
- router/index.js (路由配置)
- store/modules/auth.js (认证逻辑)
- variables.scss (样式变量)
- 所有views/页面和api/接口文件
- main.js和App.vue入口文件

请保持原有古典氛围不变，只提升用户体验和视觉感。
```

### 12.2 角色动图过渡动画提示词

```
你是一个Vue3前端开发工程师。请帮我在页面切换动画中加入角色GIF动图。

项目背景：
- 4个四大名著角色：猪八戒(bajie)、鲁智深(luzhishen)、林黛玉(lindaiyu)、诸葛亮(zhugeliang)
- 页面切换已有fade-slide过渡动画（250ms）

需要新建的文件：
1. store/modules/character.js - Pinia全局角色Store
   - 存储当前选中角色
   - 提供currentGif(当前角色GIF路径)和currentName(当前角色名)
   - 4个角色配置：key/name/gif

需要修改的文件：
1. AppLayout.vue - 在router-view过渡区域用<teleport to="body">添加动图层
   - showTransitionGif状态控制显示/隐藏
   - 半透明宣纸色遮罩+毛玻璃效果
   - GIF弹跳放大动画(scale 0.5→1.15→1.0, 250ms)
   - 金色边框+阴影+角色名称(楷体朱红色)
   - pointer-events:none不阻挡点击
   - 250ms后自动消失

2. BajieChat.vue - 导入characterStore，切换角色时调用setCharacter()

GIF文件位置：frontend/src/assets/gifs/bajie.gif (及luzhishen/lindaiyu/zhugeliang)

绝对不要修改：路由配置、认证逻辑、样式变量、API接口、其他页面
```

### 12.3 贝叶斯意图分类完善提示词

```
你是一个Python后端开发工程师。请帮我完善一个已有的朴素贝叶斯意图分类器。

已有文件：backend/service/bayesian_classifier.py
- 使用MultinomialNB + TF-IDF (char_wb, ngram 1-3, max_features=5000)
- 已有classify()和add_sample()方法
- 已有种子关键词兜底机制
- 已有自我学习机制(累计20条自动重训练)

需要完善的功能：
1. 添加模型持久化：save_model()将vectorizer和model保存为pickle文件
2. 添加模型加载：load_model()在启动时加载预训练模型，跳过初始训练
3. 准备预训练数据：创建backend/data/intent_training_samples.json
   - 至少500条标注语料，均匀覆盖9种意图
   - 格式: [{"text": "用户消息", "intent": "意图代码"}, ...]
4. 修改agent_service.py：启动时自动加载预训练模型

绝对不要修改：classify_intent_hybrid()的混合分类逻辑、OrchestratorAgent、Agent路由表
```

### 12.4 ReAct推理循环端到端打通提示词

```
你是一个Python后端开发工程师。请帮我端到端打通ReAct推理循环。

已有文件：backend/agent/react_agent.py
- Thought→Action→Observation循环(最多5轮)
- 支持3个工具：nl2sql(数据库查询)/rag_search(知识检索)/graph_query(图谱查询)
- orchestrator_agent.py已挂载reAct_agent

需要完善的功能：
1. 在agent_service.py的INTENT_CLASSIFIER_PROMPT中增加deep_reasoning意图
   - 描述：需要多步推理分析的复杂问题（如"分析张三成绩趋势并找出原因"）
2. 在orchestrator_agent.py的execute_single()路由表中增加deep_reasoning路由
3. 在react_agent.py中增加：
   - 超时保护(单轮30秒)
   - 错误重试(最多2次)
   - 推理过程日志

绝对不要修改：其他Agent的execute()方法、路由表其他条目、意图分类其他分支
```

### 12.5 知识图谱深度推理上线提示词

```
你是一个Python后端+Neo4j开发工程师。请帮我上线知识图谱深度推理功能。

已有文件：
- backend/service/graph_reasoning.py (推理逻辑完整)
- backend/service/graph_service.py (基础查询就绪)
- backend/utils/neo4j_util.py (Neo4j客户端封装)

需要扩展的Neo4j数据模型：
1. 新建Event节点：
   - 属性: name(事件名), chapter(章回), book(书籍), description(事件描述), type(事件类型)
   - 示例: {name:"大闹天宫", chapter:7, book:"novel_xiyou", description:"孙悟空大闹天宫", type:"battle"}
2. 新建CAUSES关系边：
   - 连接Event节点，表示因果链
   - 示例: (大闹天宫)-[:CAUSES {reason:"触怒天庭"}]->(被压五行山)
3. Person节点加faction属性：
   - 三国: 蜀/魏/吴；水浒: 梁山/朝廷；西游: 佛/道/妖；红楼: 贾府/其他
4. Person节点加chapter属性(首次出场章回)

需要新增的脚本：
- backend/scripts/import_events.py (导入四大名著事件数据)
- 修改scripts/init_neo4j.py (扩展数据模型创建)

绝对不要修改：graph_service.py基础查询方法、graph_controller.py接口、Neo4j连接配置
```

### 12.6 BKT学习推荐上线提示词

```
你是一个Python后端开发工程师。请帮我上线个性化学习推荐功能。

已有文件：
- backend/service/bkt_service.py (BKT算法)
- backend/service/recommendation_service.py (薄弱点诊断+LLM学习计划)
- backend/agent/recommendation_agent.py (Agent入口)

需要完善的功能：
1. 定义知识点体系：创建backend/data/knowledge_points.json
   - 分级知识点：一级(数学/语文/英语) → 二级(代数/几何/阅读/写作) → 三级(三角函数/数列/概率论)
2. 在agent_service.py的INTENT_CLASSIFIER_PROMPT中增加learning_recommendation意图
3. 在orchestrator_agent.py的execute_single()路由表中增加learning_recommendation路由
4. BKT结果联动user_profile：
   - 每次诊断后将mastery_probability写入user_profile
   - 在user_profile.py实体中新增mastery_score字段

绝对不要修改：其他Agent、意图分类其他分支、BKT核心算法逻辑
```

### 12.7 多模态交互强化提示词

```
你是一个前端Vue3开发工程师。请帮我强化语音交互功能。

已有功能：
- VoiceInput.vue (录音按钮, MediaRecorder API, 15秒倒计时)
- VoiceOutput.vue (播放按钮, 浏览器TTS优先+后端TTS回退)
- audio_controller.py (recognize/synthesize接口)
- 已集成到BajieChat.vue

需要增加的功能：
1. 连续对话模式：
   - 在BajieChat.vue中增加"连续对话"开关
   - 开启后：语音输入→自动发送→AI回复→自动TTS播放→等待下一次语音输入
2. 角色音色切换：
   - 在BajieChat.vue中根据activeCharacter切换TTS音色
   - 猪八戒→sambert-zhichu(憨厚男声)
   - 鲁智深→sambert-zhilang(粗犷男声)
   - 林黛玉→sambert-zhifei(温柔女声)
   - 诸葛亮→sambert-zhixiang(沉稳男声)
   - 修改tts_util.py增加音色映射表

绝对不要修改：VoiceInput/VoiceOutput组件内部逻辑、audio_controller接口、后端TTS/ASR核心实现
```

---

## 13. 风险与注意事项

### 13.1 高风险区域

| 风险 | 影响 | 缓解措施 |
|------|------|------|
| orchestrator_agent.py 改动过大 | 所有Agent路由失效 | 已保留execute_single()方法，新旧并存 |
| Neo4j数据模型扩展 | 图谱查询错误 | 新查询独立方法，旧查询不变 |
| 前端TabBar与路由守卫冲突 | 页面跳转异常 | 不修改路由配置，TabBar仅监听route变化 |
| 贝叶斯分类器未训练 | 所有意图回退LLM | 预先准备500条标注语料 |
| ReAct循环卡死 | 对话无限循环 | 最大5轮限制 + 超时保护(30秒/轮) |
| GIF动图文件过大 | 页面加载变慢 | 限制≤500KB，异步加载 |
| 多Agent并行内存占用 | 服务器压力 | 限制最多3个并行子任务 |
| LLM API调用失败 | 功能不可用 | 所有Agent含try/except兜底，回退到角色闲聊 |

### 13.2 外部依赖状态

| 依赖 | 功能 | 状态 |
|------|------|:--:|
| MySQL | 业务数据 + 记忆存储 | ✅ 已配置 |
| Milvus | 向量检索 (四大名著+记忆) | ✅ 已配置，需运行init_milvus.py+ingest_novel.py |
| Neo4j | 人物关系图谱 | ✅ 已配置，需运行init_neo4j.py |
| DeepSeek API | LLM调用 (对话/分类/提取/SQL) | ✅ 已配置 |
| 阿里云 DashScope | TTS/ASR/备用Qwen | ✅ 已配置 |
| 和风天气 | 实时天气查询 | ✅ 已配置 |
| scikit-learn | 贝叶斯分类器 | ⚠️ 需安装 (`pip install scikit-learn`) |
| GIF动图文件 | 角色过渡动画 | ⚠️ 需手动下载到 `frontend/src/assets/gifs/` |
| 标注语料 | 贝叶斯预训练 | ⚠️ 需手动准备500条 `backend/data/intent_training_samples.json` |
| 事件数据 | 图谱深度推理 | ⚠️ 需手动导入 `backend/scripts/import_events.py` |

### 13.3 实施铁律

1. **只加不删**: 旧代码永远保留，新功能通过if/else分支或新增方法实现
2. **先测后改**: 每次改动前先运行现有功能确认正常
3. **逐步验证**: 每完成一个功能立即测试，不堆积多个改动一起测试
4. **保留回退**: 所有新功能含try/except兜底，失败不影响核心功能
5. **不改接口**: 前端不修改API接口调用方式，后端不修改路由前缀
6. **不改配置**: 不修改.env文件、vite.config.js、package.json、requirements.txt
7. **不改路由**: 不修改router/index.js中的path/name/meta配置
8. **不改样式变量**: 不修改variables.scss中的任何变量值

### 13.4 测试验证清单

| 测试项 | 验证方式 | 预期结果 |
|------|------|------|
| 前端布局正常显示 | 打开所有页面 | 布局无错位，TabBar正常，过渡动画流畅 |
| 角色GIF动图正常 | 切换页面 | 显示对应角色动图，250ms后消失 |
| 贝叶斯分类正常 | 发送测试消息 | 高置信度命中贝叶斯，低置信度回退LLM |
| ReAct推理正常 | 发送"分析张三成绩" | 展示Think→Act→Observe→Answer完整流程 |
| 图谱深度推理正常 | 发送"为什么孙悟空被压五行山" | 返回因果链+LLM解释 |
| BKT学习推荐正常 | 发送"S2024001学习计划" | 返回掌握度+薄弱点+学习计划 |
| 语音交互正常 | 点击录音/播放按钮 | 正常录音识别/播放合成 |
| 多Agent并行正常 | 发送复合问题 | 并行执行后LLM合并结果 |
| 记忆框架正常 | 多次对话后查看 | 记忆提取存储+检索注入正常 |
| 所有原有功能正常 | 回归测试 | 学生CRUD/仪表盘/对话等全部正常 |

---

## 14. 对话历史全记录

> 此章节记录了本项目的完整对话历史，包含所有需求讨论、问题诊断、方案设计过程

### 14.1 对话一: 多智能体协同实现

**用户问题**: 如果我将这个多智能体协同在这个项目中实现后，我想将整个前端页面换一个高级的布局，整体前端页面氛围可以不用换，主要想提升用户的体验感和视觉感，但是这样做会不会改变整个项目的构造？会不会使项目代码出现很多隐形的问题？只给建议和回答

**讨论要点**:
- 确认多智能体协同架构已设计完成
- 分析前端布局改造对项目构造的影响
- 结论：布局改造仅影响3个布局组件文件，不改变项目构造，不会引入隐形问题

### 14.2 对话二: 8项核心能力诊断

**用户问题**: 依次详细解答8个问题：
1. 多智能体协同是否已创建
2. 记忆框架是否还存在且可执行
3. 智能体能否自主调用数据库/RAG/图谱
4. 能否实现ReAct推理循环
5. 能否实现贝叶斯意图分类，是否会影响已有LLM分类
6. 能否实现知识图谱深度推理
7. 能否实现个性化学习推荐
8. 项目是否实现多模态交互

**诊断结论**:
1. 多智能体协同 ✅ 已创建
2. 记忆框架 ✅ 完整可执行
3. 自主调用 ✅ 已实现 (Function Calling + ToolRegistry)
4. ReAct推理 🟡 代码已创建，待业务验证
5. 贝叶斯分类 🟡 代码已创建，与LLM并存不冲突
6. 图谱推理 🟡 逻辑就绪，Neo4j数据待扩展
7. 学习推荐 🟡 文件就绪，待真实数据验证
8. 多模态交互 🟢 已实现，能听能说

### 14.3 对话三: 7大功能实现可行性分析

**用户问题**: 如果实现所有7大功能，会不会将整个项目的逻辑改乱？只给建议和回答，不要改代码

**讨论要点**:
- 逐一分析每个功能的改动范围
- 结论：全部实现不会改乱项目，因为采用"只加不删"策略
- 核心编排器新旧逻辑并存，路由表一行未删作为fallback
- 新功能通过if/else分支或新增方法实现

### 14.4 对话四: Claude提示词生成

**用户问题**: 基于上一轮对话内容，帮我总结，然后告诉我应该如何改？直接给能给到Claude对应改的提示词就行

**输出内容**:
- 为7大功能生成了可直接复制给Claude的提示词
- 每个提示词包含：项目背景、已有文件、需要改动的内容、绝对不要修改的部分

### 14.5 对话五: 前端布局升级

**用户问题**: 浏览整个项目，基于现在项目的所有功能，如果我想将前端界面的布局按照现在的功能重新布局一下，换成高级点的布局，然后整体前端页面氛围可以不用换，主要想提升用户的体验感和视觉感，但是这样做会不会改变整个项目的构造？如果不会改变整个项目的结构和代码，那就给一个给到Claude的调整前端界面的提示词

**讨论要点**:
- 列出15项布局升级清单 (TabBar/过渡动画/Sidebar增强/HeaderBar增强/微交互)
- 确认仅改动3个文件+1个追加，不改变项目构造
- 生成了前端布局升级的Claude提示词

### 14.6 对话六: 角色动图过渡动画

**用户问题**: 把那个黑底白字的区域（页面切换 fade-slide 动画）改成 "孙悟空翻跟头" 或者 "猪八戒吃西瓜" 的动图，4个人物都需要加上动态图，切换的时候跟着切换。给我方案，然后给Claude一段能加进去的提示词

**讨论要点**:
- 设计4角色动图对应方案 (猪八戒吃西瓜/鲁智深倒拔垂杨柳/林黛玉葬花/诸葛亮摇扇)
- 技术方案：新建全局角色Store + AppLayout动图层 (teleport)
- GIF规格建议：200×200, ≤500KB, 2-4秒循环
- GIF获取方式：百度图片/花瓣网/自制(ezgif.com)
- 生成了角色动图过渡动画的Claude提示词

### 14.7 对话七: 完整技术文档生成

**用户问题**: 基于现在整个项目，浏览项目所有文件以及前面所有的对话内容，帮我生成一份详细的并且包含所有我跟你讨论的需求及问题的技术文档；文档内必须包含我所有的想法及构思

**输出内容**: 本文档 — 完整覆盖所有对话历史、需求、功能、技术方案、实施路线

---

## 附录

### A. 数据库表结构速查

| 表名 | 关键字段 | 说明 |
|------|------|------|
| `student` | student_no, student_name, class_id, gender, age, major | 学生信息 |
| `class_info` | class_id, class_name, head_teacher_id | 班级信息 |
| `score` | student_no, exam_order, score | 成绩 (student_no+exam_order唯一) |
| `employment` | student_no, company_name, offer_job, salary | 就业信息 |
| `course_info` | course_id, course_name, teacher_id, class_id | 课程信息 |
| `teacher` | teacher_id, teacher_name, phone | 教师信息 |
| `users` | username, password, role, real_name | 用户 (4种角色) |
| `operation_log` | operator, operation_type, target, detail | 操作日志 |
| `conversation_history` | user_id, session_id, role, content, agent_type | 对话历史 |
| `memory_fragment` | user_id, content, importance, memory_type, chunk_id | 记忆片段 |
| `user_profile` | user_id, interaction_count, last_emotion, preferred_topics, personality_tags | 用户画像 |
| `permissions` | role_id, resource, action | 权限配置 |
| `document_chunk` | chunk_id, novel_name, chapter_num, content | RAG文档索引 |
| `lantern_riddle` | riddle, answer, hint, difficulty | 灯谜题库 |
| `qa_pair` | question, answer, category | 问答对 |

### B. API接口速查

| 路由前缀 | 方法 | 说明 |
|------|------|------|
| `/api/v1/auth` | POST login/logout/refresh | 认证 |
| `/api/v1/agent` | POST chat/chat/stream/classify | 多智能体对话 |
| `/api/v1/students` | GET/POST/PUT/DELETE | 学生CRUD |
| `/api/v1/classes` | GET/POST/PUT/DELETE | 班级CRUD |
| `/api/v1/scores` | GET/POST/PUT/DELETE | 成绩CRUD |
| `/api/v1/employment` | GET/POST/PUT/DELETE | 就业CRUD |
| `/api/v1/courses` | GET/POST/PUT/DELETE | 课程CRUD |
| `/api/v1/logs` | GET | 日志查询 |
| `/api/v1/dashboard` | GET | 仪表盘数据 |
| `/api/v1/users` | GET/POST/PUT/DELETE | 用户管理 |
| `/api/v1/rag` | POST ask | RAG知识问答 |
| `/api/v1/bajie` | POST riddle/poetry/social/emotional | 八戒功能 |
| `/api/v1/graph` | GET person/relations/path/visualization | 知识图谱 |
| `/api/v1/smart-query` | POST query | 智能问数 |
| `/api/v1/memory` | GET/POST/DELETE sessions | 记忆管理 |
| `/api/v1/memory` | GET proactive/stream | 主动对话SSE |
| `/api/v1/audio` | POST recognize/synthesize | 语音交互 |
| `/api/v1/weather` | GET | 天气查询 |
| `/api/v1/fortune` | GET | 运势占卜 |
| `/api/v1/system` | GET health | 健康检查 |

### C. 关键代码文件依赖关系图

```
main.py
├── config.py (Settings)
├── database.py (engine + SessionLocal)
├── dependencies.py (get_db + get_current_user)
├── middleware/ (异常处理)
├── controller/ (18个)
│   ├── agent_controller.py
│   │   └── agent_service.py
│   │       ├── bayesian_classifier.py
│   │       └── orchestrator_agent.py
│   │           ├── base_agent.py
│   │           ├── data_agent.py → nl2sql_service.py
│   │           ├── knowledge_agent.py → rag_service.py
│   │           │   ├── embedding_util.py
│   │           │   ├── milvus_util.py
│   │           │   ├── book_router.py
│   │           │   └── graph_service.py → neo4j_util.py
│   │           ├── emotional_agent.py → deepseek_util.py
│   │           ├── social_agent.py → deepseek_util.py
│   │           ├── game_agent.py
│   │           ├── persona_agent.py → deepseek_util.py + memory_retriever.py
│   │           ├── weather_agent.py → weather_util.py
│   │           ├── fortune_agent.py → fortune_util.py
│   │           ├── react_agent.py
│   │           │   ├── nl2sql_service.py
│   │           │   ├── rag_service.py
│   │           │   └── graph_service.py
│   │           ├── recommendation_agent.py
│   │           │   ├── recommendation_service.py
│   │           │   │   └── bkt_service.py
│   │           ├── task_decomposer.py → deepseek_util.py
│   │           ├── agent_message_bus.py
│   │           └── tool_registry.py
│   ├── memory_controller.py
│   │   └── memory_service.py
│   │       ├── memory_dao.py
│   │       └── memory_extractor.py
│   │           ├── embedding_util.py
│   │           └── milvus_util.py
│   ├── audio_controller.py
│   │   ├── tts_util.py
│   │   └── asr_util.py
│   └── ... (其他14个controller)
│
└── entity/ (15个ORM实体)
```

### D. 项目启动命令

```bash
# 后端启动
cd backend
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 前端启动
cd frontend
npm install
npm run dev

# 初始化脚本 (按顺序执行)
python scripts/init_db.py          # 创建MySQL表
python scripts/init_milvus.py      # 创建Milvus集合
python scripts/ingest_novel.py     # 导入四大名著到Milvus
python scripts/init_neo4j.py       # 初始化Neo4j人物图谱
python scripts/hash_passwords.py   # 密码哈希加密
```

### E. 环境变量 (.env) 配置示例

```env
# MySQL
DB_USER=root
DB_PASSWORD=123456
DB_HOST=localhost
DB_PORT=3306
DB_NAME=student-mananger

# DeepSeek
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_EMBEDDING_MODEL=text-embedding-3-small

# 阿里云DashScope
ALIYUN_API_KEY=sk-xxxxxxxxxxxx
ALIYUN_TTS_MODEL=sambert-zhichu
ALIYUN_ASR_MODEL=qwen-audio-asr

# Milvus
MILVUS_HOST=127.0.0.1
MILVUS_PORT=19530

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# JWT
JWT_SECRET_KEY=student-manager-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=120

# 天气
WEATHER_API_KEY=xxxxxxxxxxxx
```

---

> **文档结束**
>
> 本文档完整记录了"学生管理系统 + 猪八戒多智能体AI平台"的所有技术细节，
> 涵盖项目概述、系统架构、完整文件清单、功能矩阵、多智能体架构、记忆框架、
> 核心能力诊断、功能增强方案、前端布局升级、角色动图动画、实施路线图、
> Claude提示词、风险与注意事项、对话历史全记录。
>
> 文档版本: v2.0.0 | 日期: 2026-06-01 | 作者: AI编程助手