<!-- CourseList.vue - 课程管理页面 -->
<template>
  <div>
    <el-card class="search-card" shadow="never">
      <el-form inline>
        <el-form-item label="课程名称"><el-input v-model="keyword" placeholder="搜索课程" clearable style="width:200px" @keyup.enter="fetchData" /></el-form-item>
        <el-form-item><el-button type="primary" @click="fetchData">搜索</el-button></el-form-item>
      </el-form>
    </el-card>
    <SmartQueryInput />
    <div class="action-bar">
      <el-button type="primary" v-if="authStore.hasPermission('course:create')" @click="openAdd">
        <el-icon><Plus /></el-icon>新增课程</el-button>
    </div>
    <el-card shadow="never">
      <el-table :data="tableData" v-loading="loading" stripe border>
        <el-table-column prop="course_name" label="课程名称" min-width="150" />
        <el-table-column prop="course_code" label="课程代码" width="120" />
        <el-table-column prop="teacher_name" label="授课教师" width="100" />
        <el-table-column prop="class_name" label="班级" width="140" />
        <el-table-column prop="total_hours" label="总课时" width="80" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openEdit(row)" v-if="authStore.hasPermission('course:update')">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)" v-if="authStore.hasPermission('course:delete')">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="page" v-model:page-size="size" :total="total"
        layout="total, prev, pager, next" @current-change="fetchData" style="margin-top:16px" />
    </el-card>
    <!-- 表单弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit?'编辑课程':'新增课程'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="课程名称" prop="course_name"><el-input v-model="form.course_name" /></el-form-item>
        <el-form-item label="课程代码" prop="course_code"><el-input v-model="form.course_code" /></el-form-item>
        <el-form-item label="授课教师ID"><el-input-number v-model="form.teacher_id" :min="0" /></el-form-item>
        <el-form-item label="班级ID"><el-input-number v-model="form.class_id" :min="0" /></el-form-item>
        <el-form-item label="总课时"><el-input-number v-model="form.total_hours" :min="1" :max="999" /></el-form-item>
        <el-form-item label="课程描述"><el-input v-model="form.description" type="textarea" :rows="2" /></el-form-item>
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
import { Plus } from '@element-plus/icons-vue'
import { useAuthStore } from '@/store/modules/auth'
import SmartQueryInput from '@/components/SmartQueryInput.vue'
import { getCourseList, createCourse, updateCourse, deleteCourse } from '@/api/course'

const authStore = useAuthStore()
const keyword = ref('')
const tableData = ref([]); const loading = ref(false)
const page = ref(1); const size = ref(20); const total = ref(0)
const dialogVisible = ref(false); const isEdit = ref(false); const editId = ref(null)
const form = reactive({ course_name: '', course_code: '', teacher_id: null, class_id: null, total_hours: 40, description: '' })
const formRef = ref(null)
const rules = {
  course_name: [{ required: true, message: '请输入课程名称' }],
  course_code: [{ required: true, message: '请输入课程代码' }],
}

async function fetchData() {
  loading.value = true
  try {
    const res = await getCourseList({ page: page.value, size: size.value, keyword: keyword.value })
    const d = res.data.data; tableData.value = d.items; total.value = d.total
  } finally { loading.value = false }
}
function openAdd() { isEdit.value = false; Object.assign(form, { course_name: '', course_code: '', teacher_id: null, class_id: null, total_hours: 40, description: '' }); dialogVisible.value = true }
function openEdit(row) { isEdit.value = true; editId.value = row.course_id; Object.assign(form, row); dialogVisible.value = true }
async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  try {
    if (isEdit.value) { await updateCourse(editId.value, form); ElMessage.success('编辑成功') }
    else { await createCourse(form); ElMessage.success('新增成功') }
    dialogVisible.value = false; fetchData()
  } catch (e) { /* handled */ }
}
async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除课程 "${row.course_name}"？`, '确认操作', { type: 'warning' })
  await deleteCourse(row.course_id); ElMessage.success('删除成功'); fetchData()
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
