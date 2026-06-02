<!-- Sidebar.vue - 侧边导航菜单（权限控制 + 底栏用户区） -->
<template>
  <div class="sidebar">
    <!-- Logo 区域 -->
    <div class="sidebar-logo">
      <el-icon :size="32" color="#C9A96E"><School /></el-icon>
      <div v-show="!isCollapse" class="logo-text-group">
        <span class="logo-text">学生管理系统</span>
        <span class="logo-sub">猪八戒智能平台</span>
      </div>
    </div>

    <!-- 导航菜单 -->
    <el-menu :default-active="activeMenu" class="sidebar-menu"
      background-color="#1B2A4A" text-color="#F5E6C8" active-text-color="#C9A96E"
      :collapse="isCollapse" :collapse-transition="false" router>

      <el-menu-item index="/dashboard">
        <el-icon><Monitor /></el-icon>
        <span>仪表盘</span>
      </el-menu-item>
      <el-menu-item index="/students" v-if="hasPerm('student:view')">
        <el-icon><User /></el-icon>
        <span>学生管理</span>
      </el-menu-item>
      <el-menu-item index="/classes" v-if="hasPerm('class:view')">
        <el-icon><School /></el-icon>
        <span>班级管理</span>
      </el-menu-item>
      <el-menu-item index="/scores" v-if="hasPerm('score:view')">
        <el-icon><Tickets /></el-icon>
        <span>成绩管理</span>
      </el-menu-item>
      <el-menu-item index="/employment" v-if="hasPerm('employment:view')">
        <el-icon><Suitcase /></el-icon>
        <span>就业管理</span>
      </el-menu-item>
      <el-menu-item index="/courses" v-if="hasPerm('course:view')">
        <el-icon><Reading /></el-icon>
        <span>课程管理</span>
      </el-menu-item>
      <el-menu-item index="/logs" v-if="hasPerm('log:view')">
        <el-icon><Clock /></el-icon>
        <span>操作日志</span>
      </el-menu-item>
      <el-menu-item index="/system/users" v-if="hasPerm('user:manage')">
        <el-icon><Setting /></el-icon>
        <span>用户管理</span>
      </el-menu-item>

      <el-divider style="border-color: rgba(201,169,110,0.25); margin: 8px 0;" />
      <div class="menu-section-title" v-show="!isCollapse">猪八戒 AI</div>

      <el-menu-item index="/bajie/chat">
        <el-icon><ChatDotRound /></el-icon>
        <span>八戒对话</span>
      </el-menu-item>
      <el-menu-item index="/bajie/qa">
        <el-icon><Collection /></el-icon>
        <span>知识问答</span>
      </el-menu-item>
      <el-menu-item index="/bajie/games">
        <el-icon><Trophy /></el-icon>
        <span>八戒游戏</span>
      </el-menu-item>
      <el-menu-item index="/bajie/social">
        <el-icon><Connection /></el-icon>
        <span>社交助手</span>
      </el-menu-item>
    </el-menu>

    <!-- 底部用户区 -->
    <div class="sidebar-footer" v-show="!isCollapse">
      <el-avatar :size="36" :src="authStore.userInfo.avatar"
        style="border: 2px solid #C9A96E; flex-shrink: 0;" />
      <div class="footer-user">
        <div class="footer-name">{{ authStore.userInfo.real_name || authStore.userInfo.username }}</div>
        <div class="footer-role">{{ roleLabel }}</div>
      </div>
      <el-icon class="footer-logout" @click="handleLogout" title="退出登录"><SwitchButton /></el-icon>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/modules/auth'
import { ElMessage } from 'element-plus'
import { Monitor, User, School, Tickets, Suitcase, Reading, Clock, Setting, ChatDotRound, Collection, Trophy, Connection, SwitchButton } from '@element-plus/icons-vue'

defineProps({ isCollapse: Boolean })

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const activeMenu = computed(() => route.path)

const roleLabel = computed(() => {
  const map = { super_admin: '超级管理员', admin: '管理员', teacher: '教师', student: '学生' }
  return map[authStore.role] || authStore.role
})

function hasPerm(code) { return authStore.hasPermission(code) }
function handleLogout() {
  authStore.logout()
  router.push('/login')
  ElMessage.success('已退出登录')
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.sidebar { height: 100%; display: flex; flex-direction: column; }

.sidebar-logo {
  height: 60px; display: flex; align-items: center; justify-content: center;
  padding: 0 16px; border-bottom: 1px solid rgba($gold, 0.25);
  .logo-text-group { margin-left: 10px; display: flex; flex-direction: column; }
  .logo-text { color: $rice-paper; font-size: 17px; font-family: $font-family-title; letter-spacing: 3px; font-weight: 600; white-space: nowrap; line-height: 1.3; }
  .logo-sub { color: $lotus-light; font-size: 10px; letter-spacing: 2px; }
}

.sidebar-menu { border-right: none; flex: 1; overflow-y: auto; overflow-x: hidden;
  &::-webkit-scrollbar { width: 3px; }
  &::-webkit-scrollbar-thumb { background: rgba($gold, 0.3); border-radius: 3px; }
}

:deep(.el-menu-item) {
  font-family: $font-family-base; letter-spacing: 1px; transition: all 0.25s ease;
  position: relative;
  &::before {
    content: ''; position: absolute; left: 0; top: 8px; bottom: 8px; width: 3px;
    background: $gold; opacity: 0; transition: opacity 0.25s;
  }
  &:hover {
    background-color: $indigo-hover !important;
    &::before { opacity: 1; }
  }
  &.is-active {
    border-left: 3px solid $vermilion !important;
    background-color: rgba($vermilion, 0.12) !important;
    &::before { opacity: 0; }
  }
}

.menu-section-title {
  padding: 8px 20px; color: $lotus-light; font-size: 12px;
  font-family: $font-family-title; letter-spacing: 3px;
}

// 底部用户区
.sidebar-footer {
  display: flex; align-items: center; gap: 8px; padding: 12px 16px;
  border-top: 1px solid rgba($gold, 0.2); background: rgba(0,0,0,0.15);
  .footer-user { flex: 1; overflow: hidden;
    .footer-name { color: $rice-paper; font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .footer-role { color: $lotus-light; font-size: 11px; }
  }
  .footer-logout { color: $lotus-light; font-size: 18px; cursor: pointer;
    &:hover { color: $vermilion; } }
}
</style>
