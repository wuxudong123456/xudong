# Phase 4-8: 高级功能实施计划

> **Goal:** 对话历史、Function Calling、语音、记忆、RAG优化
> **Architecture:** 上下文感知Agent + 工具调用 + 多模态
> **Tech Stack:** 全栈

---

## Phase 4: 对话历史与上下文记忆

### 目标
所有Agent支持多轮对话，保持上下文连贯性

### 前端改造
- 维护全局 `conversationHistory` (最多20轮)
- 每次发送带上 `history` 字段

### 后端改造

**AgentService改造**:
```python
async def process_message(self, message, history=None):
    history = history or []
    intent = await classify_intent(message, history)  # 历史辅助意图分类
    
    if intent == "data_query":
        reply, data = await self._handle_data_query(message, history)
    elif intent == "knowledge_question":
        reply, data = await self._handle_knowledge(message, history)
    # ... 其他Agent也传递history
```

**NL2SQL多轮改造**:
```python
async def generate_sql(question: str, history: List[Dict] = None) -> str:
    """支持上下文SQL生成"""
    context = ""
    if history:
        # 提取上轮的表/条件信息
        context = f"历史对话:\n{format_history(history)}\n"
    
    prompt = f"{context}{DB_SCHEMA}\n当前问题: {question}"
    # ...
```

**RAG追问改造**:
```python
async def answer_question_async(self, question, top_k=5, history=None):
    if history:
        # 用历史理解指代消解
        question = await resolve_coreference(question, history)
    # ...
```

---

## Phase 5: Function Calling工具调用

### 目标
让Agent能自主调用工具，替代硬编码意图路由

### 工具定义
```python
# backend/utils/tools.py
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": "查询学生管理系统的数据库，获取学生/班级/成绩/就业等数据",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "用户的自然语言查询问题"}
                },
                "required": ["question"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_novel",
            "description": "搜索四大名著相关知识",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "关于四大名著的问题"}
                },
                "required": ["question"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前时间",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": " emotional_support",
            "description": "提供情绪疏导和安慰",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "用户的倾诉内容"}
                },
                "required": ["message"]
            }
        }
    }
]
```

### 工具执行引擎
```python
# backend/utils/tool_executor.py
async def execute_tool(tool_name: str, parameters: dict, db: Session = None):
    """执行工具调用"""
    if tool_name == "query_database":
        return await nl2sql_query(db, parameters["question"])
    elif tool_name == "search_novel":
        service = RAGService()
        return await service.answer_question_async(parameters["question"])
    elif tool_name == "get_current_time":
        from datetime import datetime
        return {"current_time": datetime.now().isoformat()}
    elif tool_name == "emotional_support":
        # 调用情绪疏导Agent
        pass
    # ...
```

### Agent集成
```python
async def process_with_tools(self, message, history=None):
    """使用Function Calling处理消息"""
    messages = history or []
    messages.append({"role": "user", "content": message})
    
    # 第一次调用，让模型决定是否需要工具
    response = await chat_with_functions(messages, TOOLS)
    
    if response["type"] == "function_call":
        # 执行工具
        tool_results = []
        for call in response["calls"]:
            result = await execute_tool(call["function"]["name"], 
                                       json.loads(call["function"]["arguments"]))
            tool_results.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "content": json.dumps(result)
            })
        
        # 将工具结果返回给模型生成最终回复
        messages.append(response["message"])
        messages.extend(tool_results)
        final_response = await chat_completion(messages)
        return final_response
    else:
        return response["content"]
```

---

## Phase 6: 阿里云语音集成

### 后端TTS接口
```python
# backend/controller/tts_controller.py
from fastapi import APIRouter
from backend.utils.tts_util import text_to_speech_url

router = APIRouter()

@router.post("/tts", summary="文本转语音")
async def tts_endpoint(text: str):
    """将文本转为语音，返回音频URL"""
    url = await text_to_speech_url(text)
    return {"code": 200, "data": {"audio_url": url}}
```

### 前端语音播放
```javascript
// frontend/src/composables/useSpeech.js
import { ref } from 'vue'

export function useSpeech() {
  const isPlaying = ref(false)
  const audio = new Audio()
  
  async function speak(text) {
    try {
      const res = await fetch('/api/v1/tts', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text})
      })
      const data = await res.json()
      audio.src = data.data.audio_url
      audio.play()
      isPlaying.value = true
      audio.onended = () => { isPlaying.value = false }
    } catch (e) {
      console.error('TTS失败:', e)
    }
  }
  
  function stop() {
    audio.pause()
    isPlaying.value = false
  }
  
  return { speak, stop, isPlaying }
}
```

### 前端ASR录音
```javascript
// 使用Web Speech API (浏览器原生)
function startRecording() {
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)()
  recognition.lang = 'zh-CN'
  recognition.continuous = false
  recognition.interimResults = false
  
  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript
    // 将识别结果填入输入框
    inputMsg.value = transcript
    sendMessage()
  }
  
  recognition.onerror = (event) => {
    console.error('语音识别错误:', event.error)
    ElMessage.error('语音识别失败，请重试')
  }
  
  recognition.start()
}
```

---

## Phase 7: 长期记忆系统

### 数据库扩展
```sql
-- 用户画像表
CREATE TABLE user_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    nickname VARCHAR(50),
    preferred_topics VARCHAR(500),
    personality_tags VARCHAR(500),
    interaction_count INT DEFAULT 0,
    last_emotion VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
);

-- 记忆片段表
CREATE TABLE memory_fragments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    importance FLOAT DEFAULT 0.5,
    memory_type ENUM('fact', 'preference', 'event', 'emotion') DEFAULT 'fact',
    source_conversation_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_type (memory_type)
);
```

### 记忆服务
```python
# backend/service/memory_service.py
class MemoryService:
    def __init__(self, db: Session):
        self.db = db
    
    async def extract_memories(self, user_id: int, conversation: list):
        """从对话中提取记忆"""
        prompt = f"""从以下对话中提取关键信息（用户偏好、重要事件、情绪状态），
        以JSON格式返回: {{"memories": [{{"type": "fact|preference|event|emotion", 
        "content": "...", "importance": 0.8}}]}}\n\n对话:\n{format_conversation(conversation)}"""
        
        result = await chat_completion([{"role": "user", "content": prompt}])
        memories = parse_json(result)
        
        for mem in memories:
            self.save_memory(user_id, mem)
    
    def get_relevant_memories(self, user_id: int, query: str, limit=5):
        """检索相关记忆"""
        # 简单实现：按关键词匹配
        # 进阶：向量化记忆后语义检索
        memories = self.db.query(MemoryFragment).filter(
            MemoryFragment.user_id == user_id
        ).order_by(MemoryFragment.importance.desc()).limit(limit).all()
        return memories
    
    def build_memory_prompt(self, user_id: int) -> str:
        """构建记忆提示词"""
        memories = self.get_relevant_memories(user_id)
        if not memories:
            return ""
        
        memory_text = "\n".join([f"- {m.content}" for m in memories])
        return f"关于用户的记忆:\n{memory_text}\n请在回复中自然地引用这些记忆。"
```

### Agent集成记忆
```python
async def _handle_chat(self, message, history, user_id=None):
    system_prompt = self._bajie_system_prompt()
    
    # 注入记忆
    if user_id:
        memory_service = MemoryService(self.db)
        memory_prompt = memory_service.build_memory_prompt(user_id)
        if memory_prompt:
            system_prompt += "\n" + memory_prompt
    
    messages = history + [{"role": "user", "content": message}]
    reply = await chat_completion(messages, system_prompt)
    
    # 提取新记忆
    if user_id:
        await memory_service.extract_memories(user_id, messages + [{"role": "assistant", "content": reply}])
    
    return reply, None
```

---

## Phase 8: RAG深度优化

### 混合检索
```python
# backend/utils/hybrid_search.py
async def hybrid_search(query: str, top_k=5):
    """混合检索：向量 + 关键词"""
    # 1. 向量检索
    query_vector = await get_embedding(query)
    vector_results = search_all_novels(query_vector, top_k=top_k*2)
    
    # 2. BM25关键词检索 (使用whoosh或简单实现)
    keyword_results = bm25_search(query, top_k=top_k*2)
    
    # 3. RRF融合排序
    fused = reciprocal_rank_fusion(vector_results, keyword_results, k=60)
    return fused[:top_k]


def reciprocal_rank_fusion(list1, list2, k=60):
    """RRF融合算法"""
    scores = {}
    
    for rank, item in enumerate(list1):
        doc_id = item["chunk_id"]
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
        scores[doc_id + "_data"] = item
    
    for rank, item in enumerate(list2):
        doc_id = item["chunk_id"]
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
        scores[doc_id + "_data"] = item
    
    sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [scores[d[0] + "_data"] for d in sorted_docs if "_data" in scores]
```

### Rerank精排
```python
# backend/utils/rerank_util.py
async def rerank(query: str, candidates: list, top_k=5):
    """使用Cross-Encoder精排"""
    # 使用阿里云或本地轻量模型
    pairs = [[query, c["content"]] for c in candidates]
    
    # 调用模型打分
    scores = await get_cross_encoder_scores(pairs)
    
    for i, score in enumerate(scores):
        candidates[i]["rerank_score"] = score
    
    candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
    return candidates[:top_k]
```

### 引用高亮
前端改造：
```vue
<!-- 在答案中标注引用 -->
<div class="answer-text" v-html="highlightReferences(qa.answer, qa.references)"></div>

<script>
function highlightReferences(answer, refs) {
  let html = answer
  refs.forEach((ref, idx) => {
    const marker = `【引用${idx+1}】`
    html += `<sup class="ref-marker" title="${ref.content}">${marker}</sup>`
  })
  return html
}
</script>
```

---

## 验证清单 (Phase 4-8)

- [ ] 多轮对话能正确理解上下文
- [ ] NL2SQL支持追问（如"那平均成绩呢？"）
- [ ] Function Calling能正确调用工具
- [ ] TTS合成语音正常播放
- [ ] ASR语音识别准确
- [ ] 长期记忆能记住用户偏好
- [ ] RAG混合检索精度提升
- [ ] 引用高亮正常显示
