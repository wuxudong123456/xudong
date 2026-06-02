<!-- BajieGames.vue - 八戒游戏（LLM猜灯谜 + 飞花令单字接龙 + 成语接龙） -->
<template>
  <div class="bajie-games">
    <el-tabs v-model="activeTab" type="border-card" class="game-tabs">
      <!-- ===== 猜灯谜 ===== -->
      <el-tab-pane name="riddle">
        <template #label><span><el-icon><Trophy /></el-icon> 猜灯谜</span></template>
        <el-card shadow="never" class="game-card">
          <div class="game-content">
            <div class="topic-select">
              <span class="label">选择主题：</span>
              <el-radio-group v-model="riddleTopic" size="small">
                <el-radio-button value="四大名著">四大名著</el-radio-button>
                <el-radio-button value="成语">成语</el-radio-button>
                <el-radio-button value="日常物品">日常物品</el-radio-button>
                <el-radio-button value="动物">动物</el-radio-button>
                <el-radio-button value="自然现象">自然现象</el-radio-button>
              </el-radio-group>
              <el-tag type="warning" style="margin-left:12px">积分: {{ riddleScore }}</el-tag>
            </div>
            <div v-if="currentRiddle" class="riddle-box">
              <div class="riddle-icon">🏮</div>
              <p class="riddle-text">"{{ currentRiddle.text }}"</p>
              <div class="riddle-meta">
                <el-tag size="small" :type="diffType(currentRiddle.difficulty)">{{ currentRiddle.difficulty }}</el-tag>
                <el-tag size="small" type="info" style="margin-left:8px">{{ currentRiddle.category }}</el-tag>
                <span v-if="currentRiddle.hint" class="hint-text">💡 {{ currentRiddle.hint }}</span>
              </div>
              <div class="riddle-answer-area">
                <el-input v-model="guess" placeholder="输入你的答案..." @keyup.enter="submitGuess" :disabled="riddleDone" size="large">
                  <template #append><el-button @click="submitGuess" :disabled="riddleDone">猜!</el-button></template>
                </el-input>
              </div>
              <div v-if="riddleFeedback" class="feedback" :class="feedbackType">{{ riddleFeedback }}</div>
              <div v-if="riddleDone" class="answer-reveal">
                <el-alert :title="`谜底：${currentRiddle.answer}`" type="success" :closable="false" show-icon />
              </div>
            </div>
            <div v-else class="empty-game">
              <p>🏮</p><p>点击下方按钮开始猜灯谜</p>
              <el-button type="warning" @click="getNewRiddle" :loading="riddleLoading" size="large">哼哼～俺来出题!</el-button>
            </div>
          </div>
          <div class="game-actions" v-if="currentRiddle">
            <el-button @click="getNewRiddle" :loading="riddleLoading">换一题</el-button>
          </div>
        </el-card>
      </el-tab-pane>

      <!-- ===== 飞花令 ===== -->
      <el-tab-pane name="feihua">
        <template #label><span><el-icon><EditPen /></el-icon> 飞花令</span></template>
        <el-card shadow="never" class="game-card">
          <div class="game-content">
            <div class="topic-select">
              <span class="label">指定字（可选）：</span>
              <el-radio-group v-model="fhKeyword" size="small">
                <el-radio-button value="">随机</el-radio-button>
                <el-radio-button value="花">花</el-radio-button>
                <el-radio-button value="月">月</el-radio-button>
                <el-radio-button value="风">风</el-radio-button>
                <el-radio-button value="云">云</el-radio-button>
                <el-radio-button value="山">山</el-radio-button>
                <el-radio-button value="水">水</el-radio-button>
                <el-radio-button value="春">春</el-radio-button>
                <el-radio-button value="雪">雪</el-radio-button>
              </el-radio-group>
            </div>
            <div v-if="fhCurrent" class="poetry-box">
              <div class="feihua-keyword">关键字：<span class="kw">「{{ fhCurrent.keyword }}」</span></div>
              <p class="feihua-hint">{{ fhCurrent.hint }}</p>
              <p v-if="fhCurrent.example" class="feihua-example">例：{{ fhCurrent.example }}</p>
              <div class="poetry-answer-area">
                <el-input v-model="fhAnswer" placeholder="说一句含有该字的古诗词..." @keyup.enter="submitFeihua" size="large" :disabled="fhDone">
                  <template #append><el-button @click="submitFeihua" :disabled="fhDone">对!</el-button></template>
                </el-input>
              </div>
              <div v-if="fhFeedback" class="feedback" :class="fhFeedbackType">{{ fhFeedback }}</div>
            </div>
            <div v-else class="empty-game">
              <p>🌸</p><p>飞花令 · 单字接龙</p>
              <el-button type="primary" @click="startFeihuaGame" size="large">开始飞花令!</el-button>
            </div>
          </div>
          <div class="game-actions" v-if="fhCurrent">
            <el-button @click="startFeihuaGame">换一字</el-button>
          </div>
        </el-card>
      </el-tab-pane>

      <!-- ===== 成语接龙 ===== -->
      <el-tab-pane name="chengyu">
        <template #label><span><el-icon><ChatLineSquare /></el-icon> 成语接龙</span></template>
        <el-card shadow="never" class="game-card">
          <div class="game-content">
            <div v-if="cyStarted" class="chengyu-box">
              <div class="cy-chain">
                <el-tag v-for="(w, i) in cyHistory" :key="i" :type="i % 2 === 0 ? '' : 'warning'" size="large" class="cy-tag">
                  {{ w }}<template v-if="i % 2 === 0">（八戒）</template><template v-else>（你）</template>
                </el-tag>
              </div>
              <div class="cy-current">
                <p>当前尾字：<span class="kw">「{{ cyLastChar }}」</span></p>
                <p class="cy-hint">请说一个以「{{ cyLastChar }}」开头的成语</p>
              </div>
              <div class="poetry-answer-area">
                <el-input v-model="cyAnswer" placeholder="输入成语..." @keyup.enter="submitChengyu" size="large" :disabled="cyGameOver">
                  <template #append><el-button @click="submitChengyu" :disabled="cyGameOver">接!</el-button></template>
                </el-input>
              </div>
              <div v-if="cyFeedback" class="feedback" :class="cyFeedbackType">{{ cyFeedback }}</div>
              <div v-if="cyGameOver" class="game-over">
                <el-result icon="success" title="游戏结束" :sub-title="cyResultMsg">
                  <template #extra><el-button type="primary" @click="restartChengyu">再来一局</el-button></template>
                </el-result>
              </div>
            </div>
            <div v-else class="empty-game">
              <p>📝</p><p>成语接龙 · 与八戒对战</p>
              <el-button type="success" @click="restartChengyu" size="large">开始接龙!</el-button>
            </div>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Trophy, EditPen, ChatLineSquare } from '@element-plus/icons-vue'
import { getRiddle, checkRiddle, getRiddleLLM, checkRiddleLLM, startFeihualing, checkFeihualing, startChengyu, checkChengyu } from '@/api/bajie'
import request from '@/api/request'

async function saveGameRecord(gameType, content, correct) {
  try {
    await request.post('/memory/sessions', { character: gameType, memory_type: 'game' })
  } catch (e) { /* ignore */ }
}

const activeTab = ref('riddle')

// ===== 猜灯谜 =====
const riddleTopic = ref('四大名著')
const currentRiddle = ref(null)
const guess = ref('')
const riddleDone = ref(false)
const riddleFeedback = ref('')
const feedbackType = ref('')
const riddleScore = ref(0)
const riddleLoading = ref(false)
const totalGuesses = ref(0)
const correctGuesses = ref(0)

// 加载历史得分
import { listSessions } from '@/api/memory'
async function loadGameStats() {
  try {
    const res = await listSessions({ memory_type: 'game', character: 'riddle' })
    const sessions = res.data.data || []
    let total = 0, correct = 0
    for (const s of sessions) {
      total += s.msg_count || 0
      // 简单估算：每条消息算一次猜测
    }
  } catch (e) { /* ignore */ }
}

function diffType(d) {
  const map = { '简单': 'success', '中等': 'warning', '困难': 'danger' }
  return map[d] || 'info'
}

async function getNewRiddle() {
  riddleLoading.value = true
  try {
    const res = await getRiddleLLM(riddleTopic.value)
    currentRiddle.value = res.data.data
    // 不显示答案
    guess.value = ''
    riddleDone.value = false
    riddleFeedback.value = ''
  } catch (e) {
    // 回退到内置灯谜
    try {
      const res = await getRiddle()
      currentRiddle.value = res.data.data
      guess.value = ''
      riddleDone.value = false
      riddleFeedback.value = ''
    } catch (e2) {
      ElMessage.error('获取灯谜失败')
    }
  } finally { riddleLoading.value = false }
}

async function submitGuess() {
  if (!guess.value.trim() || riddleDone.value) return
  try {
    const res = await checkRiddleLLM({
      riddle_text: currentRiddle.value.text,
      answer: guess.value.trim(),
      correct_answer: currentRiddle.value.answer,
    })
    const result = res.data.data
    currentRiddle.value.answer = result.answer || currentRiddle.value.answer
    riddleDone.value = true
    riddleFeedback.value = result.message
    feedbackType.value = result.correct ? 'success' : 'error'
    riddleScore.value += result.score_change || 0
    // 自动存档
    saveGameRecord('riddle', currentRiddle.value.text, result.correct)
  } catch (e) {
    // 回退到内置校验
    try {
      const res = await checkRiddle({
        riddle_text: currentRiddle.value.text,
        answer: guess.value.trim(),
      })
      const result = res.data.data
      currentRiddle.value.answer = result.answer
      riddleDone.value = true
      riddleFeedback.value = result.message
      feedbackType.value = result.correct ? 'success' : 'error'
      riddleScore.value += result.score_change || 0
      saveGameRecord('riddle', currentRiddle.value.text, result.correct)
    } catch (e2) {
      ElMessage.error('提交答案失败')
    }
  }
}

// ===== 飞花令 =====
const fhKeyword = ref('')
const fhCurrent = ref(null)
const fhAnswer = ref('')
const fhDone = ref(false)
const fhFeedback = ref('')
const fhFeedbackType = ref('')

async function startFeihuaGame() {
  try {
    const res = await startFeihualing({ keyword: fhKeyword.value || undefined })
    fhCurrent.value = res.data.data
    fhAnswer.value = ''
    fhDone.value = false
    fhFeedback.value = ''
  } catch (e) {
    ElMessage.error('启动飞花令失败')
  }
}

async function submitFeihua() {
  if (!fhAnswer.value.trim() || fhDone.value) return
  try {
    const res = await checkFeihualing({
      keyword: fhCurrent.value.keyword,
      answer: fhAnswer.value.trim(),
    })
    const result = res.data.data
    fhDone.value = result.correct
    fhFeedback.value = result.message
    fhFeedbackType.value = result.correct ? 'success' : 'error'
  } catch (e) {
    ElMessage.error('提交答案失败')
  }
}

// ===== 成语接龙 =====
const cyStarted = ref(false)
const cyHistory = ref([])
const cyLastChar = ref('')
const cyAnswer = ref('')
const cyFeedback = ref('')
const cyFeedbackType = ref('')
const cyGameOver = ref(false)
const cyResultMsg = ref('')

async function restartChengyu() {
  try {
    const res = await startChengyu({})
    const data = res.data.data
    cyStarted.value = true
    cyHistory.value = data.history
    cyLastChar.value = data.last_char
    cyAnswer.value = ''
    cyFeedback.value = ''
    cyGameOver.value = false
  } catch (e) {
    ElMessage.error('启动成语接龙失败')
  }
}

async function submitChengyu() {
  if (!cyAnswer.value.trim() || cyGameOver.value) return
  try {
    const res = await checkChengyu({
      prev_last_char: cyLastChar.value,
      answer: cyAnswer.value.trim(),
      history: cyHistory.value,
    })
    const data = res.data.data
    const userResult = data.user
    cyFeedback.value = userResult.message
    cyFeedbackType.value = userResult.correct ? 'success' : 'error'

    if (userResult.correct) {
      cyHistory.value = data.history
      // 八戒回复
      if (data.bot.word) {
        cyLastChar.value = data.bot.next_char
        cyFeedback.value = data.bot.message
        cyFeedbackType.value = 'success'
      } else {
        // 八戒接不上了，游戏结束
        cyGameOver.value = true
        cyResultMsg.value = data.bot.message
        cyFeedback.value = data.bot.message
        cyFeedbackType.value = 'warning'
      }
      cyAnswer.value = ''
    }
  } catch (e) {
    ElMessage.error('提交答案失败')
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.bajie-games { height: calc(100vh - 140px); }
.game-tabs { height: 100%;
  :deep(.el-tabs__content) { height: calc(100% - 40px); overflow-y: auto; padding: 16px; }
}
.game-card { height: 100%; }
.game-content { text-align: center; padding: 16px 0; }
.empty-game { text-align: center; padding: 60px 0; font-size: 40px; p { color: $ink-secondary; font-size: 14px; margin: 8px 0; } }

.topic-select { margin-bottom: 20px;
  .label { color: $ink-secondary; margin-right: 8px; font-size: 14px; }
}

.riddle-box, .poetry-box, .chengyu-box { padding: 20px 0; }
.riddle-icon { font-size: 48px; filter: drop-shadow(0 0 12px rgba($vermilion, 0.4)); }
.riddle-text { font-size: 20px; font-family: $font-family-title; line-height: 1.8; color: $ink-black; margin: 16px 0; }
.riddle-meta { margin-bottom: 16px; .hint-text { margin-left: 10px; color: $ink-disabled; font-size: 13px; } }
.riddle-answer-area, .poetry-answer-area, .cy-answer-area { width: 70%; margin: 0 auto; }

.feihua-keyword { font-size: 18px; margin-bottom: 12px; .kw { color: $vermilion; font-weight: bold; font-size: 24px; } }
.feihua-hint { color: $ink-secondary; font-size: 15px; margin-bottom: 8px; }
.feihua-example { color: $ink-disabled; font-size: 13px; font-style: italic; margin-bottom: 16px; }

.cy-chain { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-bottom: 20px; }
.cy-tag { font-size: 15px; padding: 6px 14px; }
.cy-current { margin-bottom: 16px; .kw { color: $vermilion; font-size: 22px; font-weight: bold; } .cy-hint { color: $ink-secondary; font-size: 14px; } }

.feedback { margin-top: 16px; font-size: 15px; padding: 8px; border-radius: 6px;
  &.success { color: $bamboo; background: $bamboo-bg; }
  &.error { color: $vermilion-dark; background: $vermilion-bg; }
  &.warning { color: $gold-dark; background: rgba($gold-light, 0.2); }
}
.game-actions { margin-top: 16px; text-align: center; }
.answer-reveal { margin-top: 16px; }
.game-over { margin-top: 24px; }
</style>