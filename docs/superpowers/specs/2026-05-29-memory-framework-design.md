# 记忆框架 + 主动对话系统 设计文档

> **项目**: 学生管理系统 + 猪八戒多智能体AI问答
> **日期**: 2026-05-29
> **目标**: 构建四层记忆架构（存储→提取→检索→主动对话），实现数字人级别的记忆与主动交互能力
> **路线**: 路线2 — 向量记忆版 + ProactiveAgent 主动对话层

---

## 一、项目记忆现状

### 1.1 已有能力

| 组件 | 能力 | 局限 |
|------|------|------|
| `conversation_history` 表 | 原样存储每轮对话消息 | 仅存储，不提取关键信息 |
| `memory_service.py` | 创建会话、存取消息、加载历史 | 仅按时间倒序取最近N条，无语义检索 |
| `agent_service._handle_chat()` | 注入最近20条历史到LLM | 纯粹时间序，不区分重要性 |
| `agent_controller.py` | 对话结束自动存档 | 不处理存档内容，不提取记忆 |

### 1.2 缺失能力

- ❌ 无记忆提取（从对话中自动抽取关键事实/偏好/情绪）
- ❌ 无语义检索（无法根据当前话题找到相关历史记忆）
- ❌ 无用户画像（无法跨会话记住用户是谁）
- ❌ 无记忆衰减（旧记忆和新记忆没有权重区分）
- ❌ 无主动对话（AI 永远被动应答，不会主动搭话）

---

## 二、目标架构：四层记忆体系

```
┌─────────────────────────────────────────────────────────────┐
│                    第四层：主动对话层 (ProactiveAgent)          │
│  触发检测 → 话题选择 → 消息生成 → SSE推送                      │
│  职责: 让AI从"被动应答"变成"主动搭话"                          │
└──────────────────────────┬──────────────────────────────────┘
                           │ 依赖记忆层提供素材
┌──────────────────────────▼──────────────────────────────────┐
│                    第三层：记忆检索层 (MemoryRetrieval)         │
│  语义向量搜索 → 重要性排序 → 时间衰减 → 构建记忆提示词           │
│  职责: 从海量记忆中捞出当前对话最相关的片段                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    第二层：记忆提取层 (MemoryExtraction)        │
│  LLM提取 → 分类(fact/preference/event/emotion) → 重要性打分    │
│  → 向量化 → 双写存储 → 更新用户画像                             │
│  职责: 从原始对话中提炼结构化记忆                                │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    第一层：记忆存储层 (MemoryStorage)           │
│  MySQL: memory_fragments 表 (结构化, 可SQL查询)                │
│  MySQL: user_profiles 表 (用户画像, 快速读取)                  │
│  Milvus: memory_vectors 集合 (512维语义向量, COSINE检索)       │
│  职责: 持久化 + 双通道读写                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 三、第一层：记忆存储层

### 3.1 user_profiles 表（MySQL）

```sql
CREATE TABLE user_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    nickname VARCHAR(50) COMMENT '用户昵称',
    preferred_topics VARCHAR(500) COMMENT '偏好话题(逗号分隔)',
    personality_tags VARCHAR(500) COMMENT '性格标签(逗号分隔)',
    interaction_count INT DEFAULT 0 COMMENT '累计交互次数',
    last_emotion VARCHAR(50) COMMENT '最近一次情绪状态',
    last_active_time DATETIME COMMENT '最近活跃时间',
    proactive_preference TINYINT DEFAULT 1 COMMENT '是否接受主动搭话: 0=静默 1=允许',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
);
```

### 3.2 memory_fragments 表（MySQL）

```sql
CREATE TABLE memory_fragments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    content TEXT NOT NULL COMMENT '记忆内容',
    importance FLOAT DEFAULT 0.5 COMMENT '重要性 0.0-1.0',
    memory_type ENUM('fact','preference','event','emotion') DEFAULT 'fact',
    source_session_id VARCHAR(100) COMMENT '来源会话ID',
    chunk_id VARCHAR(100) COMMENT 'Milvus中对应的向量ID',
    access_count INT DEFAULT 0 COMMENT '被检索次数',
    last_accessed_at DATETIME COMMENT '最近被检索时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_type (memory_type),
    INDEX idx_importance (importance)
);
```

### 3.3 memory_vectors 集合（Milvus）

```
集合名: memory_vectors
Schema:
  - id: INT64 (自增主键)
  - chunk_id: VARCHAR(100) (对应MySQL memory_fragments.chunk_id)
  - user_id: INT64
  - content: VARCHAR(2000) (记忆文本)
  - embedding: FLOAT_VECTOR(512) (语义向量, COSINE度量, IVF_FLAT索引)

与现有4个名著集合共享同一Milvus实例，集合名不冲突。
```

---

## 四、第二层：记忆提取层

### 4.1 提取时机

```
每次对话结束（agent_controller.chat/chat_stream 的 finally 块）
    │
    ▼
异步触发 memory_extractor.extract(user_id, conversation)
    │
    ▼
非阻塞：提取失败不影响对话响应
```

### 4.2 提取流程

```
输入: 本轮对话 [{"role":"user","content":"我这次考试压力好大"},
               {"role":"assistant","content":"小明你别急..."}]
    │
    ▼
Step 1: LLM提取 (DeepSeek chat_completion, temperature=0.1)
    prompt: "从以下对话中提取关键信息，以JSON格式返回：
             {memories: [{type: fact|preference|event|emotion,
                         content: ..., importance: 0.0-1.0}]}
             规则: fact=事实, preference=偏好, event=事件, emotion=情绪"
    │
    ▼
Step 2: 去重 (与用户已有记忆做Jaccard文本相似度 > 0.8 → 跳过)
    │
    ▼
Step 3: 向量化 (DeepSeek embedding: text-embedding-3-small)
    │
    ▼
Step 4: 双写
    ├── MySQL memory_fragments: INSERT
    └── Milvus memory_vectors: INSERT (含embedding向量)
    │
    ▼
Step 5: 更新画像
    ├── interaction_count += 1
    ├── 合并 preferred_topics (去重, 最多10个)
    ├── 合并 personality_tags (去重, 最多8个)
    └── 更新 last_emotion
```

### 4.3 提取示例

```
输入对话:
  用户: "我叫小明，大二计算机系的，这次期末考试压力好大，昨晚失眠了"
  AI:   "小明别急，俺老猪当年被贬下凡间也没你这么愁..."

LLM提取输出:
{
  "memories": [
    {"type": "fact",      "content": "用户叫小明",             "importance": 1.0},
    {"type": "fact",      "content": "大二计算机系学生",        "importance": 0.9},
    {"type": "emotion",   "content": "期末考试压力大,曾失眠",    "importance": 0.8},
    {"type": "event",     "content": "正在准备期末考试",         "importance": 0.7}
  ]
}
```

---

## 五、第三层：记忆检索层

### 5.1 检索触发

```
每次收到用户消息 → agent_service.process_message()
    │
    ├── 用户消息向量化 (embedding)
    ├── 双路检索
    │   ├── Milvus: 语义相似度 top_k=10
    │   └── MySQL:  importance DESC + 最近20条
    ├── 合并去重 → 排序
    └── 构建记忆提示词 → 注入LLM system_prompt
```

### 5.2 排序公式

```
score = 语义相似度 × 0.6 + importance × 0.3 + 时间衰减 × 0.1

时间衰减: e^(-天数/30)
  第0天:  权重 1.00
  第7天:  权重 0.79
  第14天: 权重 0.63
  第30天: 权重 0.37
  第60天: 权重 0.14
```

### 5.3 记忆提示词格式

```
[系统记忆提示]
关于用户你已知以下信息：
- 用户叫小明，大二计算机系学生
- 上次数学月考成绩不理想
- 近期考试压力大，喜欢通过打球减压
请在回答时自然地结合这些信息，让用户感到被记住。
不要生硬地罗列这些信息，要与当前话题自然融合。
```

### 5.4 对接点

| 现有函数 | 注入位置 | 注入内容 |
|---------|---------|---------|
| `agent_service._handle_chat()` | system_prompt 前缀 | 记忆提示词 |
| `agent_service._handle_emotional()` | system_prompt 前缀 | 情绪历史 |
| `agent_service._handle_data_query()` | system_prompt 前缀 | 查询偏好 |
| `bajie_service.bajie_chat()` | system_prompt 前缀 | 角色+用户记忆 |

---

## 六、第四层：主动对话层

### 6.1 触发检测器（TriggerDetector）

六种触发时机：

| # | 触发类型 | 条件 | 示例消息（八戒口吻） |
|---|---------|------|---------------------|
| ① | 见面问候 | 用户打开聊天页 + 距上次对话>1小时 | "小明回来啦！上次你问的那个问题俺老猪查到了～" |
| ② | 沉默搭话 | 用户>2分钟无消息 | "小明？还在吗？有啥想问的别憋着！" |
| ③ | 时段关怀 | 22:00-06:00/06:00-09:00/11:30-13:00 | "都这个点了还没睡？俺老猪都睡醒一觉了" |
| ④ | 事件提醒 | 记忆中有日期事件且即将到期 | "你上次说周五有考试，明天就是周五了！" |
| ⑤ | 情绪追踪 | 上次情绪=负面 + 距上次>24小时 | "上次聊完你好像心情不太好，现在好点了吗？" |
| ⑥ | 兴趣激活 | 用户画像有偏好话题 + 可推送 | "俺老猪记得你喜欢三国，要不要听段赵云的故事？" |

### 6.2 防骚扰机制

```
规则:
  - 同类型触发最小间隔: 问候30分钟, 沉默10分钟, 时段关怀4小时
  - 每小时最多5条主动消息
  - 用户30秒内回复 → 标记高互动 → 允许更频繁
  - 用户连续2次忽略 → 标记低互动 → 进入"安静模式"(每小时最多1条)
```

### 6.3 话题选择器（TopicSelector）

```
候选话题池:
  T1: 问候寒暄 (基于上次对话尾句自然接续)
  T2: 情绪关怀 (last_emotion = 负面时优先)
  T3: 事件提醒 (记忆中有日期事件时启用)
  T4: 兴趣引导 (基于 preferred_topics)
  T5: 通用闲聊 (天气/节气/节日)

排序公式:
  score = 触发匹配度 × 0.4 + 情感需求度 × 0.3 + 记忆相关度 × 0.2 + 新鲜度 × 0.1

选择最高分话题 → 送入消息生成器
```

### 6.4 消息生成器（MessageGenerator）

```
输入: topic + 记忆片段 + 角色 + 用户画像

Step 1: 角色风格适配
  猪八戒(0.85): 幽默接地气、自称"俺老猪"
  鲁智深(0.80): 豪爽直接、自称"洒家"
  林黛玉(0.90): 含蓄文艺、自称"我"
  诸葛亮(0.70): 稳重睿智、自称"亮"

Step 2: 亲密度控制
  interaction_count < 5  → 礼貌疏离
  interaction_count 5-20 → 适度亲近
  interaction_count > 20 → 亲密老友

Step 3: LLM生成 (temperature=角色温度, max_tokens=100)
Step 4: 安全过滤 (不含敏感词, 不过度追问隐私, 不反复提负面事件)
```

### 6.5 推送机制：SSE长连接

```
新增API: GET /api/v1/memory/proactive-stream

流程:
  前端打开聊天页 → 建立SSE连接
  后端每15秒扫描触发条件
  满足条件 → 推送: event=proactive, data={"content":"..."}
  前端接收 → "对方正在输入..."动画 → 弹出AI消息(标注"主动搭话")
  离开聊天页 → 断开SSE

优势: 复用现有SSE基础设施（agent_chat_stream已使用SSE）
```

---

## 七、完整数据流

```
时间线 ──────────────────────────────────────────────────────────→

用户打开聊天页
    │
    ├─→ 前端建立SSE连接到 /api/v1/memory/proactive-stream
    │
    ├─→ 后端 ProactiveService 定时扫描(15秒/次)
    │      ├─ 查询 user_profiles
    │      ├─ 查询 memory_fragments
    │      ├─ 检查时间/情绪/事件 → 触发判定
    │      ├─ 话题选择 → 消息生成 → SSE推送
    │      └─→ 前端收到主动消息
    │
用户发消息: "我今天又失眠了"
    │
    ├─→ agent_controller → AgentService.process_message()
    │      │
    │      ├─ Step 1: 意图分类 (classify_intent)
    │      │      → "emotional_support"
    │      │
    │      ├─ Step 2: 记忆检索 (MemoryRetriever)
    │      │      → 向量化消息
    │      │      → Milvus搜索: "考试压力大"(0.87), "上次失眠"(0.82)
    │      │      → MySQL补充: "用户叫小明"(1.0), "喜欢打球"(0.9)
    │      │      → 构建记忆提示词
    │      │
    │      ├─ Step 3: LLM生成回复
    │      │      → system_prompt = 角色人设 + 记忆提示词
    │      │      → "小明，俺老猪记得你上次就失眠过一次..."
    │      │
    │      └─ Step 4: 回复用户
    │
    ├─→ 对话结束, 触发记忆提取 (MemoryExtractor)
    │      ├─ LLM提取本论关键信息
    │      ├─ 去重 → 向量化 → 双写(MySQL + Milvus)
    │      └─ 更新 user_profiles 画像
    │
    └─→ 存档到 conversation_history (现有逻辑不动)
```

---

## 八、项目改造清单

### 8.1 新增文件

| 文件 | 职责 |
|------|------|
| `backend/utils/memory_extractor.py` | LLM记忆提取 + 向量化 + 去重 + 双写 |
| `backend/utils/memory_retriever.py` | 语义检索 + 重要性排序 + 时间衰减 + 构建提示词 |
| `backend/service/memory_service.py` | 重构: 整合 MemoryExtractor + MemoryRetriever + 画像管理 |
| `backend/service/proactive_service.py` | 主动对话引擎: 触发检测 + 话题选择 + 消息生成 |
| `backend/controller/proactive_controller.py` | SSE主动消息推送接口 |
| `backend/entity/user_profile.py` | UserProfile ORM实体 |
| `backend/entity/memory_fragment.py` | MemoryFragment ORM实体 |

### 8.2 改造现有文件

| 文件 | 改造内容 | 风险评估 |
|------|---------|---------|
| `agent_controller.py` | 对话结束触发 `memory_service.extract()` | 低: finally块新增异步调用, 不阻断主流程 |
| `agent_service.py` | `_handle_chat/_handle_emotional` 注入记忆提示词 | 低: system_prompt末尾追加文本 |
| `bajie_service.py` | `bajie_chat` 注入用户画像 | 低: 同上 |
| `main.py` | 注册 memory_router 和 proactive_router | 低: 纯新增路由 |

### 8.3 新增API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/memory/proactive-stream` | SSE主动消息推送 |
| GET | `/api/v1/memory/profile` | 查看当前用户画像 |
| POST | `/api/v1/memory/extract` | 手动触发记忆提取 |
| DELETE | `/api/v1/memory/fragments/{id}` | 删除单条记忆 |

### 8.4 新增数据库

| 数据库 | 表/集合 | 说明 |
|--------|---------|------|
| MySQL | `user_profiles` | 用户画像表 |
| MySQL | `memory_fragments` | 记忆片段表 |
| Milvus | `memory_vectors` | 记忆向量集合(与现有4个名著集合并存) |

---

## 九、兼容性分析

### 9.1 是否会破坏现有功能

| 风险点 | 分析 | 结论 |
|--------|------|------|
| 新增MySQL表 | `user_profiles`和`memory_fragments`是新表，不修改任何现有表结构 | ✅ 零风险 |
| 新增Milvus集合 | `memory_vectors`是独立集合，不修改现有4个名著集合 | ✅ 零风险 |
| 改造agent_service | 仅在system_prompt末尾追加文本，不改变原有逻辑 | ✅ 低风险 |
| 改造agent_controller | 在finally块新增异步调用，异常被try/catch包裹，不影响主流程 | ✅ 低风险 |
| 改造bajie_service | 仅system_prompt追加，函数签名不变 | ✅ 低风险 |
| 新增路由 | 新路由不拦截现有路由 | ✅ 零风险 |
| NL2SQL/学生管理/成绩/就业/班级/课程 | 完全不涉及这些模块 | ✅ 零影响 |
| RAG知识问答/图谱 | 完全不涉及这些模块 | ✅ 零影响 |
| 灯谜/飞花令/社交僚机/情绪疏导 | 这些功能走agent_service，仅受益于记忆注入 | ✅ 零影响 |
| DeepSeek API调用量 | 每次对话结束后多1次提取调用 + 检索时多1次embedding调用 | ⚠️ 成本增加约30% |
| 数据库写入量 | 每次对话多1条Milvus写入 + 1-3条MySQL写入 | ⚠️ 负载轻微增加 |
| 数据库连接 | 新增Milvus连接复用现有连接，MySQL无新增连接 | ✅ 无影响 |

### 9.2 总结

**完整方案插入项目：可行，不会导致现有功能异常。** 所有新增模块都是独立添加，不修改任何现有数据库表结构、不修改任何现有API接口签名、不删除任何现有代码。唯一的代价是DeepSeek API调用量增加约30%。

---

## 十、仅应用于智能体的裁剪方案

如果只将记忆框架应用到多智能体对话（BajieChat），不涉及管理系统：

### 10.1 裁剪后的范围

| 模块 | 完整方案 | 仅智能体 |
|------|:------:|:------:|
| user_profiles 表 | ✅ | ✅ |
| memory_fragments 表 | ✅ | ✅ |
| memory_vectors 集合 | ✅ | ✅ |
| 记忆提取 | ✅ | ✅ |
| 记忆检索 | agent_service全部 + bajie_service | agent_service全部 + bajie_service |
| 主动对话 | ✅ | ✅ |
| 管理系统CRUD | 注入记忆提示词 | ❌ 不注 |
| Dashboard | 注入记忆提示词 | ❌ 不注 |

### 10.2 可行性

**完全可行。** 记忆框架天然就是为对话场景设计的，管理系统的CRUD查询不需要记忆能力。裁剪后：

- 改造 `agent_service._handle_chat/_handle_emotional/_handle_data_query` → 注入记忆
- 改造 `bajie_service.bajie_chat` → 注入记忆
- 管理系统所有接口 → 零改动

### 10.3 影响评估

**不会影响任何现有功能异常。** 理由同上：独立表、独立集合、追加式改造、异常隔离。

---

## 十一、实施建议

| 阶段 | 内容 | 预估工时 |
|------|------|---------|
| Phase 1 | 数据库建表 + Milvus建集合 + ORM实体 | 0.5天 |
| Phase 2 | memory_extractor.py (LLM提取+向量化+双写+画像更新) | 1.5天 |
| Phase 3 | memory_retriever.py (语义检索+排序+衰减+提示词构建) | 1天 |
| Phase 4 | 改造 agent_service + bajie_service + agent_controller (注入记忆) | 1天 |
| Phase 5 | proactive_service.py + proactive_controller.py (主动对话) | 1.5天 |
| Phase 6 | 前端BajieChat.vue改造 (SSE监听+主动消息展示+活跃度指示器) | 1天 |
| Phase 7 | 联调测试 + 调优 | 1天 |
| **合计** | | **7.5天** |