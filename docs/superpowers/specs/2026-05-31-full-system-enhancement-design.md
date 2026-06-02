# 学生管理系统 + 猪八戒多智能体AI平台 全面增强设计文档

> **项目**: 学生管理系统 + 猪八戒多智能体AI问答
> **文档日期**: 2026-05-31
> **版本**: v1.0.0
> **状态**: 设计方案阶段，基于全部对话内容生成
> **目标**: 记录所有已讨论的功能需求、技术方案、操作指南，作为后续实施的完整蓝图

---

## 目录

- [一、项目概述](#一项目概述)
- [二、完整技术架构](#二完整技术架构)
- [三、项目文件清单](#三项目文件清单)
- [四、当前已实现功能](#四当前已实现功能)
- [五、多智能体架构详解](#五多智能体架构详解)
- [六、记忆框架详解](#六记忆框架详解)
- [七、8 项核心能力诊断](#七8-项核心能力诊断)
- [八、7 大功能增强方案](#八7-大功能增强方案)
- [九、前端布局升级方案](#九前端布局升级方案)
- [十、角色动图过渡动画方案](#十角色动图过渡动画方案)
- [十一、完整实施路线图](#十一完整实施路线图)
- [十二、Claude 提示词汇总](#十二claude-提示词汇总)
- [十三、风险与注意事项](#十三风险与注意事项)
- [十四、对话历史摘要](#十四对话历史摘要)

---

## 一、项目概述

### 1.1 项目定位

学生管理系统 + 猪八戒多智能体AI问答平台。将学生管理系统（CRUD/数据看板/智能问数）与四大名著角色 AI（猪八戒/鲁智深/林黛玉/诸葛亮）融合在一个平台中，支持多角色对话、知识问答、灯谜游戏、知识图谱可视化等功能。

### 1.2 技术栈总览

| 层级 | 技术 | 版本 | 用途 |
|------|------|------|------|
| **前端框架** | Vue 3 (Composition API) + Vite | 3.5+ / 6.0+ | SPA 单页应用 |
| **UI 组件库** | Element Plus | 2.9+ | 全局 UI 组件，中文语言包 |
| **状态管理** | Pinia | 2.3+ | auth 认证模块 |
| **路由** | Vue Router 4 (hash 模式) | 4.5+ | 12个路由 + 全局权限守卫 |
| **图表** | ECharts | 5.5+ | 仪表盘 4 个图表 |
| **HTTP 客户端** | Axios | 1.7+ | API 请求封装 |
| **样式** | SCSS + Element Plus CSS 变量 | - | 古典四大名著主题色系 |
| **图标** | @element-plus/icons-vue | 2.3+ | 全局注册 |
| **后端框架** | FastAPI | - | RESTful + SSE 流式 |
| **ORM** | SQLAlchemy | - | MySQL 数据库操作 |
| **数据库** | MySQL | - | 业务数据 + 对话记忆存储 |
| **向量数据库** | Milvus (pymilvus) | - | 四大名著文本 + 记忆片段向量 |
| **图数据库** | Neo4j | - | 四大名著人物关系图谱 |
| **LLM** | DeepSeek API (OpenAI 兼容) | deepseek-chat | 对话生成 / 意图分类 / 记忆提取 |
| **Embedding** | DeepSeek text-embedding-3-small | - | 向量化文本 |
| **备用 LLM** | 阿里云 DashScope (Qwen) | qwen-turbo | 备用对话 |
| **TTS** | 阿里云 DashScope (sambert-zhichu) | - | 语音合成 |
| **ASR** | 阿里云 DashScope (qwen-audio-asr) | - | 语音识别 |
| **认证** | JWT (access_token + refresh_token) | HS256 | 用户认证 |
| **配置** | Pydantic Settings (.env) | - | 环境变量管理 |

### 1.3 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      前端 (Vue 3 + Vite)                     │
│  ┌─────────┐  ┌──────────┐  ┌────────────┐  ┌───────────┐  │
│  │AppLayout│  │ Sidebar  │  │ HeaderBar  │  │ 16 Views  │  │
│  │ 主布局   │  │ 12菜单   │  │ 面包屑用户  │  │ 业务页面   │  │
│  └─────────┘  └──────────┘  └────────────┘  └───────────┘  │
│  ┌─────────┐  ┌──────────┐  ┌────────────┐  ┌───────────┐  │
│  │VoiceIn  │  │ VoiceOut │  │GraphView  │  │SmartQuery │  │
│  │语音输入  │  │ 语音输出  │  │ 图谱展示   │  │ 智能问数   │  │
│  └─────────┘  └──────────┘  └────────────┘  └───────────┘  │
│  ┌─────────┐  ┌──────────┐  ┌────────────┐                 │
│  │ Pinia   │  │ Axios    │  │ Classical  │                 │
│  │ Auth    │  │ 14 API   │  │ Theme SCSS │                 │
│  └─────────┘  └──────────┘  └────────────┘                 │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP / SSE
┌──────────────────────▼──────────────────────────────────────┐
│                  后端 FastAPI (Python)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    18 Controller                       │  │
│  │ agent / auth / student / class / score / employment   │  │
│  │ course / log / dashboard / user / rag / bajie         │  │
│  │ graph / smart_query / memory / proactive / audio      │  │
│  │ weather / fortune                                     │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   Agent 编排层 (12文件)                 │  │
│  │  Orchestrator → 8专家Agent + ReAct + Recommendation  │  │
│  │  + TaskDecomposer + ResultMerger + MessageBus         │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    Service 层 (20文件)                  │  │
│  │  agent / rag / graph / nl2sql / memory / proactive    │  │
│  │  bkt / bayesian_classifier / graph_reasoning / etc    │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                     Utils (20文件)                      │  │
│  │  deepseek / qwen / embedding / milvus / neo4j         │  │
│  │  tts / asr / memory_extractor / memory_retriever      │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐
   │  MySQL   │  │  Milvus  │  │  Neo4j   │
   │ 业务+记忆 │  │ 向量检索  │  │ 人物图谱  │
   └──────────┘  └──────────┘  └──────────┘
        │              │              │
        ▼              ▼              ▼
   ┌──────────────────────────────────────┐
   │          外部 API 调用                 │
   │  DeepSeek / 阿里云DashScope / 和风天气  │
   └──────────────────────────────────────┘
```

---

## 二、完整技术架构

### 2.1 前端架构

#### 2.1.1 入口文件

[main.js](file:///d:/项目阶段/项目课0505/管理系统+智能问答-trae测试版/frontend/src/main.js) — Vue3 应用入口：
- 创建 Pinia 状态管理实例
- 注册 Vue Router 路由系统
- 注册 Element Plus（中文语言包）
- 全局注册所有 Element Plus 图标组件
- 引入全局样式：`global.scss` + `classical.scss`

[App.vue](file:///d:/项目阶段/项目课0505/管理系统+智能问答-trae测试版/frontend/src/App.vue) — 根组件，仅包含 `<router-view />`

#### 2.1.2 路由系统

[router/index.js](file:///d:/项目阶段/项目课0505/管理系统+智能问答-trae测试版/frontend/src/router/index.js) — 12 个路由：

| 路由路径 | 组件 | 权限要求 | 描述 |
|------|------|------|------|
| `/login` | Login.vue | 无需认证 (noAuth: true) | 登录页 |
| `/dashboard` | Dashboard.vue | 登录即可 | 数据看板 |
| `/students` | StudentList.vue | student:view | 学生管理 |
| `/classes` | ClassList.vue | class:view | 班级管理 |
| `/scores` | ScoreList.vue | score:view | 成绩管理 |
| `/employment` | EmploymentList.vue | employment:view | 就业管理 |
| `/courses` | CourseList.vue | course:view | 课程管理 |
| `/logs` | OperationLogs.vue | log:view | 操作日志 |
| `/system/users` | UserManage.vue | user:manage | 用户管理 |
| `/bajie/chat` | BajieChat.vue | 登录即可 | 八戒对话 |
| `/bajie/qa` | KnowledgeQA.vue | 登录即可 | 知识问答 |
| `/bajie/games` | BajieGames.vue | 登录即可 | 八戒游戏 |
| `/bajie/social` | SocialAssistant.vue | 登录即可 | 社交助手 |

全局路由守卫逻辑：
- 检查 localStorage 中的 `access_token`
- 未登录 → 跳转 `/login`
- 已登录访问 `/login` → 跳转 `/dashboard`

#### 2.1.3 状态管理

[store/modules/auth.js](file:///d:/项目阶段/项目课0505/管理系统+智能问答-trae测试版/frontend/src/store/modules/auth.js) — Pinia Auth Store：
- `token` / `refreshToken` / `userInfo` — 持久化到 localStorage
- `isLoggedIn` — computed，判断登录状态
- `role` / `permissions` — 从 userInfo 计算
- `login()` / `logout()` / `refreshUserInfo()` / `changePassword()` — 操作方法

#### 2.1.4 布局组件

[AppLayout.vue](file:///d:/项目阶段/项目课0505/管理系统+智能问答-trae测试版/frontend/src/components/layout/AppLayout.vue) — 主布局：
```
el-container.app-layout (height: 100vh)
├── el-aside (width: 220px / 64px collapsed)
│   └── <Sidebar />
├── el-container
│   ├── el-header (height: 60px)
│   │   └── <HeaderBar />
│   └── el-main (padding: 16px)
│       └── <router-view />
```

[Sidebar.vue](file:///d:/项目阶段/项目课0505/管理系统+智能问答-trae测试版/frontend/src/components/layout/Sidebar.vue) — 侧边导航：
- Logo 区域（School 图标 + "学生管理系统"）
- el-menu router 模式，12个菜单项
- 权限控制：`v-if="hasPerm('xxx:view')"`
- 折叠支持：`isCollapse` prop

[HeaderBar.vue](file:///d:/项目阶段/项目课0505/管理系统+智能问答-trae测试版/frontend/src/components/layout/HeaderBar.vue) — 顶部栏：
- 折叠按钮（Fold/Expand 图标）
- el-breadcrumb 面包屑（"首页 / 当前页标题"）
- 用户头像 + 用户名 + 角色标签
- 下拉菜单（修改密码 / 退出登录）
- 修改密码弹窗（el-dialog + 表单）

#### 2.1.5 样式系统

[variables.scss](file:///d:/项目阶段/项目课0505/管理系统+智能问答-trae测试版/frontend/src/assets/styles/variables.scss) — 古典色彩系统：

| 变量 | 色值 | 用途 |
|------|------|------|
| `$vermilion` | #C43B3B | 朱红 — 主操作、高亮、强调 |
| `$indigo-dark` | #1B2A4A | 黛蓝深 — 侧边栏背景 |
| `$indigo` | #2C3E6B | 黛蓝 — 头部背景 |
| `$ink-black` | #1A1A1C | 墨黑 — 主文字 |
| `$rice-paper` | #F5E6C8 | 宣纸黄 — 背景 |
| `$rice-paper-light` | #FAF0DC | 浅宣纸 — 页面背景 |
| `$gold` | #C9A96E | 金 — 点缀、强调 |
| `$bamboo` | #5D8A5D | 竹青 — 成功状态 |
| `$mineral-blue` | #4A6B8A | 石青 — 信息状态 |
| `$lotus` | #D4A0A0 | 藕荷 — 次要点缀 |

排版：标题使用楷体 (`KaiTi`, `STKaiti`)，正文使用微软雅黑。

[classical.scss](file:///d:/项目阶段/项目课0505/管理系统+智能问答-trae测试版/frontend/src/assets/styles/classical.scss) — Element Plus 全局覆盖：
- 通过 `:root` CSS 变量覆盖 Element Plus 默认蓝色主题
- 宣纸背景、金色边框、印章按钮、奏折表格
- 自定义滚动条样式（金色）
- 全局基础样式（html/body/卡片/表格/按钮/弹窗）

#### 2.1.6 业务组件

| 文件 | 功能 |
|------|------|
| [SmartQueryInput.vue](file:///d:/项目阶段/项目课0505/管理系统+智能问答-trae测试版/frontend/src/components/SmartQueryInput.vue) | 智能问数输入组件（NL2SQL） |
| [GraphView.vue](file:///d:/项目阶段/项目课0505/管理系统+智能问答-trae测试版/frontend/src/components/GraphView.vue) | 知识图谱可视化（ECharts 力导向图） |
| [VoiceInput.vue](file:///d:/项目阶段/项目课0505/管理系统+智能问答-trae测试版/frontend/src/components/voice/VoiceInput.vue) | 语音输入录音按钮（MediaRecorder API） |
| [VoiceOutput.vue](file:///d:/项目阶段/项目课0505/管理系统+智能问答-trae测试版/frontend/src/components/voice/VoiceOutput.vue) | 语音播放按钮（优先浏览器 TTS，回退后端 TTS） |

#### 2.1.7 API 层

共 14 个 API 文件：`agent.js` / `audio.js` / `auth.js` / `bajie.js` / `class.js` / `course.js` / `dashboard.js` / `employment.js` / `graph.js` / `log.js` / `memory.js` / `score.js` / `student.js` / `user.js`，统一通过 [request.js](file:///d:/项目阶段/项目课0505/管理系统+智能问答-trae测试版/frontend/src/api/request.js) 封装 Axios 实例（baseURL: `/api/v1`，自动注入 JWT token，统一错误处理）。

### 2.2 后端架构

#### 2.2.1 应用入口

[main.py](file:///d:/项目阶段/项目课0505/管理系统+智能问答-trae测试版/backend/main.py) — FastAPI 应用：
- **生命周期管理 (lifespan)**：启动时自动创建 MySQL 表 → 检查 Milvus 连接及数据 → 检查 Neo4j 连接及数据；关闭时释放数据库连接池
- **CORS 中间件**：允许 `localhost:5173` 和 `localhost:3000`
- **全局异常处理**：HTTP 异常 → 参数验证异常 → 通用异常
- **18 个 Controller 路由注册**（见下方详细列表）

#### 2.2.2 路由注册表（18 个模块）

| 路由前缀 | Controller | 标签 | 功能 |
|------|------|------|------|
| `/api/v1/auth` | auth_controller | 认证 | 登录/登出/刷新Token/修改密码 |
| `/api/v1/agent` | agent_controller | 多智能体 | 对话（非流式+SSE流式）+ 意图分类 |
| `/api/v1/students` | student_controller | 学生管理 | CRUD + 导入导出 + 批量操作 |
| `/api/v1/classes` | class_controller | 班级管理 | CRUD |
| `/api/v1/scores` | score_controller | 成绩管理 | CRUD + 成绩统计 |
| `/api/v1/employment` | employment_controller | 就业管理 | CRUD + 就业率统计 |
| `/api/v1/courses` | course_controller | 课程管理 | CRUD |
| `/api/v1/logs` | log_controller | 操作日志 | 日志查询 |
| `/api/v1/dashboard` | dashboard_controller | 仪表盘 | 统计概览 + 4图表数据 |
| `/api/v1/users` | user_controller | 用户管理 | CRUD + 角色权限 |
| `/api/v1/rag` | rag_controller | RAG问答 | 四大名著知识问答 |
| `/api/v1/bajie` | bajie_controller | 八戒功能 | 灯谜/飞花令/社交/情绪 |
| `/api/v1/graph` | graph_controller | 知识图谱 | 人物查询/关系路径/可视化数据 |
| `/api/v1/smart-query` | smart_query_controller | 智能问数 | NL2SQL 自然语言查数据 |
| `/api/v1/memory` | memory_controller | 记忆管理 | 记忆查询/会话管理 |
| `/api/v1/memory` | proactive_controller | 主动对话 | SSE 主动消息推送 |
| `/api/v1/audio` | audio_controller | 语音交互 | 语音识别 + 语音合成 |
| `/api/v1/weather` | weather_controller | 天气查询 | 和风天气 API |
| `/api/v1/fortune` | fortune_controller | 运势占卜 | 运势占卜 |

#### 2.2.3 配置系统

[config.py](file:///d:/项目阶段/项目课0505/管理系统+智能问答-trae测试版/backend/config.py) — Pydantic Settings，从 `.env` 文件读取：
- **数据库**：MySQL 连接（user/password/host/port/name）
- **LLM**：DeepSeek API Key + Base URL + 模型名
- **阿里云**：DashScope API Key + TTS/ASR 模型
- **向量数据库**：Milvus Host/Port
- **图数据库**：Neo4j URI/User/Password
- **认证**：JWT Secret Key / Algorithm / 过期时间
- **其他**：和风天气 API Key / 文件上传配置 / CORS Origins

#### 2.2.4 数据库连接

[database.py](file:///d:/项目阶段/项目课0505/管理系统+智能问答-trae测试版/backend/database.py) — SQLAlchemy：
- 连接池：pool_size=20, max_overflow=40, pool_recycle=3600
- `get_db()` — FastAPI 依赖注入，请求结束时自动关闭会话
- `checkout` 事件 — 每次取出连接前 ping 检查可用性

#### 2.2.5 实体模型（Entity）

共 15 个 ORM 实体：

| 文件 | 表名 | 说明 |
|------|------|------|
| `base.py` | - | 基类 (TimestampMixin + SoftDeleteMixin) |
| `student.py` | student | 学生信息 |
| `class_info.py` | class_info | 班级信息 |
| `score.py` | score | 成绩（student_no + exam_order 唯一约束） |
| `employment.py` | employment | 就业信息 |
| `course.py` | course | 课程信息 |
| `user.py` | user | 用户（含角色权限） |
| `teacher.py` | teacher | 教师信息 |
| `operation_log.py` | operation_log | 操作日志 |
| `conversation_history.py` | conversation_history | 对话历史 |
| `memory_fragment.py` | memory_fragment | 记忆片段（含向量 chunk_id） |
| `user_profile.py` | user_profile | 用户画像 |
| `permission.py` | permission | 权限配置 |
| `document_chunk.py` | document_chunk | 文档分块（RAG 索引） |
| `lantern_riddle.py` | lantern_riddle | 灯谜题库 |
| `qa_pair.py` | qa_pair | 问答对 |

---

## 三、项目文件清单

### 3.1 前端完整文件（frontend/src/）

```
frontend/
├── index.html                         ← HTML入口
├── package.json                       ← 依赖: vue3/element-plus/pinia/echarts
├── vite.config.js                     ← Vite配置 + 代理配置
├── src/
│   ├── main.js                        ← Vue3应用入口
│   ├── App.vue                        ← 根组件（仅<router-view>）
│   ├── router/
│   │   └── index.js                   ← 12个路由 + 全局权限守卫
│   ├── store/
│   │   └── modules/
│   │       └── auth.js                ← Pinia认证Store
│   ├── api/                           ← 14个API模块
│   │   ├── request.js                 ← Axios封装基类
│   │   ├── agent.js                   ← 多智能体对话（SSE流式）
│   │   ├── audio.js                   ← 语音识别/合成
│   │   ├── auth.js                    ← 认证（登录/刷新/修改密码）
│   │   ├── bajie.js                   ← 八戒功能（灯谜/飞花令/社交）
│   │   ├── class.js                   ← 班级管理
│   │   ├── course.js                  ← 课程管理
│   │   ├── dashboard.js               ← 仪表盘数据
│   │   ├── employment.js              ← 就业管理
│   │   ├── graph.js                   ← 知识图谱
│   │   ├── log.js                     ← 操作日志
│   │   ├── memory.js                  ← 记忆管理
│   │   ├── score.js                   ← 成绩管理
│   │   ├── student.js                 ← 学生管理
│   │   └── user.js                    ← 用户管理
│   ├── assets/
│   │   ├── gifs/                      ← （待添加）角色GIF动图
│   │   │   ├── bajie.gif
│   │   │   ├── luzhishen.gif
│   │   │   ├── lindaiyu.gif
│   │   │   └── zhugeliang.gif
│   │   └── styles/
│   │       ├── variables.scss         ← 古典色彩系统+排版+间距+阴影
│   │       ├── classical.scss         ← Element Plus全局覆盖
│   │       └── global.scss            ← body背景色
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppLayout.vue          ← 主布局（侧边栏+顶栏+主内容）
│   │   │   ├── Sidebar.vue            ← 侧边导航（12菜单项）
│   │   │   └── HeaderBar.vue          ← 顶部栏（面包屑+用户）
│   │   ├── voice/
│   │   │   ├── VoiceInput.vue         ← 语音输入（MediaRecorder）
│   │   │   └── VoiceOutput.vue        ← 语音播放（TTS）
│   │   ├── GraphView.vue              ← 知识图谱可视化（ECharts）
│   │   └── SmartQueryInput.vue        ← 智能问数输入
│   └── views/
│       ├── Login.vue                  ← 登录页（预设4种账号）
│       ├── Dashboard.vue              ← 数据看板（5卡片+4图表）
│       ├── student/StudentList.vue    ← 学生管理（CRUD+导入导出）
│       ├── class/ClassList.vue        ← 班级管理
│       ├── score/ScoreList.vue        ← 成绩管理
│       ├── employment/EmploymentList.vue← 就业管理
│       ├── course/CourseList.vue      ← 课程管理
│       ├── logs/OperationLogs.vue     ← 操作日志
│       ├── system/UserManage.vue      ← 用户管理
│       └── bajie/
│           ├── BajieChat.vue          ← 八戒对话（4角色+SSE流式+记忆）
│           ├── KnowledgeQA.vue        ← 知识问答
│           ├── BajieGames.vue         ← 八戒游戏（灯谜+飞花令）
│           └── SocialAssistant.vue    ← 社交助手
```

### 3.2 后端完整文件（backend/）

```
backend/
├── main.py                           ← FastAPI应用入口（生命周期+路由注册）
├── config.py                         ← Pydantic Settings配置
├── database.py                       ← SQLAlchemy连接池+会话
├── dependencies.py                   ← FastAPI依赖注入（get_db/get_current_user）
├── controller/                       ← 18个Controller
│   ├── __init__.py
│   ├── agent_controller.py           ← 多智能体编排接口（非流式+SSE）
│   ├── audio_controller.py           ← 语音识别/合成接口
│   ├── auth_controller.py            ← 认证接口
│   ├── bajie_controller.py           ← 八戒功能接口
│   ├── class_controller.py           ← 班级管理接口
│   ├── course_controller.py          ← 课程管理接口
│   ├── dashboard_controller.py       ← 仪表盘接口
│   ├── employment_controller.py      ← 就业管理接口
│   ├── fortune_controller.py         ← 运势占卜接口
│   ├── graph_controller.py           ← 知识图谱接口
│   ├── log_controller.py             ← 操作日志接口
│   ├── memory_controller.py          ← 记忆管理接口
│   ├── proactive_controller.py       ← 主动对话SSE接口
│   ├── rag_controller.py             ← RAG问答接口
│   ├── score_controller.py           ← 成绩管理接口
│   ├── smart_query_controller.py     ← 智能问数接口
│   ├── student_controller.py         ← 学生管理接口
│   ├── user_controller.py            ← 用户管理接口
│   └── weather_controller.py         ← 天气查询接口
├── service/                          ← 20个Service
│   ├── agent_service.py              ← 多智能体编排（意图分类+消息路由+SSE）
│   ├── auth_service.py               ← 认证服务
│   ├── bajie_service.py              ← 八戒服务
│   ├── bayesian_classifier.py        ← 贝叶斯意图分类器
│   ├── bkt_service.py                ← BKT知识追踪服务
│   ├── class_service.py              ← 班级服务
│   ├── course_service.py             ← 课程服务
│   ├── dashboard_service.py          ← 仪表盘服务
│   ├── employment_service.py         ← 就业服务
│   ├── fortune_service.py            ← 运势服务
│   ├── graph_reasoning.py            ← 图谱深度推理服务
│   ├── graph_service.py              ← 图谱基础服务
│   ├── memory_service.py             ← 记忆存储服务
│   ├── nl2sql_service.py             ← NL2SQL服务
│   ├── proactive_service.py          ← 主动对话服务
│   ├── rag_service.py                ← RAG知识问答服务
│   ├── recommendation_service.py     ← 学习推荐服务
│   ├── score_service.py              ← 成绩服务
│   ├── student_service.py            ← 学生服务
│   └── weather_service.py            ← 天气服务
├── agent/                            ← 12个Agent文件
│   ├── __init__.py
│   ├── base_agent.py                 ← Agent抽象基类
│   ├── orchestrator_agent.py         ← 多智能体编排器（核心）
│   ├── system_prompts.py             ← 4角色人设Prompt
│   ├── data_agent.py                 ← 数据查询Agent
│   ├── knowledge_agent.py            ← 知识问答Agent
│   ├── emotional_agent.py            ← 情绪疏导Agent
│   ├── social_agent.py               ← 社交僚机Agent
│   ├── game_agent.py                 ← 游戏Agent（灯谜+飞花令）
│   ├── persona_agent.py              ← 角色扮演Agent
│   ├── weather_agent.py              ← 天气Agent
│   ├── fortune_agent.py              ← 运势Agent
│   ├── react_agent.py                ← ReAct推理Agent
│   ├── recommendation_agent.py       ← 学习推荐Agent
│   ├── task_decomposer.py            ← 任务分解器
│   ├── agent_message_bus.py          ← Agent间消息总线
│   └── tool_registry.py              ← 工具注册表
├── utils/                            ← 20个工具模块
│   ├── __init__.py
│   ├── asr_util.py                   ← 阿里云语音识别
│   ├── book_router.py                ← 四大名著书籍路由
│   ├── deepseek_util.py              ← DeepSeek API（chat+stream）
│   ├── embedding_util.py             ← 向量嵌入
│   ├── excel_util.py                 ← Excel导入导出
│   ├── fortune_util.py               ← 运势工具
│   ├── jwt_util.py                   ← JWT认证工具
│   ├── llm_router.py                 ← LLM路由（DeepSeek/Qwen切换）
│   ├── logger.py                     ← 日志工具
│   ├── memory_extractor.py           ← 记忆提取器（LLM+去重+向量化+双写）
│   ├── memory_retriever.py           ← 记忆检索器（Milvus语义+MySQL补充）
│   ├── milvus_util.py                ← Milvus向量数据库工具
│   ├── neo4j_util.py                 ← Neo4j图数据库工具
│   ├── password_util.py              ← 密码加密工具
│   ├── qwen_util.py                  ← 阿里云Qwen API
│   ├── response_util.py              ← 统一响应工具
│   ├── text_chunker.py               ← 文本分块工具
│   ├── tts_util.py                   ← 文本转语音工具
│   └── weather_util.py               ← 和风天气API
├── entity/                           ← 15个ORM实体
├── schema/                           ← Pydantic Schema
├── dao/                              ← 数据访问层
├── middleware/                       ← 中间件（异常处理）
├── data/                             ← 数据文件
│   ├── bajie_persona.json
│   └── riddles.json
└── logs/                             ← 日志文件
```

### 3.3 配置文件与脚本

```
根目录/
├── .gitignore
├── requirements.txt                  ← Python依赖
├── README.md
├── 0416-finally_create_db.sql        ← 数据库初始化SQL
├── 《西游记》(1).txt                  ← 四大名著原文
├── 《三国演义》(1).txt
├── 《水浒传》(1).txt
├── 《红楼梦》(1).txt
├── 猪八戒.png / 鲁智深.png           ← 角色图片
├── 诸葛亮.jpg / 林黛玉.png
├── scripts/
│   ├── init_db.py                    ← 初始化数据库表
│   ├── init_milvus.py                ← 初始化Milvus集合
│   ├── init_neo4j.py                 ← 初始化Neo4j图谱
│   ├── ingest_novel.py               ← 导入四大名著文本到Milvus
│   ├── hash_passwords.py             ← 密码哈希
│   └── fix_users_table.sql           ← 用户表修复SQL
├── docs/
│   └── superpowers/
│       ├── plans/                    ← 5个实施计划文档
│       │   ├── 2026-05-27-phase1-cleanup.md
│       │   ├── 2026-05-27-phase2-aliyun-integration.md
│       │   ├── 2026-05-27-phase3-frontend-api.md
│       │   ├── 2026-05-27-phase4-8-advanced.md
│       │   ├── 2026-05-27-phase-new-features.md
│       │   └── 2026-05-27-rag-neo4j-implementation.md
│       └── specs/                    ← 4个设计规范文档
│           ├── 2026-05-27-ai-agent-enhancement-design.md
│           ├── 2026-05-27-rag-neo4j-enhancement-design.md
│           ├── 2026-05-29-memory-framework-design.md
│           └── 2026-05-31-full-system-enhancement-design.md
```

---

## 四、当前已实现功能

### 4.1 管理系统功能（8个）

| 功能模块 | 子功能 | 状态 |
|------|------|:--:|
| **仪表盘** | 5个统计卡片（学生总数/班级数量/教师人数/平均成绩/就业率） | ✅ |
| | 4个ECharts图表（班级分布柱状图/成绩趋势折线图/就业情况/分数段分布） | ✅ |
| **学生管理** | 列表搜索（学号/姓名/班级） + 分页 | ✅ |
| | 新增/编辑/删除（弹窗表单） | ✅ |
| | Excel导入/导出 + 批量删除 | ✅ |
| **班级管理** | CRUD + 分页 | ✅ |
| **成绩管理** | 按学生查询（student_no + exam_order） | ✅ |
| | 新增/编辑/删除 | ✅ |
| **就业管理** | CRUD + 按班级筛选 | ✅ |
| **课程管理** | CRUD | ✅ |
| **操作日志** | 日志查询（操作人/操作类型/时间范围） | ✅ |
| **用户管理** | CRUD + 角色权限（超级管理员/管理员/教师/学生） | ✅ |
| **智能问数** | NL2SQL 自然语言查询业务数据 | ✅ |

### 4.2 AI 功能（6个）

| 功能模块 | 子功能 | 状态 |
|------|------|:--:|
| **八戒对话** | 4角色切换（猪八戒/鲁智深/林黛玉/诸葛亮） | ✅ |
| | 9种意图路由（数据查询/知识问答/闲聊/情绪/社交/灯谜/飞花令/天气/运势） | ✅ |
| | SSE 流式回复 + 打字机效果 | ✅ |
| | 会话管理（左侧会话列表 + 创建/切换/删除） | ✅ |
| | 对话记忆（自动存档到 MySQL + 记忆提取到 Milvus） | ✅ |
| | 主动对话（AI 主动搭话，SSE推送） | ✅ |
| | 语音交互（前端录音/播放按钮，后端 TTS/ASR 接口） | ✅ |
| **知识问答** | RAG 四大名著知识库检索（Milvus 4个集合联合检索） | ✅ |
| | 书籍智能路由 + 图谱融合查询 | ✅ |
| **八戒游戏** | 灯谜（出题/猜谜/提示） | ✅ |
| | 飞花令（对诗） | ✅ |
| **社交助手** | 社交话术/情书生成 | ✅ |
| **知识图谱** | 人物信息查询 + 关系网络 + 路径查找 | ✅ |
| | ECharts 力导向图可视化 | ✅ |

### 4.3 记忆系统功能

| 功能 | 实现文件 | 状态 |
|------|------|:--:|
| 记忆提取 | `memory_extractor.py` — LLM提取→去重→向量化→双写MySQL+Milvus | ✅ |
| 记忆检索 | `memory_retriever.py` — Milvus语义搜索 + MySQL结构补充 + 排序衰减 | ✅ |
| 用户画像 | `user_profile.py` — ORM实体 | ✅ |
| 记忆片段 | `memory_fragment.py` — ORM实体（含chunk_id向量索引） | ✅ |
| 主动对话 | `proactive_service.py` + `proactive_controller.py` — SSE推送 | ✅ |
| 与Agent集成 | `data_agent.py` / `persona_agent.py` 在execute中调用MemoryRetriever | ✅ |

### 4.4 登录与会话管理

| 功能 | 状态 |
|------|:--:|
| 4种角色登录（超级管理员/管理员/教师/学生） | ✅ |
| 预设账号一键填充 | ✅ |
| JWT access_token（120分钟）+ refresh_token（7天） | ✅ |
| 全局路由守卫（未登录重定向） | ✅ |
| 修改密码弹窗 | ✅ |

---

## 五、多智能体架构详解

### 5.1 当前架构（已实现 — 路由表模式）

```
用户消息
  ↓
agent_service.py
  ├── classify_intent_hybrid()  ← 贝叶斯前置 + LLM回退
  │     ├── bayesian_classifier.classify() → 置信度≥0.85 直接用
  │     └── classify_intent() → DeepSeek LLM 分类（9种意图）
  ↓
OrchestratorAgent.execute()
  ├── _execute_function_calling()  ← Function Calling模式（data_query/knowledge_question）
  ├── TaskDecomposer.decompose()   ← 任务分解
  │     ├── 子任务>1 → _execute_parallel()  ← asyncio.gather 并行执行
  │     └── 子任务≤1 → execute_single()     ← 单Agent路由
  ↓
execute_single()  (原有路由表，一行未删)
  ├── data_query       → DataAgent          (BusinessManagementAgent)
  ├── knowledge_question→ KnowledgeAgent     (RAGKnowledgeAgent)
  ├── emotional_support→ EmotionalAgent      (EmotionalCounselingAgent)
  ├── social_help      → SocialAgent        (SocialAssistantAgent)
  ├── weather_query    → WeatherAgent       (WeatherQueryAgent)
  ├── fortune_telling  → FortuneAgent       (FortuneTellingAgent)
  ├── game_riddle      → GameAgent          (GameAgent)
  ├── game_poetry      → GameAgent          (GameAgent)
  ├── chat_greet       → PersonaAgent       (4角色版本)
  ├── deep_reasoning   → ReactAgent         (ReActReasoningAgent)
  └── learning_recommendation → RecommendationAgent (LearningRecommendationAgent)
```

### 5.2 Agent 文件说明

| Agent 文件 | Agent 类 | 工具/服务 | 输入→输出 |
|------|------|------|------|
| `data_agent.py` | DataAgent | NL2SQL + MemoryRetriever | 数据查询问题 → 自然语言回答 + 表格数据 |
| `knowledge_agent.py` | KnowledgeAgent | RAGService | 名著问题 → 基于原文的回答 + 引用出处 |
| `emotional_agent.py` | EmotionalAgent | DeepSeek | 情绪倾诉 → 共情安慰回应 |
| `social_agent.py` | SocialAgent | DeepSeek | 社交需求 → 话术/情书/建议 |
| `game_agent.py` | GameAgent | 灯谜题库 / DeepSeek | 游戏命令 → 灯谜/对诗 |
| `persona_agent.py` | PersonaAgent | MemoryRetriever | 日常闲聊 → 角色风格回应 |
| `weather_agent.py` | WeatherAgent | 和风天气API | 天气查询 → 天气信息 |
| `fortune_agent.py` | FortuneAgent | DeepSeek | 运势请求 → 占卜结果 |
| `react_agent.py` | ReactAgent | ToolRegistry | 复杂问题 → Think→Act→Observe 循环推理 |
| `recommendation_agent.py` | RecommendationAgent | BKT + LLM | 学习请求 → 个性化学习计划 |
| `orchestrator_agent.py` | OrchestratorAgent | 全部Agent + 编排 | 消息 → 调度→合并→返回 |
| `base_agent.py` | BaseAgent(ABC) | tools + tool_registry | Agent基类，定义execute抽象方法 |

### 5.3 Agent 间通信

`agent_message_bus.py` — 消息总线：
- `set(key, value)` — 发布消息到总线
- `get(key)` — 从总线获取消息
- `clear()` — 清空总线

用于多 Agent 共享上下文（Function Calling 结果传递、ReAct 观察结果共享）。

---

## 六、记忆框架详解

### 6.1 四层记忆体系架构

```
┌─────────────────────────────────────────────────────────────┐
│              第四层：主动对话层 (ProactiveAgent)               │
│  触发检测 → 话题选择 → 消息生成 → SSE推送                      │
│  职责: 让AI从"被动应答"变成"主动搭话"                          │
│  实现: proactive_service.py / proactive_controller.py        │
└──────────────────────────┬──────────────────────────────────┘
                           │ 依赖记忆层提供素材
┌──────────────────────────▼──────────────────────────────────┐
│              第三层：记忆检索层 (MemoryRetrieval)              │
│  语义向量搜索 → 重要性排序 → 时间衰减 → 构建记忆提示词           │
│  职责: 从海量记忆中捞出当前对话最相关的片段                      │
│  实现: memory_retriever.py (Milvus + MySQL)                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              第二层：记忆提取层 (MemoryExtraction)             │
│  LLM提取 → 分类(fact/preference/event/emotion) → 重要性打分    │
│  → 向量化 → 双写存储 → 更新用户画像                            │
│  职责: 从原始对话中提炼结构化记忆                                │
│  实现: memory_extractor.py (fire-and-forget异步)              │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              第一层：存储层 (Storage)                          │
│  MySQL: conversation_history + memory_fragment + user_profile │
│  Milvus: memory_vectors (向量索引)                            │
│  职责: 双写存储，保证结构化查询+语义检索                          │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 记忆提取流程

1. **触发**：对话流结束后，`agent_controller.py` 中异步调用 `MemoryExtractor.extract_memories()`
2. **LLM 提取**：将对话发给 DeepSeek，提取关键事实/偏好/事件/情绪
3. **去重**：Jaccard 相似度 > 0.3 的视为重复记忆，不重复存储
4. **向量化**：DeepSeek embedding → 1536 维向量
5. **双写**：MySQL memory_fragment 表 + Milvus memory_vectors 集合

### 6.3 记忆检索流程

1. **Milvus 语义搜索**：用户消息向量化 → Milvus 搜 Top-K 相似记忆
2. **MySQL 补充检索**：按用户 ID + memory_type + importance 补充
3. **合并结果**：去重 + 按 importance 排序 + 时间衰减
4. **构建记忆提示词**：Top 5 条记忆 → 注入到 Agent 的 System Prompt 中

---

## 七、8 项核心能力诊断

> 此章节记录了用户提出的 8 个技术问题的诊断结论

### 7.1 多智能体协同 — 🟡 部分实现

**问题：** 我现在的多智能体协同已经创建好了是吗？

**诊断结论：** 文件已创建完毕，进行了部分升级，但涉及前端的功能（如协同管理面板、Agent 可视化看板等）尚未添加。

| 已有文件 | 涵盖能力 | 状态 |
|------|------|:--:|
| `orchestrator_agent.py` | 运行入口 + 任务分解 + 并行执行 + 结果合并 + 路由表 | ✅ |
| `task_decomposer.py` | 任务分解器 | ✅ |
| `agent_message_bus.py` | Agent 间消息总线 | ✅ |
| `tool_registry.py` | 工具注册表 + 执行引擎 | ✅ |

**缺失能力：**
- ❌ 无协同管理面板（前端）
- ❌ 无 Agent 状态监控看板（前端）
- ❌ 无任务日志与历史查看界面（前端）
- ⚠️ `result_merger.py` 逻辑已迁移至 `orchestrator_agent.py` 内部的 `_merge_results()` 方法

### 7.2 记忆框架 — 🟢 已完整实现

**问题：** 记忆框架是否还存在？且还能执行？

**诊断结论：** 四层记忆体系完整存在：
- ✅ `memory_extractor.py` — LLM 提取 + 去重 + 向量化 + 双写
- ✅ `memory_retriever.py` — Milvus 语义搜索 + MySQL 补充
- ✅ `memory_fragment.py` — 记忆片段 ORM
- ✅ `user_profile.py` — 用户画像 ORM
- ✅ `proactive_service.py` — 主动对话引擎
- ✅ `proactive_controller.py` — SSE 主动消息推送
- ✅ 已集成到 `data_agent.py` 和 `persona_agent.py` 的 execute 方法中
- ⚠️ 依赖 MySQL 和 Milvus 正常运行

### 7.3 自主调用数据库/RAG/图谱 — 🔴 已实现 Function Calling 基础，不可自主决策

**问题：** 我的智能体是否能自主调用数据库和 RAG 和图谱？

**诊断结论：** 已实现基础的 Function Calling 机制（`tool_registry.py` + orchestrator 中的 `_execute_function_calling()`），但智能体仍不具备完全自主决策能力。

**已有基础：**
- ✅ `tool_registry.py` — 工具注册表（注册了 `query_student_data`、`search_novel_knowledge` 等多种工具）
- ✅ `base_agent.py` — Agent 基类中已定义 `self.tools` 和 `self.tool_registry` 属性
- ✅ `orchestrator_agent.py` — `_execute_function_calling()` 实现了基础 Function Calling 循环
- ✅ Agent 间的 `agent_message_bus.py` — 消息总线用于传递上下文

**缺失能力：**
- ❌ 智能体自身不可自主决定是否调用工具 —— 当前由编排器集中决策
- ❌ 没有 graph_query 工具注册到 ToolRegistry（图谱只能通过独立 API 访问）
- ❌ 工具调用日志不完整（缺少调用了哪个工具、返回了什么结果、耗时多少的统计）

### 7.4 ReAct 推理循环 — 🟡 文件已创建，未在实际业务中验证

**问题：** 是否还能实现 ReAct 推理循环：Think→Act→Observe→Think 循环推理？

**诊断结论：** `react_agent.py` 已创建，但在实际业务流程（agent_service.py / agent_controller.py 对话流）中尚未进行全面的端到端测试验证，稳定性未知。

**已有基础：**
- ✅ `agent/react_agent.py` 文件已存在
- ✅ `orchestrator_agent.py` 中已挂载 `self.react_agent`（含 try/except 兜底）
- ✅ 路由表新增 `"deep_reasoning": (self.react_agent, "ReActReasoningAgent")`

**缺失能力：**
- ❌ 没有 `deep_reasoning` 意图的识别逻辑（`classify_intent` 没有对应的意图分类提示词）
- ❌ 没有触发入口（用户无法通过正常对话触发 ReAct 推理）

### 7.5 贝叶斯意图分类 — 🟡 文件已创建，与 LLM 分类并存

**问题：** 是否还能实现贝叶斯意图分类？实现这个会不会因为已有大模型进行意图识别而影响？

**诊断结论：** `bayesian_classifier.py` 已创建，采用"贝叶斯前置 + LLM 兜底"方案。不会影响已有 LLM 意图识别，二者完全兼容。

**已有基础：**
- ✅ `bayesian_classifier.py` 文件已存在（MultinomialNB + TF-IDF）
- ✅ `agent_service.py` 中的 `classify_intent_hybrid()` 函数已实现混合分类逻辑
- ✅ 逻辑：贝叶斯置信度 ≥ 0.85 直接用 → < 0.85 回退 LLM
- ✅ 自我学习机制：LLM 结果加入训练缓冲区 `add_training_sample()`

**缺失能力：**
- ❌ 预训练数据不足（scikit-learn 朴素贝叶斯需要足够样本才能有效分类）
- ❌ 缺少模型持久化和加载机制（每次重启需要重新训练）

### 7.6 知识图谱深度推理 — 🟡 逻辑模块已创建，Neo4j 数据待扩展

**问题：** 是否还能实现知识图谱深度推理（事件因果推理、人物阵营分析、剧情时间线）？

**诊断结论：** `graph_reasoning.py` 已创建，实现了推理函数逻辑框架，但 Neo4j 数据模型尚未扩展。

**已有基础：**
- ✅ `graph_reasoning.py` 文件已存在
- ✅ `graph_service.py` 基础查询已就绪（get_person / get_relations / find_path）
- ✅ Neo4j 连接已就绪

**缺失能力：**
- ❌ Neo4j 中只有 Person 节点，没有 Event 节点
- ❌ Neo4j 中 Person 节点没有 faction 属性（阵营分类）
- ❌ Neo4j 中 Person 节点没有 chapter 属性（章回索引）
- ❌ 没有 CAUSES 关系边（事件因果链）
- ❌ `graph_reasoning.py` 中编写的是推理逻辑框架和查询模板，实际线数据需手动导入

### 7.7 个性化学习推荐 — 🟡 文件已创建，无真实用户数据验证

**问题：** 能否实现个性化学习推荐（BKT + 薄弱点诊断 + 学习计划生成）？

**诊断结论：** 三个文件已创建完毕，但在真实学生数据上尚未进行验证。

**已有基础：**
- ✅ `bkt_service.py` 文件已存在
- ✅ `recommendation_service.py` 文件已存在
- ✅ `recommendation_agent.py` 文件已存在
- ✅ `orchestrator_agent.py` 中已挂载 `self.recommendation_agent`
- ✅ `score.py` 实体有 `student_no`、`exam_order`、`score` 字段，可做成绩分析

**缺失能力：**
- ❌ 没有 `learning_recommendation` 意图（无法通过对话触发）
- ❌ 缺少知识点体系定义（知识点的映射关系）
- ❌ 没有用户画像联动（BKT 结果不写入 user_profile）

### 7.8 多模态交互 — 🟢 已实现前后端，待集成到聊天流程

**问题：** 告诉我现在项目是否实现多模态交互？是否做到能听能说？

**诊断结论：** 多模态交互已实现，能做到"能听能说"。

**已有能力：**
- ✅ `tts_util.py` → `text_to_speech()` → 阿里云语音合成
- ✅ `asr_util.py` → `speech_to_text()` → 阿里云语音识别
- ✅ `audio_controller.py` → `POST /api/v1/audio/recognize`（语音识别接口）
- ✅ `audio_controller.py` → `POST /api/v1/audio/synthesize`（语音合成接口）
- ✅ [VoiceInput.vue](file:///d:/项目阶段/项目课0505/管理系统+智能问答-trae测试版/frontend/src/components/voice/VoiceInput.vue) — 前端录音按钮（MediaRecorder API）
- ✅ [VoiceOutput.vue](file:///d:/项目阶段/项目课0505/管理系统+智能问答-trae测试版/frontend/src/components/voice/VoiceOutput.vue) — 前端播放按钮（优先浏览器TTS，回退后端TTS）
- ✅ 已集成到 BajieChat.vue 聊天流程中（每行回复下方有语音播放按钮）

**缺失能力：**
- ❌ BajieChat.vue 中语音输入按钮未在聊天流程中直接使用（需手动触发）

---

## 八、7 大功能增强方案

> 此章节记录了用户提出的 7 大功能增强需求及其实现方案

### 8.1 架构影响分析总结

**核心结论：全部实现不会改乱项目。**

| 功能 | 改动文件 | 新增文件 | 破坏性 | 原因 |
|------|:--:|:--:|:--:|------|
| ① 多智能体协同 | `orchestrator_agent.py` | `task_decomposer.py` / `agent_message_bus.py` | 🟡 中 | 重写核心编排逻辑，但旧路由表完整保留 |
| ② Function Calling | `base_agent.py` (+2属性) / `orchestrator_agent.py` (+方法) | `tool_registry.py` | 🟡 中 | 基类加属性，编排器加分支，不影响旧逻辑 |
| ③ ReAct 循环 | `classify_intent` (+意图) / `orchestrator_agent` (+路由) | `react_agent.py` | 🟢 低 | 纯增量，新增路由条目 |
| ④ 贝叶斯分类 | `agent_service.py` (+函数引用) | `bayesian_classifier.py` | 🟢 极低 | 4 行改动，if/else 分支切换 |
| ⑤ 图谱深度推理 | `graph_service.py` (+方法调用) | `graph_reasoning.py` | 🟢 低 | 追加方法，不删旧代码 |
| ⑥ BKT 学习推荐 | `classify_intent` (+意图) / `orchestrator_agent` (+路由) | `bkt_service.py` / `recommendation_service.py` / `recommendation_agent.py` | 🟢 低 | 纯增量 |
| ⑦ 多模态交互 | 无 (已实现) | 无 (已实现) | 🟢 零 | 功能已就绪 |

### 8.2 功能 ①：多智能体协同全面升级

**目标：** 补齐协同管理面板、Agent 状态监控看板、任务日志等前端能力

**实现要点：**
- 前端新增协同管理看板页面（Agent 状态可视化、任务实时监控）
- 后端为编排器补充 WebSocket 状态广播接口（向管理面板推送 Agent 执行状态）
- Agent 间消息总线补充消息持久化日志

### 8.3 功能 ②：Agent 自主工具调用级联

**目标：** 让智能体自主决策是否调用工具以及调用哪个工具，而非由编排器集中决策

**实现要点：**
- 将 graph_query 工具注册到 ToolRegistry
- 为每个 Agent 的 execute() 添加独立的 Function Calling 决策分支
- 补充工具调用日志统计（调用了哪个工具、返回了什么结果、耗时多少）

### 8.4 功能 ③：ReAct 推理循环端到端打通

**目标：** 完成 ReactAgent 的实际业务流程验证与集成

**实现要点：**
- 在 `classify_intent` 中增加 `deep_reasoning` 意图识别逻辑
- 在 BajieChat 中增加 ReAct 推理触发入口（如"分析一下"、"帮我推理"）
- 验证 Think→Act→Observe→Think 循环在真实对话场景中的稳定性

### 8.5 功能 ④：贝叶斯意图分类完善

**目标：** 完善贝叶斯分类器的预训练和模型持久化

**实现要点：**
- 准备预训练数据（约 500 条标注语料，覆盖 9 种意图）
- 添加模型持久化和加载机制（pickle/joblib 保存和加载）
- 启动时自动加载预训练模型

### 8.6 功能 ⑤：知识图谱深度推理上线

**目标：** Neo4j 数据模型扩展 + 因果推理/阵营分析/时间线上线

**实现要点：**
- Neo4j 新建 Event 节点（事件名称/章回/书籍/事件描述）
- Neo4j 新建 CAUSES 关系边（事件因果链）
- Person 节点添加 faction 属性（阵营：蜀/魏/吴/佛/道等）
- Person 节点添加 chapter 属性（首次出场章回）
- `graph_reasoning.py` 中的推理逻辑与 Neo4j 真实数据对接

### 8.7 功能 ⑥：个性化学习推荐上线

**目标：** BKT + 薄弱点诊断 + 学习计划生成端到端上线

**实现要点：**
- 定义知识点体系（如三角函数/概率论/几何/代数等）
- BKT 算法基于真实学生成绩数据计算掌握概率
- 在 `classify_intent` 中增加 `learning_recommendation` 意图
- BKT 结果联动 `user_profile` 写入

### 8.8 功能 ⑦：多模态交互强化（已基本就绪）

当前语音交互已实现，如需强化可考虑：
- 在 BajieChat 输入区增加语音输入按钮（已存在但未突出）
- 增加连续对话模式（语音输入 → 自动回复 → TTS 播放）
- 增加音色选择（不同角色使用不同 TTS 音色）

---

## 九、前端布局升级方案

### 9.1 升级目标

提升用户体验和视觉品质，保持古典四大名著主题氛围不变。

### 9.2 升级清单

| 升级项 | 优先级 | 描述 |
|------|:--:|------|
| TabBar 标签页栏 | ⭐⭐⭐ | 记录打开的页面，点击切换，右键关闭 |
| 页面过渡动画 | ⭐⭐⭐ | fade-slide 淡入滑动效果（250ms） |
| Sidebar Logo 增强 | ⭐⭐ | 增大图标 + "猪八戒智能平台"副标题 |
| Sidebar 菜单 hover 动效 | ⭐⭐ | hover 时金色竖条 + 背景渐变过渡 |
| Sidebar 底部用户区 | ⭐⭐ | 显示当前用户头像 + 用户名 |
| Sidebar 折叠 tooltip | ⭐ | 折叠时 hover 图标弹出菜单名称 |
| HeaderBar 完整面包屑 | ⭐⭐ | 从"首页/当前页"升级为完整路径 |
| HeaderBar 全屏按钮 | ⭐ | 右侧加全屏图标按钮 |
| HeaderBar 通知铃铛 | ⭐ | 预留通知图标按钮（badge 显示 0） |
| HeaderBar 用户下拉增强 | ⭐ | 增加"个人设置"选项（预留） |
| HeaderBar 视觉升级 | ⭐⭐ | 渐变背景 + 细金色底边 |
| 卡片 hover 微交互 | ⭐ | 上浮 2px + 阴影加深 |
| 按钮 hover 放大 | ⭐ | 1.02 倍 + 过渡动画 |
| 表格行 hover | ⭐ | 藕荷色系背景 |
| 输入框 focus 动效 | ⭐ | 边框颜色过渡动画 |

### 9.3 改动范围

**仅改 3 个文件 + 1 个追加：**

| 文件 | 改动类型 | 说明 |
|------|------|------|
| `AppLayout.vue` | 重写 | 新增 TabBar + fade-slide 过渡 + 动图层 |
| `Sidebar.vue` | 增强 | Logo 升级 + hover 动效 + 底部用户信息 |
| `HeaderBar.vue` | 增强 | 完整面包屑 + 全屏按钮 + 通知铃铛 |
| `classical.scss` | 末尾追加 | 全局微交互样式 |

**绝对不碰（30+ 文件）：**
- ❌ `router/index.js` — 路由 path/name/meta 不变
- ❌ `store/modules/auth.js` — 认证逻辑不变
- ❌ `main.js` / `App.vue` — 入口不变
- ❌ `api/` 目录全部 14 个文件
- ❌ `views/` 目录全部 14 个业务页面
- ❌ `SmartQueryInput.vue` / `GraphView.vue`
- ❌ `VoiceInput.vue` / `VoiceOutput.vue`
- ❌ `variables.scss` — 变量值不变
- ❌ `classical.scss` — 现有覆盖不删除

---

## 十、角色动图过渡动画方案

### 10.1 需求描述

在页面切换的 fade-slide 过渡动画中，屏幕中央显示当前选中角色的 GIF 动图，让"猪八戒智能平台"更生动有趣。

### 10.2 四角色与动图对应

| 角色 | Key | 推荐动图主题 | 文件名 | 来源 |
|------|------|------|------|------|
| 猪八戒 | bajie | 猪八戒吃西瓜 / 背媳妇 | `bajie.gif` | 86版西游记 |
| 鲁智深 | luzhishen | 倒拔垂杨柳 / 喝酒 | `luzhishen.gif` | 98版水浒传 |
| 林黛玉 | lindaiyu | 葬花 / 抚琴 | `lindaiyu.gif` | 87版红楼梦 |
| 诸葛亮 | zhugeliang | 摇扇 / 抚琴 | `zhugeliang.gif` | 94版三国演义 |

### 10.3 GIF 规格建议

| 参数 | 推荐值 |
|------|------|
| 尺寸 | 200×200 至 300×300 像素（正方形） |
| 时长 | 2-4 秒循环 |
| 大小 | ≤ 500KB |
| 背景 | 透明或宣纸黄色系 |

### 10.4 技术方案

**新建文件：**
| 文件 | 说明 |
|------|------|
| `store/modules/character.js` | Pinia 全局角色 Store（activeCharacter / currentGif / currentName） |

**修改文件：**

| 文件 | 改动 | 说明 |
|------|------|------|
| `BajieChat.vue` | +2 处 | 导入 characterStore + 切换角色时同步全局 Store |
| `AppLayout.vue` | 重写 `<router-view>` 区域 | 新增 `<teleport to="body">` 动图层 |

**视觉效果：**
- 页面切换 → 半透明宣纸色遮罩（毛玻璃效果）
- 角色 GIF 弹跳放大出现（scale 0.5 → 1.15 → 1.0，250ms）
- GIF 带金色边框 + 阴影 + 角色名称（楷体朱红）
- 250ms 后自动消失，`pointer-events: none` 不阻挡点击

### 10.5 GIF 文件获取

用户需自行下载 GIF 文件到 `frontend/src/assets/gifs/` 目录：
- 百度图片搜索："猪八戒吃西瓜 gif"、"林黛玉 葬花 gif" 等
- 花瓣网/Pinterest：搜索"西游记 表情包"
- 自制：截取电视剧片段用 ezgif.com 转 GIF

---

## 十一、完整实施路线图

```
阶段一：前端布局升级（3-4天）
├── Day 1: classical.scss 末尾追加全局微交互样式
├── Day 2: AppLayout.vue 重写（TabBar + fade-slide 过渡）
├── Day 3: Sidebar.vue + HeaderBar.vue 增强
└── Day 4: 角色动图过渡动画 + 全局角色 Store

阶段二：后端 AI 增强验证（7天）
├── Day 5: 贝叶斯分类完善（预训练数据 + 模型持久化）
├── Day 6: ReAct 推理循环端到端打通（意图识别 + 业务验证）
├── Day 7-8: 多智能体协同前端管理面板（状态监控 + 任务日志）
├── Day 9: Function Calling 增强（graph_query 工具 + 工具调用日志）
├── Day 10: 知识图谱深度推理上线（Neo4j 数据扩展 + 推理对接）
├── Day 11: BKT 学习推荐上线（知识点体系 + 真实数据验证）
└── Day 12: 多模态交互强化（连续对话模式 + 音色选择）

阶段三：联调测试（2天）
├── Day 13: 前后端联调 + 功能验证
└── Day 14: 修复 Bug + 文档更新
```

---

## 十二、Claude 提示词汇总

本方案已为所有功能生成了可直接复制给 Claude 的提示词：

| 序号 | 功能 | 改动文件数 | 适用场景 |
|:--:|------|:--:|------|
| 1 | 前端布局升级（TabBar + 过渡动画 + Sidebar/HeaderBar 增强） | 3 + 1 | 前端 UI 改造 |
| 2 | 角色动图过渡动画（全局角色 Store + AppLayout 动图层） | 2 + 1 | 趣味交互增强 |
| 3 | 贝叶斯意图分类完善（预训练 + 模型持久化） | 1 + 1 | 意图分类优化 |
| 4 | ReAct 推理循环端到端打通 | 2 + 1 | 深度推理能力 |
| 5 | 多智能体协同前端管理面板 | 3 + 1 | 协同可视化 |
| 6 | Function Calling 增强（graph 工具 + 调用日志） | 2 + 1 | Agent 自主决策 |
| 7 | 知识图谱深度推理上线（Neo4j 数据扩展） | 2 + 1 | 图谱推理能力 |
| 8 | BKT 学习推荐上线（知识点体系 + 真实数据验证） | 2 + 2 | 个性化推荐 |
| 9 | 多模态交互强化（连续对话 + 音色） | 2 + 1 | 语音交互增强 |

---

## 十三、风险与注意事项

### 13.1 高风险区域

| 风险 | 影响 | 缓解措施 |
|------|------|------|
| orchestrator_agent.py 改动过大 | 所有 Agent 路由失效 | 已保留 execute_single() 方法，新旧并存 |
| Neo4j 数据模型扩展 | 图谱查询错误 | 新查询独立方法，旧查询不变 |
| 前端 TabBar 与路由守卫冲突 | 页面跳转异常 | 不修改路由配置，TabBar 仅监听 route 变化 |
| 贝叶斯分类器未训练 | 所有意图回退 LLM | 预先准备 500 条标注语料 |
| ReAct 循环卡死 | 对话无限循环 | 最大 5 轮限制 + 超时保护 |

### 13.2 外部依赖

| 依赖 | 功能 | 状态 |
|------|------|:--:|
| MySQL | 业务数据 + 记忆存储 | ✅ 已有 |
| Milvus | 向量检索 | ✅ 已有 |
| Neo4j | 人物关系图谱 | ✅ 已有 |
| DeepSeek API | LLM 调用 | ✅ 已有 |
| 阿里云 DashScope | TTS/ASR | ✅ 已有 |
| scikit-learn | 贝叶斯分类器 | ⚠️ 需安装 |
| GIF 动图文件 | 角色过渡动画 | ⚠️ 需手动下载 |
| 标注语料 | 贝叶斯预训练 | ⚠️ 需手动准备 |

### 13.3 实施铁律

1. **只加不删**：旧代码永远保留，新功能通过 if