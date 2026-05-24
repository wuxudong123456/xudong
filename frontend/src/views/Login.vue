<!--
  Login.vue - 登录页面
  支持超级管理员/管理员/教师/学生不同角色登录
-->
<template>
  <div class="login-container">
    <div class="login-card">
      <h2 class="login-title">学生管理系统</h2>
      <p class="login-subtitle">猪八戒多智能体 AI 平台</p>
      <el-form ref="formRef" :model="form" :rules="rules" size="large">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" :prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码"
            :prefix-icon="Lock" show-password @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" class="login-btn" @click="handleLogin">
            登 录
          </el-button>
        </el-form-item>
      </el-form>
      <!-- 预置账号提示 -->
      <el-alert title="预置账号(点击复制)" type="info" :closable="false" show-icon>
        <div class="account-list">
          <el-tag v-for="acc in presetAccounts" :key="acc.role" class="account-tag"
            @click="fillAccount(acc)" type="info">
            {{ acc.role }}: {{ acc.username }} / {{ acc.password }}
          </el-tag>
        </div>
      </el-alert>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/store/modules/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

// 预置账号列表
const presetAccounts = [
  { role: '超级管理员', username: 'super_admin', password: 'admin123' },
  { role: '管理员', username: 'admin1', password: '123456' },
  { role: '教师', username: 'teacher1', password: '123456' },
  { role: '学生', username: 'student1', password: '123456' },
]

/** 点击预置账号自动填充 */
function fillAccount(acc) {
  form.username = acc.username
  form.password = acc.password
  ElMessage.success(`已选择 ${acc.role} 账号`)
}

/** 登录处理 */
async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await authStore.login(form.username, form.password)
    ElMessage.success('登录成功!')
    // 登录后跳转到来源页或仪表盘
    router.push(route.query.redirect || '/dashboard')
  } catch (e) {
    // 错误已在请求拦截器处理
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 420px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.login-title {
  text-align: center;
  margin: 0 0 8px;
  font-size: 24px;
  color: #303133;
}

.login-subtitle {
  text-align: center;
  margin: 0 0 32px;
  color: #909399;
  font-size: 14px;
}

.login-btn {
  width: 100%;
}

.account-list {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.account-tag {
  cursor: pointer;
  font-size: 12px;
}
</style>
