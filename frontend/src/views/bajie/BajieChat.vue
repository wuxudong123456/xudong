<!-- BajieChat.vue - 四大名著人物对话（带会话记忆） -->
<template>
  <div class="bajie-chat">
    <div class="chat-layout">
      <!-- 左侧会话列表 -->
      <div class="session-sidebar">
        <div class="sidebar-header">
          <span class="title">对话记录</span>
          <el-button type="primary" size="small" @click="newChat" :icon="Plus">新对话</el-button>
        </div>
        <div class="session-list">
          <div v-if="sessions.length === 0" class="empty-hint">暂无对话记录</div>
          <div
            v-for="s in sessions" :key="s.session_id"
            :class="['session-item', { active: s.session_id === currentSessionId }]"
            @click="openSession(s)"
          >
            <span class="s-emoji">{{ charEmoji(s.character) }}</span>
            <div class="s-info">
              <div class="s-title">{{ s.title }}</div>
              <div class="s-meta">{{ s.msg_count }} 条 · {{ fmtTime(s.last_time) }}</div>
            </div>
            <el-button link size="small" class="s-del" @click.stop="delSession(s.session_id)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </div>

      <!-- 右侧聊天区 -->
      <div class="chat-main">
        <!-- 角色选择 + 展示 -->
        <el-card class="bajie-profile" shadow="never" :class="activeCharacter">
          <el-row :gutter="16" align="middle">
            <el-col :span="3" style="text-align:center">
              <div class="profile-avatar" :class="activeCharacter">
                <span class="avatar-emoji">{{ currentChar.emoji }}</span>
                <span class="avatar-initial">{{ currentChar.initial }}</span>
              </div>
            </el-col>
            <el-col :span="14">
              <div class="profile-intro">
                <p class="profile-name">
                  <el-select v-model="activeCharacter" class="char-select" @change="switchCharacter" popper-class="char-popper">
                    <el-option v-for="c in characters" :key="c.key" :value="c.key"
                      :label="`${c.emoji} ${c.name} · ${c.novel}`"
                    >
                      <span style="font-size:18px">{{ c.emoji }}</span>
                      <span style="font-weight:bold;margin-left:6px">{{ c.name }}</span>
                      <span style="color:#909399;font-size:12px;margin-left:6px">{{ c.novel }} · {{ c.title }}</span>
                    </el-option>
                  </el-select>
                  <el-tag :class="activeCharacter" size="small">{{ currentChar.title }}</el-tag>
                </p>
                <p class="profile-desc">{{ currentChar.desc }}</p>
                <p class="profile-style">{{ currentChar.style }}</p>
              </div>
            </el-col>
            <el-col :span="7">
              <div class="profile-quote">"{{ currentChar.quote }}"</div>
            </el-col>
          </el-row>
        </el-card>

        <!-- 状态指示器 -->
        <div class="proactive-indicator">
          <span class="pi-dot" :class="{ active: proactiveActive }"></span>
          <span class="pi-text">{{ proactiveActive ? 'AI在线' : 'AI静默' }}</span>
        </div>

        <!-- 聊天窗口 -->
        <el-card shadow="never" class="chat-card">
          <div class="chat-messages" ref="msgContainer">
            <div v-for="(msg, idx) in messages" :key="idx" :class="['msg-item', msg.role]">
              <div class="msg-avatar">
                <el-icon :size="32" v-if="msg.role==='user'"><UserFilled /></el-icon>
                <span v-else class="char-icon">{{ currentChar.emoji }}</span>
              </div>
              <div class="msg-content">
                <div class="msg-text" :class="{ proactive: msg._proactive }">
                  <span v-if="msg._proactive" class="proactive-tag">主动搭话</span>
                  {{ msg.content }}
                </div>
                <div class="msg-time">{{ msg.time }}</div>
                <VoiceOutput v-if="msg.role==='assistant' && !msg._writing" :text="msg.content" class="msg-voice-btn" />
              </div>
            </div>
            <div v-if="streaming" class="msg-item assistant">
              <div class="msg-avatar"><span class="char-icon">{{ currentChar.emoji }}</span></div>
              <div class="msg-content">
                <div class="msg-text streaming">{{ streamText }}<span class="cursor">|</span></div>
              </div>
            </div>
          </div>
          <div class="chat-input">
            <el-input v-model="inputMsg" type="textarea" :rows="3" :placeholder="currentChar.placeholder"
              @keyup.enter="sendMessage" :disabled="streaming" />
            <div class="input-actions">
              <VoiceInput @recognized="onVoiceRecognized" :disabled="streaming" />
              <el-button @click="toggleVoice" :type="voiceOn?'warning':''" circle>
                <el-icon><Microphone /></el-icon>
              </el-button>
              <el-button type="primary" @click="sendMessage" :loading="streaming" style="margin-left:8px">
                发送 <el-icon style="margin-left:4px"><Promotion /></el-icon>
              </el-button>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Delete, UserFilled, Microphone, Promotion } from '@element-plus/icons-vue'
import { agentChatStream } from '@/api/agent'
import { listSessions, createSession, loadHistory, deleteSession } from '@/api/memory'
import VoiceInput from '@/components/voice/VoiceInput.vue'
import VoiceOutput from '@/components/voice/VoiceOutput.vue'

const characters = [
  { key: 'bajie', name: '猪八戒', emoji: '🐷', initial: '猪', title: '天蓬元帅', novel: '西游记',
    quote: '散伙分行李！回高老庄找高小姐去！',
    desc: '前世乃天庭天蓬元帅，错投猪胎。贪吃贪睡爱偷懒，但关键时刻最讲义气。',
    style: '自称"俺老猪"，口头禅：哼哼～、你这呆子',
    placeholder: '跟俺老猪聊聊呗...',
    greeting: '嘿！俺老猪来也！你是来找俺唠嗑的，还是有啥正事要办？',
  },
  { key: 'luzhishen', name: '鲁智深', emoji: '🍺', initial: '鲁', title: '花和尚', novel: '水浒传',
    quote: '洒家今日便要倒拔这棵垂杨柳！',
    desc: '原名鲁达，渭州提辖出身，三拳打死镇关西后出家为僧。粗犷豪爽嗜酒如命。',
    style: '自称"洒家"，口头禅：直娘贼、来来来再饮三百杯',
    placeholder: '跟洒家聊聊...',
    greeting: '洒家鲁智深是也！刚从五台山下来，正愁没人喝酒聊天。你有啥事尽管说！',
  },
  { key: 'lindaiyu', name: '林黛玉', emoji: '🌸', initial: '黛', title: '潇湘妃子', novel: '红楼梦',
    quote: '我就知道，别人不挑剩下的也不给我。',
    desc: '贾母外孙女，居于大观园潇湘馆。才情冠绝群芳，敏感细腻，诗词信手拈来。',
    style: '自称"我"或"颦儿"，语气清冷文雅，爱用典故',
    placeholder: '与颦儿说说话吧...',
    greeting: '原是来了个说话的。我正觉得闷，这潇湘馆的竹子都看了八百遍了。',
  },
  { key: 'zhugeliang', name: '诸葛亮', emoji: '🎯', initial: '亮', title: '卧龙先生', novel: '三国演义',
    quote: '臣本布衣，躬耕于南阳，苟全性命于乱世。',
    desc: '蜀汉丞相，号卧龙。运筹帷幄决胜千里，鞠躬尽瘁死而后已。',
    style: '自称"亮"或"臣"，说话条理清晰，爱分析利弊',
    placeholder: '向孔明先生请教...',
    greeting: '亮躬耕南阳，蒙先主三顾之恩。阁下既来，必有要事相商，不妨直言。',
  },
]

const activeCharacter = ref('bajie')
const currentChar = computed(() => characters.find(c => c.key === activeCharacter.value))

const messages = ref([])
const inputMsg = ref('')
const streaming = ref(false)
const streamText = ref('')
const voiceOn = ref(false)
const msgContainer = ref(null)

// 会话状态
const sessions = ref([])
const currentSessionId = ref(null)

// 主动对话状态
const proactiveActive = ref(false)
const proactiveMsgIds = new Set()
let proactiveES = null
let proactiveRetry = 0

function charEmoji(key) {
  const c = characters.find(x => x.key === key)
  return c ? c.emoji : '💬'
}

function fmtTime(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  const now = new Date()
  const diff = now - d
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
  if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'
  return d.toLocaleDateString()
}

// 加载会话列表
async function loadSessions() {
  try {
    const res = await listSessions({ memory_type: 'chat', character: activeCharacter.value })
    sessions.value = res.data.data || []
  } catch (e) { /* ignore */ }
}

// 新建对话
async function newChat() {
  currentSessionId.value = null
  messages.value = [{
    role: 'assistant', content: currentChar.value.greeting,
    time: new Date().toLocaleTimeString(),
  }]
  streamText.value = ''
  streaming.value = false
}

// 打开历史会话
async function openSession(s) {
  currentSessionId.value = s.session_id
  try {
    const res = await loadHistory(s.session_id)
    const history = res.data.data || []
    if (history.length > 0) {
      messages.value = history.map(m => ({
        role: m.role, content: m.content,
        time: '',
      }))
    } else {
      messages.value = [{
        role: 'assistant', content: currentChar.value.greeting,
        time: new Date().toLocaleTimeString(),
      }]
    }
  } catch (e) {
    messages.value = [{
      role: 'assistant', content: currentChar.value.greeting,
      time: new Date().toLocaleTimeString(),
    }]
  }
}

// 删除会话
async function delSession(sid) {
  try {
    await deleteSession(sid)
    if (currentSessionId.value === sid) {
      newChat()
    }
    await loadSessions()
    ElMessage.success('已删除')
  } catch (e) { ElMessage.error('删除失败') }
}

// 切换角色 → 新建对话
function switchCharacter() {
  newChat()
  loadSessions()
}

// 发送消息
async function sendMessage() {
  const text = inputMsg.value.trim()
  if (!text || streaming.value) return

  messages.value.push({ role: 'user', content: text, time: new Date().toLocaleTimeString() })
  inputMsg.value = ''
  await scrollToBottom()

  const history = messages.value.slice(-20, -1).map(m => ({ role: m.role, content: m.content }))
  streaming.value = true
  streamText.value = ''

  await agentChatStream(text, history, {
    onIntent: () => {},
    onContent: (content) => { streamText.value += content; scrollToBottom() },
    onDone: () => {
      messages.value.push({ role: 'assistant', content: streamText.value, time: new Date().toLocaleTimeString() })
      streamText.value = ''; streaming.value = false
      loadSessions()
    },
    onError: () => {
      messages.value.push({ role: 'assistant', content: '抱歉，出了点问题。', time: new Date().toLocaleTimeString() })
      streamText.value = ''; streaming.value = false
    },
  }, activeCharacter.value, currentSessionId.value)
}

async function scrollToBottom() {
  await nextTick()
  const el = msgContainer.value
  if (el) el.scrollTop = el.scrollHeight
}

function onVoiceRecognized({ text }) {
  inputMsg.value = (inputMsg.value + ' ' + text).trim()
}

function toggleVoice() {
  if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
    ElMessage.warning('您的浏览器不支持语音识别'); return
  }
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  const r = new SpeechRecognition(); r.lang = 'zh-CN'; r.continuous = false; r.interimResults = false
  r.onstart = () => { voiceOn.value = true }
  r.onresult = (e) => { inputMsg.value = e.results[0][0].transcript; sendMessage() }
  r.onerror = () => { ElMessage.error('语音识别失败'); voiceOn.value = false }
  r.onend = () => { voiceOn.value = false }
  r.start()
}

// 主动对话 SSE
function connectProactive() {
  if (proactiveES) {
    proactiveES.close()
  }
  const token = localStorage.getItem('access_token')
  if (!token) return

  proactiveES = new EventSource(
    `/api/v1/memory/proactive-stream?character=${activeCharacter.value}`,
    { withCredentials: false }
  )
  // EventSource 不支持自定义 header，改用 fetch 方式...
  // 实际上 EventSource 不传 token，需要改用 fetch+ReadableStream
  proactiveES.close()
  connectProactiveFetch()
}

async function connectProactiveFetch() {
  const token = localStorage.getItem('access_token')
  if (!token) return

  try {
    const resp = await fetch(
      `/api/v1/memory/proactive-stream?character=${activeCharacter.value}`,
      { headers: { 'Authorization': `Bearer ${token}` } }
    )
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)

    proactiveActive.value = true
    proactiveRetry = 0
    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data:')) {
          try {
            const data = JSON.parse(line.slice(5).trim())
            if (data.type && data.content) {
              handleProactiveMsg(data)
            }
          } catch (e) { /* ignore */ }
        }
      }
    }
  } catch (e) {
    proactiveActive.value = false
    if (proactiveRetry < 3) {
      proactiveRetry++
      setTimeout(connectProactiveFetch, 5000)
    }
  }
}

function handleProactiveMsg(data) {
  const mid = data.type + data.content.slice(0, 20)
  if (proactiveMsgIds.has(mid)) return
  proactiveMsgIds.add(mid)
  if (proactiveMsgIds.size > 100) proactiveMsgIds.clear()

  // 1秒输入动画后展示消息
  const writingIndicator = { role: 'assistant', content: '...', time: new Date().toLocaleTimeString(), _writing: true }
  messages.value.push(writingIndicator)
  scrollToBottom()

  setTimeout(() => {
    messages.value = messages.value.filter(m => !m._writing)
    messages.value.push({
      role: 'assistant', content: data.content,
      time: new Date().toLocaleTimeString(),
      _proactive: true,
    })
    scrollToBottom()
  }, 1200)
}

function disconnectProactive() {
  proactiveActive.value = false
  if (proactiveES) {
    proactiveES.close()
    proactiveES = null
  }
}

onMounted(() => {
  loadSessions()
  newChat()
  connectProactiveFetch()
})

onUnmounted(() => {
  disconnectProactive()
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.bajie-chat { height: calc(100vh - 140px); }
.chat-layout { display: flex; gap: 12px; height: 100%; }

// ===== 左侧会话列表 =====
.session-sidebar {
  width: 220px; flex-shrink: 0; background: $rice-paper; border-radius: 10px;
  border: 1px solid $rice-paper-border; display: flex; flex-direction: column; overflow: hidden;
  .sidebar-header { padding: 12px; display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1px solid $rice-paper-border;
    .title { font-family: $font-family-title; font-size: 14px; color: $ink-black; letter-spacing: 2px; }
  }
  .session-list { flex: 1; overflow-y: auto; padding: 8px; }
  .empty-hint { text-align: center; color: $ink-disabled; font-size: 13px; padding: 30px 0; }
  .session-item { display: flex; align-items: center; padding: 10px; border-radius: 8px;
    cursor: pointer; margin-bottom: 4px; transition: all 0.2s;
    &:hover { background: rgba($gold, 0.08); }
    &.active { background: rgba($gold, 0.15); border-left: 3px solid $gold; }
    .s-emoji { font-size: 20px; margin-right: 8px; }
    .s-info { flex: 1; overflow: hidden;
      .s-title { font-size: 13px; color: $ink-black; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
      .s-meta { font-size: 11px; color: $ink-disabled; margin-top: 2px; }
    }
    .s-del { opacity: 0; transition: opacity 0.2s; }
    &:hover .s-del { opacity: 1; }
  }
}

// ===== 右侧聊天区 =====
.chat-main { flex: 1; display: flex; flex-direction: column; gap: 10px; overflow: hidden; }

.bajie-profile {
  flex-shrink: 0; border-radius: 10px; transition: all 0.4s ease;
  &.bajie { background: rgba(#C43B3B, 0.04); border-left: 4px solid #C43B3B; }
  &.luzhishen { background: rgba(#5D8A5D, 0.04); border-left: 4px solid #5D8A5D; }
  &.lindaiyu { background: rgba(#E8A0BF, 0.04); border-left: 4px solid #E8A0BF; }
  &.zhugeliang { background: rgba(#4A6B8A, 0.04); border-left: 4px solid #4A6B8A; }
}
.profile-avatar {
  width: 60px; height: 60px; border-radius: 50%; margin: 0 auto;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  animation: avatarPulse 3s ease-in-out infinite;
  &.bajie { background: radial-gradient(circle, rgba(#C43B3B, 0.15), rgba(#C43B3B, 0.05)); }
  &.luzhishen { background: radial-gradient(circle, rgba(#5D8A5D, 0.15), rgba(#5D8A5D, 0.05)); }
  &.lindaiyu { background: radial-gradient(circle, rgba(#E8A0BF, 0.15), rgba(#E8A0BF, 0.05)); }
  &.zhugeliang { background: radial-gradient(circle, rgba(#4A6B8A, 0.15), rgba(#4A6B8A, 0.05)); }
  .avatar-emoji { font-size: 26px; }
  .avatar-initial { font-size: 10px; color: #fff; padding: 1px 6px; border-radius: 8px; margin-top: 1px;
    .bajie & { background: #C43B3B; }
    .luzhishen & { background: #5D8A5D; }
    .lindaiyu & { background: #E8A0BF; }
    .zhugeliang & { background: #4A6B8A; }
  }
}
@keyframes avatarPulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.05); } }
.profile-intro {
  .profile-name { display: flex; align-items: center; gap: 8px; margin: 0 0 4px;
    .char-select { width: 190px;
      :deep(.el-input__wrapper) { background: transparent; box-shadow: none; font-size: 18px; font-weight: bold; font-family: $font-family-title; }
    }
    .el-tag { border: none; color: #fff;
      &.bajie { background: #C43B3B; } &.luzhishen { background: #5D8A5D; }
      &.lindaiyu { background: #E8A0BF; } &.zhugeliang { background: #4A6B8A; }
    }
  }
  .profile-desc { color: $ink-secondary; font-size: 12px; margin: 0 0 2px; line-height: 1.5; }
  .profile-style { color: $ink-disabled; font-size: 11px; margin: 0; }
}
.profile-quote { font-size: 13px; color: $ink-secondary; font-style: italic; text-align: right; padding-right: 8px; }

.chat-card { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.chat-messages { flex: 1; overflow-y: auto; padding: 16px; background: $rice-paper-light; border-radius: 8px; margin-bottom: 12px; border: 1px solid $rice-paper-border; }
.msg-item { display: flex; margin-bottom: 16px; align-items: flex-start;
  &.user { flex-direction: row-reverse;
    .msg-text { background: $vermilion; color: #fff; border-radius: 10px 10px 3px 10px; }
    .msg-time { text-align: right; }
  }
  &.assistant {
    .msg-text { background: $rice-paper; color: $ink-black; border-left: 3px solid $gold; border-radius: 10px 10px 10px 3px; }
  }
}
.msg-avatar { width: 40px; text-align: center; flex-shrink: 0;
  .el-icon { color: $mineral-blue; }
  .char-icon { font-size: 28px; }
}
.msg-content { max-width: 70%; margin: 0 12px; }
.msg-text { padding: 10px 14px; line-height: 1.6; white-space: pre-wrap; word-break: break-word; box-shadow: 0 1px 4px rgba(#1A1A1C, .08);
  &.proactive { border-left: 3px solid $gold; background: rgba($gold, 0.06); }
}
.proactive-tag { display: inline-block; font-size: 10px; color: $gold-dark; background: rgba($gold, 0.15);
  padding: 1px 6px; border-radius: 4px; margin-right: 6px; letter-spacing: 1px; }

.msg-time { font-size: 11px; color: $ink-disabled; margin-top: 4px; }
.streaming .msg-text { border: 1px dashed $gold-border; }
.cursor { color: $vermilion; animation: blink 1s infinite; }
@keyframes blink { 0%, 50% { opacity: 1; } 51%, 100% { opacity: 0; } }

.proactive-indicator { display: flex; align-items: center; gap: 6px; margin-bottom: 4px;
  .pi-dot { width: 8px; height: 8px; border-radius: 50%; background: #c0c4cc; transition: background 0.3s;
    &.active { background: #67c23a; box-shadow: 0 0 6px rgba(#67c23a, 0.4); }
  }
  .pi-text { font-size: 11px; color: $ink-disabled; }
}

.msg-voice-btn { margin-top: 2px; }

.chat-input { display: flex; gap: 8px; align-items: flex-end; }
.input-actions { display: flex; align-items: center; flex-shrink: 0; }
</style>
