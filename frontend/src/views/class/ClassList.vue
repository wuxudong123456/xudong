<!-- ClassList.vue - 班级管理页面 -->
<template>
  <div>
    <el-card class="search-card" shadow="never">
      <el-form inline>
        <el-form-item label="班级名称">
          <el-input v-model="keyword" placeholder="搜索班级" clearable style="width:200px" @keyup.enter="fetchData" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">搜索</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    <SmartQueryInput />
    <div class="action-bar">
      <el-button type="primary" @click="openAdd" v-if="authStore.hasPermission('class:create')">
        <el-icon><Plus /></el-icon>新增班级</el-button>
    </div>
    <el-card shadow="never">
      <el-table :data="tableData" v-loading="loading" stripe border>
        <el-table-column prop="class_id" label="ID" width="60" />
        <el-table-column prop="class_name" label="班级名称" />
        <el-table-column prop="student_count" label="学生人数" width="100" />
        <el-table-column prop="start_time" label="开课时间" width="120" />
        <el-table-column prop="close_time" label="闭班时间" width="120" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openEdit(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="page" v-model:page-size="size" :total="total"
        layout="total, prev, pager, next" @current-change="fetchData" style="margin-top:16px" />
    </el-card>
    <!-- 表单弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑班级' : '新增班级'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="班级名称" prop="class_name">
          <el-input v-model="form.class_name" placeholder="如: Java开发一班" /></el-form-item>
        <el-form-item label="开课时间"><el-date-picker v-model="form.start_time" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="闭班时间"><el-date-picker v-model="form.close_time" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="班主任ID"><el-input-number v-model="form.head_teacher_id" :min="0" /></el-form-item>
        <el-form-item label="授课老师ID"><el-input-number v-model="form.lecturer_id" :min="0" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useAuthStore } from '@/store/modules/auth'
import SmartQueryInput from '@/components/SmartQueryInput.vue'
import { getClassList, createClass, updateClass, deleteClass } from '@/api/class'

const authStore = useAuthStore()
const keyword = ref('')
const tableData = ref([])
const loading = ref(false)
const page = ref(1); const size = ref(20); const total = ref(0)
const dialogVisible = ref(false); const isEdit = ref(false); const editClassId = ref(null)
const form = reactive({ class_name: '', start_time: null, close_time: null, head_teacher_id: null, lecturer_id: null })
const formRef = ref(null)
const rules = { class_name: [{ required: true, message: '请输入班级名称' }] }

async function fetchData() {
  loading.value = true
  try {
    const res = await getClassList({ page: page.value, size: size.value, keyword: keyword.value })
    const d = res.data.data; tableData.value = d.items; total.value = d.total
  } finally { loading.value = false }
}
function openAdd() { isEdit.value = false; Object.assign(form, { class_name: '', start_time: null, close_time: null, head_teacher_id: null, lecturer_id: null }); dialogVisible.value = true }
function openEdit(row) { isEdit.value = true; editClassId.value = row.class_id; Object.assign(form, row); dialogVisible.value = true }
async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  try {
    if (isEdit.value) { await updateClass(editClassId.value, form); ElMessage.success('编辑成功') }
    else { await createClass(form); ElMessage.success('新增成功') }
    dialogVisible.value = false; fetchData()
  } catch (e) { /* handled */ }
}
async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除班级 "${row.class_name}"？`, '确认操作', { type: 'warning' })
  await deleteClass(row.class_id)
  ElMessage.success('删除成功'); fetchData()
}
onMounted(fetchData)
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.search-card { margin-bottom: 16px; }
.action-bar { margin-bottom: 16px; }

:deep(.el-table) {
  border-radius: $border-radius-base;
  overflow: hidden;
}
</style>
