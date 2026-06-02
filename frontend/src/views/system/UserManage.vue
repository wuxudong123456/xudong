<!-- UserManage.vue - 用户管理页面（仅超级管理员和管理员可见） -->
<template>
  <div>
    <el-card class="search-card" shadow="never">
      <el-form inline>
        <el-form-item label="关键词"><el-input v-model="keyword" placeholder="用户名/姓名搜索" clearable style="width:200px" @keyup.enter="fetchData" /></el-form-item>
        <el-form-item label="角色">
          <el-select v-model="filterRole" clearable placeholder="全部" style="width:140px">
            <el-option label="超级管理员" value="super_admin" />
            <el-option label="管理员" value="admin" />
            <el-option label="教师" value="teacher" />
            <el-option label="学生" value="student" />
          </el-select>
        </el-form-item>
        <el-form-item><el-button type="primary" @click="fetchData">搜索</el-button></el-form-item>
      </el-form>
    </el-card>
    <div class="action-bar">
      <el-button type="primary" v-if="authStore.role === 'super_admin'" @click="openAdd">
        <el-icon><Plus /></el-icon>新增用户</el-button>
    </div>
    <el-card shadow="never">
      <el-table :data="tableData" v-loading="loading" stripe border>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="real_name" label="姓名" width="100" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="roleTagType(row.role)" size="small">{{ roleLabel(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" width="180" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="status" label="状态" width="70">
          <template #default="{ row }">
            <el-tag :type="row.status===1?'success':'danger'" size="small">{{ row.status===1?'启用':'禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_login_time" label="最后登录" width="180" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openEdit(row)">编辑</el-button>
            <el-button type="warning" link size="small" @click="openResetPwd(row)" v-if="authStore.role==='super_admin'">重置密码</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)" v-if="authStore.role==='super_admin'&&row.role!=='super_admin'">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="page" v-model:page-size="size" :total="total"
        layout="total, prev, pager, next" @current-change="fetchData" style="margin-top:16px" />
    </el-card>
    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit?'编辑用户':'新增用户'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="用户名" prop="username"><el-input v-model="form.username" :disabled="isEdit" /></el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit"><el-input v-model="form.password" type="password" show-password /></el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" :disabled="isEdit&&form.role==='super_admin'">
            <el-option label="管理员" value="admin" />
            <el-option label="教师" value="teacher" />
            <el-option label="学生" value="student" />
          </el-select>
        </el-form-item>
        <el-form-item label="姓名"><el-input v-model="form.real_name" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
        <el-form-item label="手机号"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="状态" v-if="isEdit">
          <el-switch v-model="form.status" :active-value="1" :inactive-value="0" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="handleSubmit">确认</el-button>
      </template>
    </el-dialog>
    <!-- 重置密码弹窗 -->
    <el-dialog v-model="pwdVisible" title="重置密码" width="400px">
      <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="90px">
        <el-form-item label="新密码" prop="new_password"><el-input v-model="pwdForm.new_password" type="password" show-password /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdVisible=false">取消</el-button><el-button type="primary" @click="doResetPwd">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useAuthStore } from '@/store/modules/auth'
import { getUserList, createUser, updateUser, resetUserPassword, deleteUser } from '@/api/user'

const authStore = useAuthStore()
const keyword = ref(''); const filterRole = ref('')
const tableData = ref([]); const loading = ref(false)
const page = ref(1); const size = ref(20); const total = ref(0)

// 新增/编辑
const dialogVisible = ref(false); const isEdit = ref(false); const editUserId = ref(null)
const form = reactive({ username: '', password: '', role: 'student', real_name: '', email: '', phone: '', status: 1 })
const formRef = ref(null)
const rules = {
  username: [{ required: true, message: '请输入用户名' }],
  password: [{ required: true, message: '请输入密码' }],
  role: [{ required: true, message: '请选择角色' }],
}

// 重置密码
const pwdVisible = ref(false); const resetUserId = ref(null)
const pwdForm = reactive({ new_password: '' })
const pwdFormRef = ref(null)
const pwdRules = { new_password: [{ required: true, message: '请输入新密码' }] }

function roleLabel(role) {
  const map = { super_admin: '超级管理员', admin: '管理员', teacher: '教师', student: '学生' }
  return map[role] || role
}
function roleTagType(role) {
  const map = { super_admin: 'danger', admin: 'warning', teacher: 'success', student: '' }
  return map[role] || ''
}

async function fetchData() {
  loading.value = true
  try {
    const res = await getUserList({ page: page.value, size: size.value, keyword: keyword.value, role: filterRole.value || undefined })
    const d = res.data.data; tableData.value = d.items; total.value = d.total
  } finally { loading.value = false }
}
function openAdd() {
  isEdit.value = false
  Object.assign(form, { username: '', password: '', role: 'student', real_name: '', email: '', phone: '', status: 1 })
  dialogVisible.value = true
}
function openEdit(row) {
  isEdit.value = true; editUserId.value = row.id
  Object.assign(form, { username: row.username, role: row.role, real_name: row.real_name, email: row.email, phone: row.phone, status: row.status })
  dialogVisible.value = true
}
async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  try {
    if (isEdit.value) {
      await updateUser(editUserId.value, { real_name: form.real_name, email: form.email, phone: form.phone, role: form.role, status: form.status })
      ElMessage.success('编辑成功')
    } else {
      await createUser({ username: form.username, password: form.password, role: form.role, real_name: form.real_name, email: form.email, phone: form.phone })
      ElMessage.success('新增用户成功')
    }
    dialogVisible.value = false; fetchData()
  } catch (e) { /* handled */ }
}
function openResetPwd(row) {
  resetUserId.value = row.id; pwdForm.new_password = ''; pwdVisible.value = true
}
async function doResetPwd() {
  const valid = await pwdFormRef.value.validate().catch(() => false)
  if (!valid) return
  await resetUserPassword(resetUserId.value, { new_password: pwdForm.new_password })
  ElMessage.success('密码重置成功'); pwdVisible.value = false
}
async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除用户 "${row.username}"？`, '确认操作', { type: 'warning' })
  await deleteUser(row.id); ElMessage.success('删除成功'); fetchData()
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
