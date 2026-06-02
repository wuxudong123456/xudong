<!-- ScoreList.vue - 成绩管理页面 -->
<template>
  <div>
    <el-card class="search-card" shadow="never">
      <el-form inline>
        <el-form-item label="学号"><el-input v-model="search.student_no" placeholder="学号" clearable style="width:150px" /></el-form-item>
        <el-form-item label="班级"><el-select v-model="search.class_id" clearable placeholder="全部" style="width:160px">
            <el-option v-for="c in classOptions" :key="c.class_id" :label="c.class_name" :value="c.class_id" /></el-select></el-form-item>
        <el-form-item label="考试序次"><el-input-number v-model="search.exam_order" :min="1" placeholder="全部" /></el-form-item>
        <el-form-item><el-button type="primary" @click="fetchData">搜索</el-button></el-form-item>
      </el-form>
    </el-card>
    <SmartQueryInput />
    <div class="action-bar">
      <el-button type="primary" v-if="authStore.hasPermission('score:create')" @click="openAdd">
        <el-icon><Plus /></el-icon>录入成绩</el-button>
      <el-upload :show-file-list="false" accept=".xlsx,.xls" :http-request="handleImport" style="display:inline-block;margin-left:8px">
        <el-button type="success"><el-icon><Upload /></el-icon>批量导入</el-button>
      </el-upload>
      <el-button @click="handleExport"><el-icon><Download /></el-icon>导出</el-button>
      <el-button @click="showStats = !showStats" type="warning"><el-icon><DataAnalysis /></el-icon>成绩统计</el-button>
    </div>
    <!-- 成绩统计面板 -->
    <el-card v-if="showStats" class="stats-card" shadow="never">
      <el-descriptions :column="4" border>
        <el-descriptions-item label="平均分">{{ stats.avg_score }}</el-descriptions-item>
        <el-descriptions-item label="最高分">{{ stats.max_score }}</el-descriptions-item>
        <el-descriptions-item label="最低分">{{ stats.min_score }}</el-descriptions-item>
        <el-descriptions-item label="总记录">{{ stats.total_records }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
    <el-card shadow="never">
      <el-table :data="tableData" v-loading="loading" stripe border>
        <el-table-column prop="student_no" label="学号" width="120" />
        <el-table-column prop="student_name" label="姓名" width="100" />
        <el-table-column prop="class_name" label="班级" width="140" />
        <el-table-column prop="exam_order" label="考核序次" width="100" />
        <el-table-column prop="score" label="成绩" width="100" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openEdit(row)" v-if="authStore.hasPermission('score:update')">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)" v-if="authStore.hasPermission('score:delete')">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="page" v-model:page-size="size" :total="total"
        layout="total, prev, pager, next" @current-change="fetchData" style="margin-top:16px" />
    </el-card>
    <!-- 表单弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit?'编辑成绩':'录入成绩'" width="400px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="学号" prop="student_no"><el-input v-model="form.student_no" /></el-form-item>
        <el-form-item label="考核序次" prop="exam_order"><el-input-number v-model="form.exam_order" :min="1" /></el-form-item>
        <el-form-item label="成绩" prop="score"><el-input-number v-model="form.score" :min="0" :max="100" :precision="1" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="handleSubmit">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Download, DataAnalysis } from '@element-plus/icons-vue'
import { useAuthStore } from '@/store/modules/auth'
import SmartQueryInput from '@/components/SmartQueryInput.vue'
import { getScoreList, createScore, updateScore, deleteScore, importScores, exportScores, getScoreStats } from '@/api/score'
import { getClassList } from '@/api/class'

const authStore = useAuthStore()
const search = reactive({ student_no: '', class_id: null, exam_order: null })
const classOptions = ref([])
const tableData = ref([]); const loading = ref(false)
const page = ref(1); const size = ref(20); const total = ref(0)
const showStats = ref(false)
const stats = reactive({ avg_score: 0, max_score: 0, min_score: 0, total_records: 0 })
const dialogVisible = ref(false); const isEdit = ref(false); const editScoreId = ref(null)
const form = reactive({ student_no: '', exam_order: 1, score: 0 })
const formRef = ref(null)
const rules = {
  student_no: [{ required: true, message: '请输入学号' }],
  exam_order: [{ required: true, message: '请输入考核序次' }],
  score: [{ required: true, message: '请输入成绩' }],
}

async function fetchData() {
  loading.value = true
  try {
    const res = await getScoreList({ ...search, page: page.value, size: size.value })
    const d = res.data.data; tableData.value = d.items; total.value = d.total
  } finally { loading.value = false }
}
async function loadOptions() {
  const res = await getClassList({ page: 1, size: 100 })
  classOptions.value = res.data.data.items
}
function openAdd() { isEdit.value = false; Object.assign(form, { student_no: '', exam_order: 1, score: 0 }); dialogVisible.value = true }
function openEdit(row) { isEdit.value = true; editScoreId.value = row.id; Object.assign(form, row); dialogVisible.value = true }
async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  try {
    if (isEdit.value) { await updateScore(editScoreId.value, form); ElMessage.success('编辑成功') }
    else { await createScore(form); ElMessage.success('录入成功') }
    dialogVisible.value = false; fetchData()
  } catch (e) { /* handled */ }
}
async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除该成绩记录？`, '确认操作', { type: 'warning' })
  await deleteScore(row.id); ElMessage.success('删除成功'); fetchData()
}
async function handleImport({ file }) {
  const res = await importScores(file); ElMessage.success(res.data.message); fetchData()
}
async function handleExport() {
  const res = await exportScores()
  const blob = new Blob([res.data]); const url = URL.createObjectURL(blob)
  const a = document.createElement('a'); a.href = url; a.download = '成绩信息.xlsx'; a.click()
  URL.revokeObjectURL(url); ElMessage.success('导出成功')
}
async function loadStats() {
  try { const res = await getScoreStats(); Object.assign(stats, res.data.data) } catch (e) { /* handled */ }
}
onMounted(() => { loadOptions(); fetchData(); loadStats() })
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.search-card { margin-bottom: 16px; }
.action-bar { margin-bottom: 16px; display: flex; align-items: center; }
.stats-card { margin-bottom: 16px; }

:deep(.el-table) {
  border-radius: $border-radius-base;
  overflow: hidden;
}
</style>
