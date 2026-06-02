# Phase 3: 前端API对接 实施计划

> **Goal:** 消除所有假数据和TODO，前端真实调用后端API
> **Architecture:** 前端Vue组件对接后端REST/SSE接口
> **Tech Stack:** Vue3, EventSource, Axios

---

## 文件变更总览

| 操作 | 文件 | 说明 |
|------|------|------|
| 修改 | `frontend/src/views/bajie/BajieChat.vue` | 接SSE流式接口 |
| 修改 | `frontend/src/views/bajie/BajieGames.vue` | 接灯谜/诗词API |
| 修改 | `frontend/src/views/bajie/SocialAssistant.vue` | 接话术/情书API |
| 修改 | `frontend/src/views/bajie/KnowledgeQA.vue` | 接流式RAG |
| 新建 | `frontend/src/api/bajie.js` | 八戒相关API封装 |
| 新建 | `frontend/src/api/agent.js` | 多智能体API封装 |
| 修改 | `frontend/src/api/request.js` | SSE支持 |

---

## Task 1: 新建API模块

**Files:**
- 新建: `frontend/src/api/bajie.js`
- 新建: `frontend/src/api/agent.js`

**Step 1: 八戒API封装**

```javascript
// frontend/src/api/bajie.js
import request from './request'

export function getRiddle(difficulty) {
  return request.get('/bajie/riddle', { params: { difficulty } })
}

export function checkRiddle(data) {
  return request.post('/bajie/riddle/check', data)
}

export function getPoetry() {
  return request.get('/bajie/poetry')
}

export function checkPoetry(data) {
  return request.post('/bajie/poetry/check', data)
}

export function generateChatLines(data) {
  return request.post('/bajie/chat-lines', data)
}

export function writeLoveLetter(data) {
  return request.post('/bajie/love-letter', data)
}
```

**Step 2: 多智能体API封装**

```javascript
// frontend/src/api/agent.js
import request from './request'

export function agentChat(data) {
  return request.post('/agent/chat', data)
}

export function agentChatStream(message, history, onMessage, onIntent, onDone, onError) {
  const payload = JSON.stringify({ message, history })
  
  const eventSource = new EventSource(
    `/api/v1/agent/chat/stream?payload=${encodeURIComponent(payload)}`
  )
  
  // 注意: SSE不支持POST，需要改用fetch + ReadableStream
  // 或者后端支持GET传参
  
  return eventSource
}

// 使用fetch + ReadableStream实现POST SSE
export async function agentChatStreamFetch(message, history, callbacks) {
  const { onIntent, onContent, onDone, onError } = callbacks
  
  try {
    const response = await fetch('/api/v1/agent/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      },
      body: JSON.stringify({ message, history }),
    })
    
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')
      
      for (const line of lines) {
        if (line.startsWith('event: intent')) {
          // 读取下一行的data
        } else if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') {
            onDone?.()
            return
          }
          try {
            const parsed = JSON.parse(data)
            if (parsed.intent) {
              onIntent?.(parsed.intent)
            } else if (parsed.content) {
              onContent?.(parsed.content)
            }
          } catch (e) {
            // 忽略解析错误
          }
        }
      }
    }
    
    onDone?.()
  } catch (error) {
    onError?.(error)
  }
}
```

---

## Task 2: BajieChat.vue改造

**Files:**
- 修改: `frontend/src/views/bajie/BajieChat.vue`

**改造要点**:

```vue
<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { Avatar, UserFilled, Microphone, Promotion } from '@element-plus/icons-vue'
import { agentChatStreamFetch } from '@/api/agent'

// 聊天消息列表
const messages = ref([
  { role: 'assistant', content: '嘿！俺老猪来也！你是来找俺唠嗑的，还是有啥正事要办？', time: new Date().toLocaleTimeString() },
])
const inputMsg = ref('')
const streaming = ref(false)
const streamText = ref('')
const voiceOn = ref(false)
const msgContainer = ref(null)

/** 发送消息 - 真实SSE调用 */
async function sendMessage() {
  const text = inputMsg.value.trim()
  if (!text || streaming.value) return
  
  // 添加用户消息
  messages.value.push({ 
    role: 'user', 
    content: text, 
    time: new Date().toLocaleTimeString() 
  })
  inputMsg.value = ''
  await scrollToBottom()
  
  // 构建历史记录 (最近10轮)
  const history = messages.value
    .slice(-20, -1) // 排除刚添加的用户消息
    .map(m => ({ role: m.role, content: m.content }))
  
  streaming.value = true
  streamText.value = ''
  
  await agentChatStreamFetch(text, history, {
    onIntent: (intent) => {
      console.log('意图:', intent)
    },
    onContent: (content) => {
      streamText.value += content
      scrollToBottom()
    },
    onDone: () => {
      messages.value.push({
        role: 'assistant',
        content: streamText.value,
        time: new Date().toLocaleTimeString(),
      })
      streamText.value = ''
      streaming.value = false
    },
    onError: (error) => {
      messages.value.push({
        role: 'assistant',
        content: '哎哟，俺老猪脑子卡壳了...请稍后再试！',
        time: new Date().toLocaleTimeString(),
      })
      streamText.value = ''
      streaming.value = false
      console.error('SSE错误:', error)
    },
  })
}

/** 语音输入 */
function toggleVoice() {
  if (!('webkitSpeechRecognition' in window)) {
    ElMessage.warning('您的浏览器不支持语音识别')
    return
  }
  
  const recognition = new webkitSpeechRecognition()
  recognition.lang = 'zh-CN'
  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript
    inputMsg.value = transcript
    sendMessage()
  }
  recognition.start()
}

async function scrollToBottom() {
  await nextTick()
  const el = msgContainer.value
  if (el) el.scrollTop = el.scrollHeight
}

onMounted(() => scrollToBottom())
</script>
```

---

## Task 3: BajieGames.vue改造

**Files:**
- 修改: `frontend/src/views/bajie/BajieGames.vue`

**改造要点**:

```vue
<script setup>
import { ref } from 'vue'
import { Trophy, EditPen } from '@element-plus/icons-vue'
import { getRiddle, checkRiddle, getPoetry, checkPoetry } from '@/api/bajie'
import { ElMessage } from 'element-plus'

// ===== 灯谜状态 =====
const score = ref(0)
const currentRiddle = ref(null)
const guess = ref('')
const answered = ref(false)
const showAnswer = ref(false)
const feedback = ref('')
const feedbackType = ref('')
const history = ref([])

// ===== 飞花令状态 =====
const currentPoetry = ref(null)
const poetryAnswer = ref('')
const poetryDone = ref(false)
const poetryFeedback = ref('')
const poetryFeedbackType = ref('')

function difficultyType(d) {
  const map = { '简单': 'success', '中等': 'warning', '困难': 'danger' }
  return map[d] || ''
}

// ----- 灯谜逻辑 -----
/** 获取新灯谜 - 真实API */
async function getNewRiddle() {
  try {
    const res = await getRiddle()
    currentRiddle.value = res.data.data
    guess.value = ''
    answered.value = false
    showAnswer.value = false
    feedback.value = ''
  } catch (e) {
    ElMessage.error('获取灯谜失败')
  }
}

/** 提交猜谜 - 真实API */
async function submitGuess() {
  if (!guess.value.trim() || answered.value) return
  const userGuess = guess.value.trim()
  
  try {
    const res = await checkRiddle({
      riddle_text: currentRiddle.value.text,
      answer: userGuess,
    })
    const result = res.data.data
    answered.value = true
    
    if (result.correct) {
      feedback.value = result.message
      feedbackType.value = 'success'
      score.value += result.score_change
    } else {
      feedback.value = result.message
      feedbackType.value = 'error'
    }
    
    history.value.unshift({
      riddle: currentRiddle.value.text.slice(0, 20) + '...',
      guess: userGuess,
      correct: result.correct,
      time: new Date().toLocaleTimeString(),
    })
  } catch (e) {
    ElMessage.error('提交答案失败')
  }
}

// ----- 飞花令逻辑 -----
/** 获取新诗词 - 真实API */
async function getNewPoetry() {
  try {
    const res = await getPoetry()
    currentPoetry.value = res.data.data
    poetryAnswer.value = ''
    poetryDone.value = false
    poetryFeedback.value = ''
  } catch (e) {
    ElMessage.error('获取诗词失败')
  }
}

/** 提交对诗 - 真实API */
async function submitPoetry() {
  if (!poetryAnswer.value.trim() || poetryDone.value) return
  
  try {
    const res = await checkPoetry({
      line: currentPoetry.value.line,
      answer: poetryAnswer.value.trim(),
    })
    const result = res.data.data
    poetryDone.value = true
    
    if (result.correct) {
      poetryFeedback.value = result.message
      poetryFeedbackType.value = 'success'
    } else {
      poetryFeedback.value = result.message
      poetryFeedbackType.value = 'warning'
    }
  } catch (e) {
    ElMessage.error('提交答案失败')
  }
}
</script>
```

---

## Task 4: SocialAssistant.vue改造

**Files:**
- 修改: `frontend/src/views/bajie/SocialAssistant.vue`

**改造要点**:

```vue
<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { ChatLineSquare, Postcard } from '@element-plus/icons-vue'
import { generateChatLines, writeLoveLetter } from '@/api/bajie'

// ===== 话术生成 =====
const scenario = ref('first_meet')
const personality = ref('outgoing')
const extraInfo = ref('')
const generating = ref(false)
const generatedLines = ref(null)

async function generateLines() {
  generating.value = true
  try {
    const res = await generateChatLines({
      scenario: scenario.value,
      personality: personality.value,
      extra_info: extraInfo.value,
    })
    generatedLines.value = res.data.data
  } catch (e) {
    ElMessage.error('生成话术失败')
  } finally {
    generating.value = false
  }
}

// ===== 情书代写 =====
const loveLetter = reactive({ to: '', style: 'romantic', memory: '' })
const writing = ref(false)
const writtenLetter = ref('')

async function writeLetter() {
  writing.value = true
  try {
    const res = await writeLoveLetter({
      to: loveLetter.to,
      style: loveLetter.style,
      memory: loveLetter.memory,
    })
    writtenLetter.value = res.data.data
  } catch (e) {
    ElMessage.error('生成情书失败')
  } finally {
    writing.value = false
  }
}

function copyText(text) {
  navigator.clipboard.writeText(text)
  ElMessage.success('已复制到剪贴板')
}
</script>
```

---

## Task 5: KnowledgeQA.vue流式改造

**Files:**
- 修改: `frontend/src/views/bajie/KnowledgeQA.vue`

**改造要点**:

增加流式问答模式切换，使用fetch + ReadableStream:

```javascript
// 在KnowledgeQA.vue中增加流式问答函数
async function askQuestionStream() {
  const q = question.value.trim()
  if (!q || searching.value) return
  
  currentQuestion.value = q
  question.value = ''
  searching.value = true
  
  const qaItem = {
    question: q,
    answer: '',
    references: [],
  }
  qaList.value.push(qaItem)
  
  try {
    const response = await fetch('/api/v1/rag/qa/stream?question=' + encodeURIComponent(q) + '&top_k=5', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      },
    })
    
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') {
            searching.value = false
            return
          }
          qaItem.answer += data
        }
      }
    }
  } catch (e) {
    qaItem.answer = '查询失败，请稍后再试'
  } finally {
    searching.value = false
  }
}
```

---

## 验证清单

- [ ] BajieChat.vue能正常SSE流式对话
- [ ] BajieGames.vue能获取真实灯谜和诗词
- [ ] SocialAssistant.vue能生成真实话术和情书
- [ ] KnowledgeQA.vue支持流式问答
- [ ] 语音输入按钮可用（浏览器支持时）
- [ ] 所有页面无假数据残留
- [ ] 网络错误有友好提示
