<!-- SmartQueryInput.vue - 智能问数 + 查询历史 -->
<template>
  <div class="smart-query">
    <div class="sq-input-row">
      <el-input
        v-model="question" size="large"
        placeholder="智能问数：自然语言查询，如「各班级平均分排名」「成绩最高的学生」..."
        clearable @keyup.enter="doQuery" :disabled="loading"
        @focus="showHistory = true" @blur="hideHistory"
      >
        <template #prefix><el-icon color="#C9A96E" :size="20"><ChatDotRound /></el-icon></template>
        <template #append>
          <el-button type="warning" @click="doQuery" :loading="loading" :icon="Search">问八戒</el-button>
        </template>
      </el-input>
      <!-- 查询历史下拉 -->
      <div v-if="showHistory && queryHistory.length > 0" class="sq-history" @mousedown.prevent>
        <div class="sq-history-title">最近的查询</div>
        <div v-for="h in queryHistory" :key="h.id" class="sq-history-item" @click="reuseQuery(h.question)">
          <el-icon :size="14"><Clock /></el-icon>
          <span>{{ h.question }}</span>
          <span class="sq-history-time">{{ fmtTime(h.time) }}</span>
        </div>
      </div>
    </div>

    <transition name="el-fade-in">
      <div v-if="answer" class="sq-result">
        <el-alert type="success" :closable="true" show-icon @close="answer=''">
          <template #title><span style="font-size:15px">{{ answer }}</span></template>
        </el-alert>
        <div v-if="tableData.length > 0" class="sq-table" style="margin-top:12px">
          <el-table :data="tableData" border stripe size="small" max-height="300">
            <el-table-column v-for="col in columns" :key="col" :prop="col" :label="col" min-width="100" show-overflow-tooltip />
          </el-table>
          <p v-if="rowCount > tableData.length" style="text-align:center;color:#909399;margin-top:8px">
            仅显示前{{ tableData.length }}条，共{{ rowCount }}条结果
          </p>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ChatDotRound, Search, Clock } from '@element-plus/icons-vue'
import request from '@/api/request'

const question = ref('')
const loading = ref(false)
const answer = ref('')
const tableData = ref([])
const columns = ref([])
const rowCount = ref(0)
const showHistory = ref(false)
const queryHistory = ref([])

function fmtTime(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  const now = new Date()
  const diff = now - d
  if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
  if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'
  return d.toLocaleDateString()
}

function hideHistory() {
  setTimeout(() => { showHistory.value = false }, 200)
}

function reuseQuery(q) {
  question.value = q
  showHistory.value = false
  doQuery()
}

async function loadHistory() {
  try {
    const res = await request.get('/memory/query-history')
    queryHistory.value = res.data.data || []
  } catch (e) { /* ignore */ }
}

async function doQuery() {
  const q = question.value.trim()
  if (!q || loading.value) return
  loading.value = true
  answer.value = ''
  tableData.value = []
  try {
    const res = await request.post('/smart-query/', { question: q })
    const d = res.data.data
    answer.value = d.answer
    columns.value = d.columns || []
    tableData.value = d.data || []
    rowCount.value = d.row_count || 0
    loadHistory()
  } catch (e) {
    answer.value = '哎哟，脑子卡壳了...请稍后再试！'
  } finally {
    loading.value = false
  }
}

onMounted(loadHistory)
</script>

<style lang="scss" scoped>
.smart-query { margin-bottom: 16px; }
.sq-input-row { position: relative;
  :deep(.el-input__wrapper) {
    border: 2px solid rgba(#C9A96E, 0.35); border-radius: 8px;
    box-shadow: 0 2px 8px rgba(#C9A96E, 0.1);
    &:hover, &:focus-within { border-color: #C9A96E; box-shadow: 0 4px 16px rgba(#C9A96E, 0.18); }
  }
}
.sq-history {
  position: absolute; top: 100%; left: 0; right: 0; z-index: 1000;
  background: #fff; border: 1px solid #e4e7ed; border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1); max-height: 260px; overflow-y: auto;
  .sq-history-title { padding: 10px 14px; font-size: 12px; color: #909399; border-bottom: 1px solid #ebeef5; }
  .sq-history-item { display: flex; align-items: center; gap: 8px; padding: 10px 14px;
    cursor: pointer; font-size: 14px; color: #303133;
    &:hover { background: #f5f7fa; }
    .sq-history-time { margin-left: auto; font-size: 12px; color: #c0c4cc; }
  }
}
.sq-result { margin-top: 12px; }
.sq-table :deep(.el-table) { border-radius: 6px; overflow: hidden; }
</style>
