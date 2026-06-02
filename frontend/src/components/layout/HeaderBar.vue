<!-- HeaderBar.vue - 顶部导航栏（折叠+面包屑+全屏+通知+用户） -->
<template>
  <div class="header-bar">
    <div class="header-left">
      <el-icon class="collapse-btn" @click="$emit('update:isCollapse', !isCollapse)">
        <Fold v-if="!isCollapse" /><Expand v-else />
      </el-icon>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item v-if="parentTitle" :to="parentPath">{{ parentTitle }}</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentTitle">{{ currentTitle }}</el-breadcrumb-item>
      </el-breadcrumb>
    </div>
    <div class="header-right">
      <el-tooltip :content="isFullscreen ? '退出全屏' : '全屏'" placement="bottom">
        <el-icon class="header-icon" @click="toggleFullscreen"><FullScreen v-if="!isFullscreen" /><Minus v-else /></el-icon>
      </el-tooltip>
      <el-tooltip content="暂无新通知" placement="bottom">
        <el-badge :value="0" :max="99" class="header-badge">
          <el-icon class="header-icon"><Bell /></el-icon>
        </el-badge>
      </el-tooltip>
      <el-dropdown trigger="click" @command="handleCommand">
        <span class="user-info">
          <el-avatar :size="32" :src="authStore.userInfo.avatar" style="border: 2px solid #C9A96E;" />
          <span class="username">{{ authStore.userInfo.real_name || authStore.userInfo.username }}</span>
          <el-icon><ArrowDown /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item><el-tag :type="roleTagType" size="small">{{ roleLabel }}</el-tag></el-dropdown-item>
            <el-dropdown-item command="profile">个人设置</el-dropdown-item>
            <el-dropdown-item command="changePassword">修改密码</el-dropdown-item>
            <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <el-dialog v-model="pwdDialogVisible" title="修改密码" width="400px">
      <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="80px">
        <el-form-item label="旧密码" prop="oldPassword">
          <el-input v-model="pwdForm.oldPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="pwdForm.newPassword" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleChangePassword">确认修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/modules/auth'
import { changePasswordApi } from '@/api/auth'
import { ElMessage } from 'element-plus'
import { Fold, Expand, ArrowDown, FullScreen, Minus, Bell } from '@element-plus/icons-vue'

defineProps({ isCollapse: Boolean })
defineEmits(['update:isCollapse'])

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const currentTitle = computed(() => route.meta.title || '')
const parentLabels = { students: '学生管理', classes: '班级管理', scores: '成绩管理', employment: '就业管理', courses: '课程管理', logs: '操作日志', bajie: '猪八戒 AI', system: '系统管理' }
const parentTitle = computed(() => { const p = route.path.split('/')[1]; return parentLabels[p] || '' })
const parentPath = computed(() => { const p = route.path.split('/'); return p.length > 2 ? '/' + p[1] : '/' })

const roleLabel = computed(() => ({ super_admin:'超级管理员',admin:'管理员',teacher:'教师',student:'学生' }[authStore.role]||authStore.role))
const roleTagType = computed(() => ({ super_admin:'danger',admin:'warning',teacher:'success',student:'info' }[authStore.role]||'info'))

const isFullscreen = ref(false)
function toggleFullscreen() {
  if (!document.fullscreenElement) { document.documentElement.requestFullscreen(); isFullscreen.value = true }
  else { document.exitFullscreen(); isFullscreen.value = false }
}

const pwdDialogVisible = ref(false)
const pwdFormRef = ref(null)
const pwdForm = reactive({ oldPassword: '', newPassword: '' })
const pwdRules = { oldPassword: [{ required: true, message: '请输入旧密码', trigger: 'blur' }], newPassword: [{ required: true, min: 6, message: '新密码至少6位', trigger: 'blur' }] }

async function handleChangePassword() {
  const valid = await pwdFormRef.value.validate().catch(() => false)
  if (!valid) return
  try {
    await changePasswordApi({ old_password: pwdForm.oldPassword, new_password: pwdForm.newPassword })
    ElMessage.success('密码修改成功, 请重新登录')
    authStore.logout(); router.push('/login')
  } catch (e) { /* handled */ }
}

function handleCommand(cmd) {
  if (cmd === 'logout') { authStore.logout(); router.push('/login'); ElMessage.success('已退出登录') }
  else if (cmd === 'changePassword') { pwdForm.oldPassword = ''; pwdForm.newPassword = ''; pwdDialogVisible.value = true }
  else if (cmd === 'profile') ElMessage.info('个人设置功能即将上线')
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';
.header-bar { display: flex; justify-content: space-between; align-items: center; width: 100%; }
.header-left { display: flex; align-items: center; gap: 14px; }
.header-right { display: flex; align-items: center; gap: 16px; }
.collapse-btn { font-size: 20px; cursor: pointer; color: $indigo; &:hover { color: $vermilion; } }
.header-icon { font-size: 20px; cursor: pointer; color: $ink-secondary; transition: color 0.2s; &:hover { color: $vermilion; } }
.header-badge :deep(.el-badge__content) { background: $vermilion; }
:deep(.el-breadcrumb__inner.is-link) { color: $indigo; font-weight: 500; &:hover { color: $vermilion; } }
:deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) { color: $vermilion; font-family: $font-family-title; }
.user-info { display: flex; align-items: center; gap: 8px; cursor: pointer; .username { font-size: 14px; color: $ink-black; } }
</style>
