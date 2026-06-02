<!-- KnowledgeQA.vue - 四大名著知识问答页面（基于西游记/三国/红楼/水浒RAG + Neo4j图谱） -->
<template>
  <div class="knowledge-qa">
    <el-card class="qa-header" shadow="never">
      <el-row align="middle">
        <el-col :span="2" style="text-align:center">
          <span style="font-size:40px">📚</span>
        </el-col>
        <el-col :span="22">
          <h3 style="margin:0 0 4px">四大名著 · 知识问答</h3>
          <p style="color:#909399;font-size:13px;margin:0">
            基于《西游记》《三国演义》《红楼梦》《水浒传》全文的RAG智能问答系统。
            支持智能书籍路由、人物关系图谱、原文检索融合查询。
          </p>
          <p style="color:#909399;font-size:12px;margin:4px 0 0">
            试试问："曹操败走华容道是哪一回？"、"刘备和关羽是什么关系？"、"比较孙悟空和贾宝玉"
          </p>
        </el-col>
      </el-row>
      <!-- 向量库状态 -->
      <div class="collection-status" v-if="collectionInfo">
        <el-tag v-for="(info, key) in collectionInfo.collections" :key="key"
          size="small" :type="info.exists && info.num_entities > 0 ? 'success' : 'info'"
          style="margin-right:6px">
          {{ info.name_cn }}: {{ info.num_entities }}条
        </el-tag>
      </div>
    </el-card>

    <!-- 查询模式选择 -->
    <el-card shadow="never" style="margin-bottom: 12px;">
      <el-radio-group v-model="queryMode" size="small">
        <el-radio-button label="auto">自动模式</el-radio-button>
        <el-radio-button label="rag">原文检索</el-radio-button>
        <el-radio-button label="graph">人物关系</el-radio-button>
        <el-radio-button label="hybrid">融合查询</el-radio-button>
      </el-radio-group>
      <el-button size="small" style="margin-left: 12px;" @click="showGraph = true" type="success" plain>
        查看人物关系图谱
      </el-button>
    </el-card>

    <el-card shadow="never" class="qa-chat-card">
      <div class="qa-messages" ref="qaContainer">
        <div v-for="(qa, idx) in qaList" :key="idx" class="qa-item">
          <div class="qa-question">
            <span class="qa-label">Q</span>
            <span>{{ qa.question }}</span>
            <el-tag v-if="qa.mode" size="small" style="margin-left: 8px;" :type="modeTagType(qa.mode)">
              {{ modeText(qa.mode) }}
            </el-tag>
          </div>
          <div class="qa-answer">
            <span class="qa-label">A</span>
            <div>
              <div class="answer-text">{{ qa.answer }}</div>
              <!-- 引用出处（含名著来源） -->
              <div v-if="qa.references && qa.references.length" class="qa-sources">
                <el-divider content-position="left" style="margin:8px 0">引用出处</el-divider>
                <div v-for="(ref, ri) in qa.references" :key="ri" class="source-item">
                  <el-tag size="small" :type="novelTagType(ref.novel_name_cn)">{{ ref.novel_name_cn }}</el-tag>
                  <el-tag size="small" type="success" style="margin-left:4px">第{{ ref.chapter_num }}回</el-tag>
                  <span style="margin-left:6px;color:#606266;font-size:13px">{{ ref.content }}</span>
                  <span style="margin-left:4px;color:#909399;font-size:11px">相似度:{{ (ref.score*100).toFixed(1) }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-if="searching" class="qa-item">
          <div class="qa-question"><span class="qa-label">Q</span><span>{{ currentQuestion }}</span></div>
          <div class="qa-answer"><span class="qa-label">A</span><span class="searching-text">八戒正在翻阅四大名著查找中<span class="dots">...</span></span></div>
        </div>
      </div>
      <div class="qa-input">
        <el-input v-model="question" placeholder="向八戒提问关于四大名著的任何问题..." clearable
          @keyup.enter="askQuestion" :disabled="searching" size="large">
          <template #append>
            <el-button type="primary" @click="askQuestion" :loading="searching" icon="Search">提问</el-button>
          </template>
        </el-input>
        <!-- 推荐问题（覆盖四大名著） -->
        <div class="suggested-questions">
          <span style="font-size:12px;color:#909399;margin-right:8px">试试问：</span>
          <el-tag v-for="sq in suggestedQuestions" :key="sq" class="suggest-tag"
            @click="question=sq;askQuestion()" effect="plain">{{ sq }}</el-tag>
        </div>
      </div>
    </el-card>

    <!-- 人物关系图谱弹窗 -->
    <el-dialog v-model="showGraph" title="人物关系图谱" width="80%" destroy-on-close>
      <div style="margin-bottom: 16px;">
        <el-input v-model="graphSearchKeyword" placeholder="搜索人物..." style="width: 200px; margin-right: 8px;" />
        <el-button @click="searchGraphPerson" type="primary" size="small">搜索</el-button>
        <el-select v-model="selectedBook" placeholder="选择名著" style="width: 150px; margin-left: 8px;" @change="loadGraphData">
          <el-option label="全部" value="" />
          <el-option label="西游记" value="novel_xiyou" />
          <el-option label="三国演义" value="novel_sanguo" />
          <el-option label="水浒传" value="novel_shuihu" />
          <el-option label="红楼梦" value="novel_honglou" />
        </el-select>
      </div>
      <GraphView v-if="graphData.nodes.length" :data="graphData" />
      <el-empty v-else description="暂无图谱数据，请先导入人物关系" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import request from '@/api/request'
import GraphView from '@/components/GraphView.vue'
import { getGraphVisualization, searchPerson } from '@/api/graph'

const qaList = ref([])
const question = ref('')
const searching = ref(false)
const currentQuestion = ref('')
const qaContainer = ref(null)
const collectionInfo = ref(null)
const queryMode = ref('auto')
const showGraph = ref(false)
const graphData = ref({ nodes: [], links: [], categories: [] })
const graphSearchKeyword = ref('')
const selectedBook = ref('')

const suggestedQuestions = [
  '孙悟空大闹天宫是哪一回？',
  '曹操败走华容道在哪一回？',
  '林黛玉进贾府时的描写是什么？',
  '武松打虎是在《水浒传》第几回？',
  '猪八戒的九齿钉耙是谁打造的？',
  '诸葛亮草船借箭用了多少条船？',
  '鲁智深倒拔垂杨柳是怎么回事？',
  '贾宝玉梦游太虚幻境在哪一回？',
  '刘备和关羽是什么关系？',
  '比较孙悟空和贾宝玉的性格',
]

function novelTagType(name) {
  const map = { '西游记': 'warning', '三国演义': 'danger', '红楼梦': '', '水浒传': 'success' }
  return map[name] || 'info'
}

function modeTagType(mode) {
  const map = { auto: 'primary', rag: 'success', graph: 'warning', hybrid: 'danger' }
  return map[mode] || 'info'
}

function modeText(mode) {
  const map = { auto: '自动', rag: '原文', graph: '图谱', hybrid: '融合' }
  return map[mode] || mode
}

/** 加载向量库状态 */
async function loadCollectionInfo() {
  try {
    const res = await request.get('/rag/collection-info')
    collectionInfo.value = res.data.data
  } catch (e) { /* ignore */ }
}

/** 提问 */
async function askQuestion() {
  const q = question.value.trim()
  if (!q || searching.value) return
  currentQuestion.value = q; question.value = ''; searching.value = true
  await scrollToBottom()
  try {
    const res = await request.get('/rag/qa', {
      params: { question: q, top_k: 5, mode: queryMode.value }
    })
    const d = res.data.data
    qaList.value.push({
      question: q,
      answer: d.answer,
      references: d.references || [],
      mode: d.mode || 'rag',
    })
  } catch (e) {
    qaList.value.push({
      question: q,
      answer: '哼哼～俺老猪翻遍了四大名著也没找到答案...可能是向量库还没准备好。',
      references: [],
      mode: 'error',
    })
  }
  searching.value = false; currentQuestion.value = ''
  await scrollToBottom()
}

async function scrollToBottom() {
  await nextTick()
  const el = qaContainer.value
  if (el) el.scrollTop = el.scrollHeight
}

/** 加载图谱数据 */
async function loadGraphData() {
  try {
    const res = await getGraphVisualization({
      book: selectedBook.value || undefined,
    })
    if (res.data.code === 200) {
      graphData.value = res.data.data
    }
  } catch (e) {
    console.error('加载图谱失败', e)
  }
}

/** 搜索人物 */
async function searchGraphPerson() {
  if (!graphSearchKeyword.value) return
  try {
    const res = await searchPerson(graphSearchKeyword.value)
    if (res.data.code === 200 && res.data.data.length > 0) {
      // 以搜索到的人物为中心加载图谱
      const person = res.data.data[0]
      const graphRes = await getGraphVisualization({
        book: selectedBook.value || undefined,
        center: person.name,
      })
      if (graphRes.data.code === 200) {
        graphData.value = graphRes.data.data
      }
    }
  } catch (e) {
    console.error('搜索人物失败', e)
  }
}

onMounted(() => {
  loadCollectionInfo()
  loadGraphData()
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.knowledge-qa { height: calc(100vh - 140px); display: flex; flex-direction: column; gap: 12px; }
.qa-header { flex-shrink: 0; }
.collection-status { margin-top: 10px; padding-top: 8px; border-top: 1px solid $gold-border; }
.qa-chat-card { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.qa-messages { flex: 1; overflow-y: auto; padding: 16px; background: $rice-paper-light; border-radius: 8px; border: 1px solid $rice-paper-border; margin-bottom: 12px; }
.qa-item { margin-bottom: 20px; }
.qa-question, .qa-answer { display: flex; gap: 10px; align-items: flex-start; margin-bottom: 6px; }
.qa-label { display: inline-flex; width: 28px; height: 28px; border-radius: 50%; align-items: center; justify-content: center; font-weight: 700; font-size: 13px; color: #fff; flex-shrink: 0; }
.qa-question .qa-label { background: $indigo; }
.qa-answer .qa-label { background: $bamboo; }
.answer-text { line-height: 1.8; color: $ink-black; white-space: pre-wrap; }
.qa-sources {
  margin-top: 8px;
  background: $rice-paper;
  padding: 8px 12px;
  border-radius: $border-radius-base;
  border-left: 3px solid $gold;
}
.source-item { margin-bottom: 4px; }
.searching-text { color: $ink-secondary; }
.dots::after { content: ''; animation: dots 1.5s steps(3) infinite; }
@keyframes dots { 0% { content: '.'; } 33% { content: '..'; } 66% { content: '...'; } }

.qa-input { flex-shrink: 0; }
.suggested-questions { margin-top: 8px; display: flex; align-items: center; flex-wrap: wrap; gap: 6px; }
.suggest-tag {
  cursor: pointer;
  background: $rice-paper;
  border-color: $gold-border;
  &:hover { border-color: $vermilion; color: $vermilion; }
}

:deep(.el-radio-button__inner) {
  font-family: $font-family-title;
  letter-spacing: 1px;
}
</style>
