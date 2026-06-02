<!--
  StudentList.vue - 学生管理页面
  实现增删改查、批量导入删除、模糊检索、分页查询
-->
<template>
  <div class="student-list">
    <!-- 搜索栏 -->
    <el-card class="search-card" shadow="never">
      <el-form :model="searchForm" inline>
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="学号/姓名搜索" clearable style="width:200px"
            @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="班级">
          <el-select v-model="searchForm.class_id" placeholder="全部" clearable style="width:160px">
            <el-option v-for="c in classOptions" :key="c.class_id" :label="c.class_name" :value="c.class_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="学历">
          <el-select v-model="searchForm.education" placeholder="全部" clearable style="width:120px">
            <el-option label="本科" value="本科" />
            <el-option label="大专" value="大专" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 智能问数 -->
    <SmartQueryInput />
    <!-- 操作按钮 -->
    <div class="action-bar">
      <el-button type="primary" @click="openAdd" v-if="authStore.hasPermission('student:create')">
        <el-icon><Plus /></el-icon>新增学生
      </el-button>
      <el-upload :show-file-list="false" accept=".xlsx,.xls" :http-request="handleImport"
        v-if="authStore.hasPermission('student:import')" style="display:inline-block;margin-left:8px">
        <el-button type="success"><el-icon><Upload /></el-icon>导入Excel</el-button>
      </el-upload>
      <el-button @click="handleExport" v-if="authStore.hasPermission('student:export')">
        <el-icon><Download /></el-icon>导出Excel
      </el-button>
      <el-button type="danger" @click="handleBatchDelete" :disabled="selectedIds.length===0"
        v-if="authStore.hasPermission('student:delete')">
        <el-icon><Delete /></el-icon>批量删除
      </el-button>
    </div>

    <!-- 数据表格 -->
    <el-card shadow="never">
      <el-table :data="tableData" v-loading="loading" stripe border
        @selection-change="handleSelectionChange" style="width:100%">
        <el-table-column type="selection" width="45" />
        <el-table-column prop="student_no" label="学号" width="120" />
        <el-table-column prop="student_name" label="姓名" width="100" />
        <el-table-column prop="gender" label="性别" width="60" />
        <el-table-column prop="age" label="年龄" width="60" />
        <el-table-column prop="class_name" label="班级" width="140" />
        <el-table-column prop="education" label="学历" width="80" />
        <el-table-column prop="graduate_school" label="毕业院校" min-width="150" show-overflow-tooltip />
        <el-table-column prop="major" label="专业" width="120" show-overflow-tooltip />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openEdit(row)"
              v-if="authStore.hasPermission('student:update')">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)"
              v-if="authStore.hasPermission('student:delete')">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <!-- 分页 -->
      <el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.size"
        :total="pagination.total" :page-sizes="[10,20,50,100]" layout="total, sizes, prev, pager, next"
        @size-change="fetchData" @current-change="fetchData" style="margin-top:16px" />
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" @close="resetForm">
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="学号" prop="student_no">
              <el-input v-model="formData.student_no" placeholder="请输入学号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="姓名" prop="student_name">
              <el-input v-model="formData.student_name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别">
              <el-select v-model="formData.gender" placeholder="请选择">
                <el-option label="男" value="男" /><el-option label="女" value="女" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="年龄">
              <el-input-number v-model="formData.age" :min="10" :max="100" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="班级" prop="class_id">
              <el-select v-model="formData.class_id" placeholder="请选择班级">
                <el-option v-for="c in classOptions" :key="c.class_id" :label="c.class_name" :value="c.class_id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学历">
              <el-select v-model="formData.education" placeholder="请选择">
                <el-option label="本科" value="本科" /><el-option label="大专" value="大专" />
                <el-option label="硕士" value="硕士" /><el-option label="博士" value="博士" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="毕业院校">
              <el-input v-model="formData.graduate_school" placeholder="毕业院校" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="专业">
              <el-input v-model="formData.major" placeholder="专业" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="籍贯">
              <el-input v-model="formData.native_place" placeholder="籍贯" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="入学时间">
              <el-date-picker v-model="formData.admission_time" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确认</el-button>
      </template>
    </el-dialog>

    <!-- 删除确认弹窗 -->
    <el-dialog v-model="confirmVisible" title="确认操作" width="360px">
      <p>{{ confirmMessage }}</p>
      <template #footer>
        <el-button @click="confirmVisible = false">取消</el-button>
        <el-button type="danger" @click="doDelete">确认删除</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Download, Delete } from '@element-plus/icons-vue'
import { useAuthStore } from '@/store/modules/auth'
import SmartQueryInput from '@/components/SmartQueryInput.vue'
import { getStudentList, createStudent, updateStudent, deleteStudent, batchDeleteStudents, exportStudents, importStudents } from '@/api/student'
import { getClassList } from '@/api/class'

const authStore = useAuthStore()

// 搜索表单
const searchForm = reactive({ keyword: '', class_id: null, education: '' })
const classOptions = ref([])

// 表格数据
const tableData = ref([])
const loading = ref(false)
const selectedIds = ref([])
const pagination = reactive({ page: 1, size: 20, total: 0 })

// 表单弹窗
const dialogVisible = ref(false)
const dialogTitle = ref('新增学生')
const isEdit = ref(false)
const editId = ref(null)
const formRef = ref(null)
const formData = reactive({
  student_no: '', class_id: null, student_name: '', gender: '', age: null,
  native_place: '', graduate_school: '', major: '', education: '',
  admission_time: null, graduate_time: null, advisor_id: null, job_open_time: null,
})
const rules = {
  student_no: [{ required: true, message: '请输入学号', trigger: 'blur' }],
  student_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  class_id: [{ required: true, message: '请选择班级', trigger: 'change' }],
}

// 删除确认
const confirmVisible = ref(false)
const confirmMessage = ref('')
let deleteId = null
let deleteIds = null

// 加载班级选项
async function loadClassOptions() {
  const res = await getClassList({ page: 1, size: 100 })
  classOptions.value = res.data.data.items
}

// 加载表格数据
async function fetchData() {
  loading.value = true
  try {
    const res = await getStudentList({ ...searchForm, page: pagination.page, size: pagination.size })
    const d = res.data.data
    tableData.value = d.items
    pagination.total = d.total
  } finally { loading.value = false }
}

function handleSearch() { pagination.page = 1; fetchData() }
function handleReset() { Object.assign(searchForm, { keyword: '', class_id: null, education: '' }); handleSearch() }

function handleSelectionChange(rows) { selectedIds.value = rows.map(r => r.id) }

// 新增
function openAdd() {
  isEdit.value = false; dialogTitle.value = '新增学生'
  resetForm(); dialogVisible.value = true
}
// 编辑
function openEdit(row) {
  isEdit.value = true; dialogTitle.value = '编辑学生'
  editId.value = row.id
  Object.assign(formData, row)
  dialogVisible.value = true
}
function resetForm() {
  Object.assign(formData, {
    student_no: '', class_id: null, student_name: '', gender: '', age: null,
    native_place: '', graduate_school: '', major: '', education: '',
    admission_time: null, graduate_time: null, advisor_id: null, job_open_time: null,
  })
}

// 提交表单
async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  try {
    if (isEdit.value) {
      await updateStudent(editId.value, formData)
      ElMessage.success('编辑成功')
    } else {
      await createStudent(formData)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (e) { /* handled */ }
}

// 删除
function handleDelete(row) {
  deleteId = row.id; deleteIds = null
  confirmMessage.value = `确认删除学生 "${row.student_name}" (学号: ${row.student_no}) 吗？此操作为软删除，可恢复。`
  confirmVisible.value = true
}
function handleBatchDelete() {
  deleteId = null; deleteIds = [...selectedIds.value]
  confirmMessage.value = `确认批量删除 ${deleteIds.length} 条记录吗？`
  confirmVisible.value = true
}
async function doDelete() {
  try {
    if (deleteIds) {
      await batchDeleteStudents(deleteIds)
      ElMessage.success(`成功删除 ${deleteIds.length} 条记录`)
    } else {
      await deleteStudent(deleteId)
      ElMessage.success('删除成功')
    }
    confirmVisible.value = false
    fetchData()
  } catch (e) { /* handled */ }
}

// Excel操作
async function handleExport() {
  const res = await exportStudents({ class_id: searchForm.class_id || undefined })
  const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = '学生信息.xlsx'; a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('导出成功')
}
async function handleImport({ file }) {
  try {
    const res = await importStudents(file)
    ElMessage.success(res.data.message)
    fetchData()
  } catch (e) { /* handled */ }
}

onMounted(() => { loadClassOptions(); fetchData() })
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.search-card { margin-bottom: 16px; }
.action-bar { margin-bottom: 16px; display: flex; align-items: center; }

:deep(.el-table) {
  border-radius: $border-radius-base;
  overflow: hidden;
}
</style>
