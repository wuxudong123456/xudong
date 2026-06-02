<!-- EmploymentList.vue - 就业管理页面 -->
<template>
  <div>
    <el-card class="search-card" shadow="never">
      <el-form inline>
        <el-form-item label="学号"><el-input v-model="search.student_no" placeholder="学号" clearable style="width:150px" /></el-form-item>
        <el-form-item label="班级"><el-select v-model="search.class_id" clearable placeholder="全部" style="width:160px">
            <el-option v-for="c in classOptions" :key="c.class_id" :label="c.class_name" :value="c.class_id" /></el-select></el-form-item>
        <el-form-item><el-button type="primary" @click="fetchData">搜索</el-button></el-form-item>
      </el-form>
    </el-card>
    <SmartQueryInput />
    <div class="action-bar">
      <el-button type="primary" v-if="authStore.hasPermission('employment:create')" @click="openAdd">
        <el-icon><Plus /></el-icon>新增就业</el-button>
      <el-button @click="showStats = !showStats" type="warning"><el-icon><DataAnalysis /></el-icon>就业统计</el-button>
    </div>
    <!-- 就业统计面板 -->
    <el-card v-if="showStats" class="stats-card" shadow="never">
      <el-table :data="statsData" border stripe>
        <el-table-column prop="class_name" label="班级" />
        <el-table-column prop="total_students" label="总人数" />
        <el-table-column prop="employed_count" label="已就业" />
        <el-table-column prop="employment_rate" label="就业率(%)" />
        <el-table-column prop="avg_salary" label="平均薪资(元)" />
      </el-table>
    </el-card>
    <el-card shadow="never">
      <el-table :data="tableData" v-loading="loading" stripe border>
        <el-table-column prop="student_no" label="学号" width="120" />
        <el-table-column prop="student_name" label="姓名" width="100" />
        <el-table-column prop="class_name" label="班级" width="140" />
        <el-table-column prop="company_name" label="就业单位" min-width="180" show-overflow-tooltip />
        <el-table-column prop="offer_job" label="offer岗位" width="140" />
        <el-table-column prop="salary" label="薪资(元)" width="110" />
        <el-table-column prop="offer_send_time" label="offer发放日" width="130" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openEdit(row)" v-if="authStore.hasPermission('employment:update')">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)" v-if="authStore.hasPermission('employment:delete')">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="page" v-model:page-size="size" :total="total"
        layout="total, prev, pager, next" @current-change="fetchData" style="margin-top:16px" />
    </el-card>
    <!-- 表单弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit?'编辑就业':'新增就业'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="学号" prop="student_no"><el-input v-model="form.student_no" /></el-form-item>
        <el-form-item label="就业单位" prop="company_name"><el-input v-model="form.company_name" /></el-form-item>
        <el-form-item label="offer岗位" prop="offer_job"><el-input v-model="form.offer_job" /></el-form-item>
        <el-form-item label="薪资"><el-input-number v-model="form.salary" :min="0" :step="1000" /></el-form-item>
        <el-form-item label="offer发放日"><el-date-picker v-model="form.offer_send_time" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
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
import { Plus, DataAnalysis } from '@element-plus/icons-vue'
import { useAuthStore } from '@/store/modules/auth'
import SmartQueryInput from '@/components/SmartQueryInput.vue'
import { getEmploymentList, createEmployment, updateEmployment, deleteEmployment, getEmploymentStats } from '@/api/employment'
import { getClassList } from '@/api/class'

const authStore = useAuthStore()
const search = reactive({ student_no: '', class_id: null })
const classOptions = ref([])
const tableData = ref([]); const loading = ref(false)
const page = ref(1); const size = ref(20); const total = ref(0)
const showStats = ref(false); const statsData = ref([])
const dialogVisible = ref(false); const isEdit = ref(false); const editId = ref(null)
const form = reactive({ student_no: '', company_name: '', offer_job: '', salary: null, offer_send_time: null })
const formRef = ref(null)
const rules = {
  student_no: [{ required: true, message: '请输入学号' }],
  company_name: [{ required: true, message: '请输入就业单位' }],
}

async function fetchData() {
  loading.value = true
  try {
    const res = await getEmploymentList({ ...search, page: page.value, size: size.value })
    const d = res.data.data; tableData.value = d.items; total.value = d.total
  } finally { loading.value = false }
}
async function loadOptions() {
  const res = await getClassList({ page: 1, size: 100 })
  classOptions.value = res.data.data.items
}
async function loadStats() {
  try { const res = await getEmploymentStats(); statsData.value = res.data.data.by_class } catch (e) { /* handled */ }
}
function openAdd() { isEdit.value = false; Object.assign(form, { student_no: '', company_name: '', offer_job: '', salary: null, offer_send_time: null }); dialogVisible.value = true }
function openEdit(row) { isEdit.value = true; editId.value = row.employment_id; Object.assign(form, row); dialogVisible.value = true }
async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  try {
    if (isEdit.value) { await updateEmployment(editId.value, form); ElMessage.success('编辑成功') }
    else { await createEmployment(form); ElMessage.success('新增成功') }
    dialogVisible.value = false; fetchData()
  } catch (e) { /* handled */ }
}
async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除该就业记录？`, '确认操作', { type: 'warning' })
  await deleteEmployment(row.employment_id); ElMessage.success('删除成功'); fetchData()
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
