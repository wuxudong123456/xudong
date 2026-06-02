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
@import '@/assets/styles/variables.scss';

.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  // 水墨山水背景
  background:
    // 远山层叠
    radial-gradient(ellipse 120% 40% at 50% 100%, rgba($indigo-dark, 0.5) 0%, transparent 70%),
    radial-gradient(ellipse 100% 30% at 20% 90%, rgba($indigo, 0.3) 0%, transparent 65%),
    radial-gradient(ellipse 90% 25% at 80% 92%, rgba($indigo-dark, 0.35) 0%, transparent 60%),
    // 圆月
    radial-gradient(circle 60px at 78% 22%, rgba($gold-light, 0.25) 0%, transparent 100%),
    // 基础宣纸渐变
    linear-gradient(180deg, $rice-paper-light 0%, $rice-paper 40%, $rice-paper-dark 100%);
  position: relative;
  overflow: hidden;

  // 山形剪影
  &::before {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 45%;
    background: $indigo-dark;
    clip-path: polygon(
      0% 80%, 5% 55%, 12% 60%, 18% 40%, 24% 50%, 28% 35%, 34% 45%,
      40% 30%, 45% 38%, 50% 25%, 55% 35%, 60% 28%, 65% 40%,
      70% 32%, 75% 42%, 82% 30%, 88% 48%, 93% 38%, 100% 55%,
      100% 100%, 0% 100%
    );
    opacity: 0.7;
    z-index: 0;
  }

  // 近山
  &::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 25%;
    background: darken($indigo-dark, 5%);
    clip-path: polygon(
      0% 90%, 10% 65%, 22% 75%, 30% 55%, 40% 65%, 48% 50%,
      58% 60%, 66% 48%, 75% 58%, 85% 50%, 92% 62%, 100% 55%,
      100% 100%, 0% 100%
    );
    z-index: 0;
  }
}

.login-card {
  width: 420px;
  padding: 48px 40px 36px;
  background: $rice-paper;
  border: $border-width-base solid $rice-paper-border;
  border-radius: $border-radius-lg;
  box-shadow: 0 8px 40px rgba(#1A1A1C, 0.18);
  position: relative;
  z-index: 2;
  // 顶部装饰金边
  border-top: 4px solid $gold-border;
}

.login-title {
  text-align: center;
  margin: 0 0 8px;
  font-size: 26px;
  font-family: $font-family-title;
  color: $ink-black;
  letter-spacing: 6px;
  // 标题下方装饰线
  &::after {
    content: '';
    display: block;
    width: 40px;
    height: 2px;
    background: $gold;
    margin: 12px auto 0;
  }
}

.login-subtitle {
  text-align: center;
  margin: 0 0 36px;
  color: $ink-secondary;
  font-size: 14px;
  font-family: $font-family-classic;
  letter-spacing: 2px;
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 18px;
  font-family: $font-family-title;
  letter-spacing: 8px;
  box-shadow: 0 3px 0 rgba(#1A1A1C, 0.2);
  transition: all 0.2s;
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 0 rgba(#1A1A1C, 0.25);
  }
}

:deep(.el-input__wrapper) {
  background: lighten($rice-paper, 5%);
  box-shadow: 0 0 0 1px $rice-paper-border inset;
  transition: all 0.25s;
}
:deep(.el-input.is-focus .el-input__wrapper) {
  box-shadow: 0 0 0 1px $vermilion inset !important;
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

:deep(.el-alert) {
  background: $lotus-bg;
  border-color: $lotus;
  border-radius: $border-radius-base;
}
</style>
