# AI智能体全面升级设计文档

> **项目**: 学生管理系统 + 猪八戒多智能体AI问答
> **日期**: 2026-05-27
> **目标**: 实现所有深入方向，清理冗余代码，接入阿里云API，达到生产级状态

---

## 一、项目现状分析

### 1.1 当前架构
```
Frontend (Vue3 + Element Plus)
  ├── 学生/班级/成绩/就业/课程管理 (完整)
  ├── 仪表盘 (完整)
  ├── 八戒对话 (前端假数据，TODO)
  ├── 知识问答 (已接RAG，非流式)
  ├── 八戒游戏 (前端假数据，TODO)
  └── 社交僚机 (前端假数据，TODO)

Backend (FastAPI + SQLAlchemy + MySQL)
  ├── 管理模块CRUD (完整)
  ├── NL2SQL数据查询 (完整)
  ├── RAG四大名著问答 (完整)
  ├── 多智能体编排 (完整，后端就绪)
  ├── 八戒服务 (完整，后端就绪)
  └── DeepSeek API调用 (完整)

AI基础设施
  ├── DeepSeek API (chat + embedding)
  ├── Milvus向量库 (4个名著集合)
  └── BGE-small本地嵌入模型 (512维)
```

### 1.2 关键问题清单
| 编号 | 问题 | 影响 | 解决Phase |
|------|------|------|-----------|
| P0-1 | 前端所有AI页面使用假数据 | 功能不可用 | Phase 3 |
| P0-2 | `base_dao.py` 完全为空 | DAO无基类抽象 | Phase 1 |
| P0-3 | 多处`print()`未使用logging | 无法生产级日志 | Phase 1 |
| P0-4 | `BajieChat.vue` 未接SSE流式 | 聊天体验差 | Phase 3 |
| P1-1 | 对话历史未传递 | 单轮对话 | Phase 4 |
| P1-2 | 无阿里云API接入 | 无法使用语音等能力 | Phase 2 |
| P1-3 | 无Function Calling | 意图路由硬编码 | Phase 5 |
| P2-1 | 无语音交互 | 纯文本 | Phase 6 |
| P2-2 | 无长期记忆 | 每次重启遗忘 | Phase 7 |
| P2-3 | RAG无Rerank | 检索精度有限 | Phase 8 |

---

## 二、总体架构设计

### 2.1 双模型策略
```
┌─────────────────────────────────────────────────────────────┐
│                      AI模型路由层                            │
├─────────────────────────────────────────────────────────────┤
│  DeepSeek API (保留)          │  阿里云通义千问 (新增)        │
│  ├── 文本生成 (chat)          │  ├── 文本生成 (qwen-turbo)   │
│  ├── 流式生成 (stream)        │  ├── 流式生成 (stream)       │
│  └── Function Calling         │  ├── 语音合成 (TTS)          │
│                               │  ├── 语音识别 (ASR)          │
│                               │  └── 嵌入向量 (text-embedding)│
└─────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────────────┐
                    │   统一LLM客户端   │
                    │  (自动选择模型)   │
                    └─────────────────┘
```

**模型选择策略**:
- 创意生成/角色扮演 → DeepSeek (温度高，表现好)
- 语音合成/识别 → 阿里云 (专属能力)
- 嵌入向量 → 阿里云 (text-embedding-v3，768维)
- NL2SQL/RAG → 双模型容错 (主DeepSeek，备阿里云)
- Function Calling → 双模型支持

### 2.2 增强后的多智能体架构
```
用户消息 → 统一入口
    ↓
┌─────────────────────────────────────────────────────────────┐
│  意图分类 (IntentClassifier)                                │
│  支持: 规则分类 + 模型分类 + 置信度阈值                      │
└─────────────────────────────────────────────────────────────┘
    ↓
路由决策 (支持Function Calling覆盖)
    ↓
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ 数据查询Agent│ 知识问答Agent│ 角色扮演Agent│ 工具调用Agent│
│ (NL2SQL)    │ (RAG+优化)  │ (八戒人格)  │ (Function)  │
├─────────────┼─────────────┼─────────────┼─────────────┤
│ • 多轮查询  │ • 混合检索  │ • 语音交互  │ • 查天气    │
│ • 上下文SQL │ • Rerank   │ • 情绪识别  │ • 设提醒    │
│ • 结果缓存  │ • 引用高亮  │ • 长期记忆  │ • 查数据    │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

### 2.3 日志与监控架构
```
┌────────────────────────────────────────┐
│           统一日志系统                  │
├────────────────────────────────────────┤
│  应用日志 → backend/logs/app.log       │
│  错误日志 → backend/logs/error.log     │
│  AI调用日志 → backend/logs/ai.log      │
│  访问日志 → backend/logs/access.log    │
└────────────────────────────────────────┘
```

---

## 三、Phase划分与依赖关系

```
Phase 1: 基础清理 (无依赖)
    ├── 删除/重构空文件
    ├── print() → logging
    ├── 配置修正
    └── 代码规范统一

Phase 2: 阿里云API接入 (依赖Phase 1)
    ├── 封装阿里云LLM客户端
    ├── 封装阿里云语音客户端(TTS/ASR)
    ├── 双模型路由策略
    └── 配置扩展

Phase 3: 前端API对接 (依赖Phase 2)
    ├── BajieChat.vue 接SSE流式
    ├── BajieGames.vue 接后端API
    ├── SocialAssistant.vue 接后端API
    └── KnowledgeQA.vue 接流式

Phase 4: 对话历史与上下文 (依赖Phase 3)
    ├── 前端维护history状态
    ├── 后端所有Agent使用history
    ├── 多轮NL2SQL
    └── 多轮RAG

Phase 5: Function Calling (依赖Phase 4)
    ├── 工具定义Schema
    ├── 工具执行引擎
    ├── Agent集成Function Calling
    └── 前端展示工具调用过程

Phase 6: 语音集成 (依赖Phase 2, 3)
    ├── 后端TTS服务
    ├── 前端语音播放
    ├── 前端ASR录音
    └── 八戒语音交互

Phase 7: 长期记忆 (依赖Phase 4)
    ├── conversation_history表启用
    ├── 用户画像构建
    ├── 记忆检索与注入
    └── 个性化回复

Phase 8: RAG优化 (依赖Phase 2)
    ├── 混合检索(BM25+向量)
    ├── Rerank精排
    ├── 引用高亮
    └── 答案摘要
```

---

## 四、各Phase详细设计

### Phase 1: 基础清理与代码优化

**目标**: 消除技术债务，建立统一的日志和配置基础

**任务清单**:
1. `base_dao.py` 实现泛型基类，StudentDAO/UserDAO继承
2. 全局扫描替换 `print()` → `logging`
3. 修正 `embedding_util.py` 注释（512维而非1536维）
4. 删除/标记未使用的 `MILVUS_COLLECTION_NAME` 配置
5. 统一后端日志配置（按天轮转、分级）
6. 创建 `backend/logs/` 目录结构

**文件变更**:
- 修改: `backend/dao/base_dao.py` (新建实现)
- 修改: `backend/dao/student_dao.py`, `user_dao.py` (继承基类)
- 修改: `backend/utils/*.py` (替换print)
- 修改: `backend/config.py` (日志配置)
- 修改: `backend/main.py` (日志初始化)
- 新建: `backend/utils/logger.py` (统一日志)

### Phase 2: 阿里云API接入

**目标**: 建立双模型能力，接入阿里云语音服务

**阿里云API配置**:
- Base URL: `https://dashscope.aliyuncs.com/api/v1`
- API Key: `sk-390ad1d2d9254ae1ab416df1da7f55ae`
- 可用模型:
  - `qwen-turbo` / `qwen-plus` / `qwen-max` (文本生成)
  - `qwen-audio-asr` (语音识别)
  - `sambert-zhichu` (语音合成)
  - `text-embedding-v3` (向量嵌入，768维)

**文件变更**:
- 新建: `backend/utils/qwen_util.py` (阿里云LLM封装)
- 新建: `backend/utils/tts_util.py` (语音合成)
- 新建: `backend/utils/asr_util.py` (语音识别)
- 修改: `backend/config.py` (阿里云配置)
- 修改: `backend/utils/deepseek_util.py` (统一接口)
- 新建: `backend/utils/llm_router.py` (模型路由)

**统一LLM接口设计**:
```python
# backend/utils/llm_router.py
async def chat_completion(
    messages, 
    system_prompt=None, 
    provider="auto",  # "deepseek", "aliyun", "auto"
    temperature=0.7,
    max_tokens=1024,
) -> str:
    """统一LLM调用，支持自动选择模型"""

async def chat_completion_stream(...) -> AsyncGenerator[str, None]:
    """统一流式调用"""
```

### Phase 3: 前端API对接

**目标**: 消除所有假数据和TODO，前端真实调用后端

**BajieChat.vue改造**:
- `sendMessage()` 调用 `/api/v1/agent/chat/stream` SSE接口
- 维护 `messages` 历史数组，发送时带上最近6轮
- 语音按钮接入Web Speech API (浏览器原生)

**BajieGames.vue改造**:
- 灯谜调用 `GET /api/v1/bajie/riddle`
- 诗词调用 `GET /api/v1/bajie/poetry` + `POST /api/v1/bajie/poetry/check`
- 积分同步到后端

**SocialAssistant.vue改造**:
- 话术生成调用 `POST /api/v1/bajie/chat-lines`
- 情书代写调用 `POST /api/v1/bajie/love-letter`

**KnowledgeQA.vue改造**:
- 增加流式问答选项，调用 `/api/v1/rag/qa/stream`

### Phase 4: 对话历史与上下文记忆

**目标**: 所有Agent支持多轮对话

**前端改造**:
- 维护全局 `conversationHistory` (最多20轮)
- 每次发送带上 `history` 字段

**后端改造**:
- `AgentService.process_message()` 接收history并传递给所有子Agent
- `RAGService` 使用history做追问理解
- `nl2sql_service` 使用history做上下文SQL (如"那班级平均成绩呢？")
- `BajieService.bajie_chat()` 使用history保持角色一致性

### Phase 5: Function Calling工具调用

**目标**: 让Agent能自主调用工具

**工具定义**:
```python
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": "查询学生管理系统的数据库",
            "parameters": {...}
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "search_novel",
            "description": "搜索四大名著相关内容",
            "parameters": {...}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前时间",
            "parameters": {}
        }
    }
]
```

**执行流程**:
1. 用户发送消息
2. LLM判断是否需要调用工具
3. 如需调用，返回tool_calls
4. 系统执行工具，获取结果
5. 将结果返回给LLM生成最终回复

### Phase 6: 阿里云语音集成

**目标**: 八戒能说话、能听话

**后端TTS**:
- 新建 `/api/v1/tts` 接口
- 接收文本，调用阿里云Sambert，返回音频URL或Base64

**前端语音**:
- BajieChat增加语音播报开关
- 收到回复后自动调用TTS播放
- 支持用户语音输入 (Web Speech API + 阿里云ASR备用)

### Phase 7: 长期记忆系统

**目标**: 记住用户，个性化交互

**数据库表** (已有 `conversation_history`，需扩展):
```sql
-- 用户画像表
CREATE TABLE user_profile (
    id INT PRIMARY KEY,
    user_id INT,
    preferred_topics VARCHAR(500),  -- 偏好话题
    personality_tags VARCHAR(500),  -- 性格标签
    interaction_count INT,          -- 交互次数
    last_emotion VARCHAR(50),       -- 上次情绪
    created_at TIMESTAMP
);

-- 记忆片段表
CREATE TABLE memory_fragments (
    id INT PRIMARY KEY,
    user_id INT,
    content TEXT,                   -- 记忆内容
    importance FLOAT,               -- 重要性(0-1)
    memory_type VARCHAR(50),        -- 类型: fact, preference, event
    created_at TIMESTAMP
);
```

**记忆流程**:
1. 每次对话后，提取关键信息
2. 存入memory_fragments
3. 下次对话前，检索相关记忆注入prompt
4. 八戒能说出"上次你说..."

### Phase 8: RAG深度优化

**目标**: 检索更精准，回答更优质

**混合检索**:
- 向量检索 (语义匹配) + BM25关键词检索
- 结果融合 (RRF算法)

**Rerank精排**:
- 使用Cross-Encoder模型对Top-20重排序
- 取Top-5作为最终上下文

**引用高亮**:
- 前端显示答案时，标注引用来源
- 点击引用可查看原文

---

## 五、文件变更总览

### 新建文件
```
backend/
  utils/
    logger.py           # 统一日志配置
    qwen_util.py        # 阿里云LLM封装
    tts_util.py         # 语音合成
    asr_util.py         # 语音识别
    llm_router.py       # 模型路由
    memory_util.py      # 记忆管理
    rerank_util.py      # Rerank精排
  service/
    memory_service.py   # 记忆服务
    tts_service.py      # TTS服务
  controller/
    tts_controller.py   # TTS接口
    memory_controller.py # 记忆接口

frontend/src/
  composables/
    useSpeech.js         # 语音合成/识别组合式函数
    useChatHistory.js    # 聊天历史管理
  stores/
    modules/
      conversation.js    # 对话状态管理
```

### 修改文件
```
backend/
  config.py              # 增加阿里云配置
  main.py                # 日志初始化，新路由
  dao/base_dao.py        # 实现泛型基类
  dao/student_dao.py     # 继承基类
  dao/user_dao.py        # 继承基类
  utils/deepseek_util.py # 统一接口
  utils/embedding_util.py # 修正注释，支持阿里云嵌入
  utils/milvus_util.py   # print→logging
  utils/text_chunker.py  # print→logging
  service/agent_service.py # 全Agent支持history
  service/rag_service.py   # 支持history，混合检索
  service/nl2sql_service.py # 支持多轮
  service/bajie_service.py  # 支持history

frontend/src/
  views/bajie/BajieChat.vue      # 接SSE，语音
  views/bajie/BajieGames.vue     # 接后端API
  views/bajie/SocialAssistant.vue # 接后端API
  views/bajie/KnowledgeQA.vue    # 接流式
```

---

## 六、风险评估与回退策略

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| 阿里云API调用失败 | 中 | 高 | 自动回退DeepSeek |
| 语音功能浏览器兼容 | 高 | 中 | 降级为文字，提示不支持 |
| Milvus向量维度变化(512→768) | 低 | 高 | 新建集合，保留旧集合 |
| 前端SSE兼容问题 | 低 | 中 | 提供非流式fallback |

---

## 七、成功标准

- [ ] 所有前端TODO消除，无假数据
- [ ] 所有print()替换为logging
- [ ] 阿里云API可正常调用，双模型容错
- [ ] 对话支持多轮上下文
- [ ] 语音合成可用
- [ ] 无控制台报错，无未处理异常
