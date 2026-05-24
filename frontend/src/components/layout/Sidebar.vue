<!--
  Sidebar.vue - 侧边导航菜单
  根据路由配置和用户权限动态显示菜单项
-->
<template>
  <div class="sidebar">
    <!-- Logo -->
    <div class="sidebar-logo">
      <img src="@/assets/images/logo.png" alt="logo" class="logo-img" />
      <span v-show="!isCollapse" class="logo-text">学生管理系统</span>
    </div>
    <!-- 导航菜单 -->
    <el-menu :default-active="activeMenu" class="sidebar-menu" background-color="#304156"
      text-color="#bfcbd9" active-text-color="#409EFF" :collapse="isCollapse" :collapse-transition="false"
      router>
      <!-- 仪表盘 -->
      <el-menu-item index="/dashboard">
        <el-icon><Monitor /></el-icon>
        <span>仪表盘</span>
      </el-menu-item>
      <!-- 学生管理 -->
      <el-menu-item index="/students" v-if="hasPerm('student:view')">
        <el-icon><User /></el-icon>
        <span>学生管理</span>
      </el-menu-item>
      <!-- 班级管理 -->
      <el-menu-item index="/classes" v-if="hasPerm('class:view')">
        <el-icon><School /></el-icon>
        <span>班级管理</span>
      </el-menu-item>
      <!-- 成绩管理 -->
      <el-menu-item index="/scores" v-if="hasPerm('score:view')">
        <el-icon><Tickets /></el-icon>
        <span>成绩管理</span>
      </el-menu-item>
      <!-- 就业管理 -->
      <el-menu-item index="/employment" v-if="hasPerm('employment:view')">
        <el-icon><Suitcase /></el-icon>
        <span>就业管理</span>
      </el-menu-item>
      <!-- 课程管理 -->
      <el-menu-item index="/courses" v-if="hasPerm('course:view')">
        <el-icon><Reading /></el-icon>
        <span>课程管理</span>
      </el-menu-item>
      <!-- 操作日志 -->
      <el-menu-item index="/logs" v-if="hasPerm('log:view')">
        <el-icon><Clock /></el-icon>
        <span>操作日志</span>
      </el-menu-item>
      <!-- 系统管理 -->
      <el-menu-item index="/system/users" v-if="hasPerm('user:manage')">
        <el-icon><Setting /></el-icon>
        <span>用户管理</span>
      </el-menu-item>
      <!-- 分隔 -->
      <el-divider style="border-color: #404a59; margin: 8px 0;" />
      <div class="menu-section-title" v-show="!isCollapse">猪八戒 AI</div>
      <!-- 八戒对话 -->
      <el-menu-item index="/bajie/chat">
        <el-icon><ChatDotRound /></el-icon>
        <span>八戒对话</span>
      </el-menu-item>
      <!-- 知识问答 -->
      <el-menu-item index="/bajie/qa">
        <el-icon><Collection /></el-icon>
        <span>知识问答</span>
      </el-menu-item>
      <!-- 八戒游戏 -->
      <el-menu-item index="/bajie/games">
        <el-icon><Trophy /></el-icon>
        <span>八戒游戏</span>
      </el-menu-item>
      <!-- 社交助手 -->
      <el-menu-item index="/bajie/social">
        <el-icon><Connection /></el-icon>
        <span>社交助手</span>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/store/modules/auth'
import { Monitor, User, School, Tickets, Suitcase, Reading, Clock, Setting, ChatDotRound, Collection, Trophy, Connection } from '@element-plus/icons-vue'

defineProps({ isCollapse: Boolean })

const route = useRoute()
const authStore = useAuthStore()

// 当前激活的菜单项
const activeMenu = computed(() => route.path)

// 权限检查
function hasPerm(code) {
  return authStore.hasPermission(code)
}
</script>

<style lang="scss" scoped>
.sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.sidebar-logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 16px;
  border-bottom: 1px solid #404a59;
}

.logo-img {
  width: 32px;
  height: 32px;
}

.logo-text {
  margin-left: 8px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
}

.sidebar-menu {
  border-right: none;
  flex: 1;
}

.menu-section-title {
  padding: 8px 20px;
  color: #7a80b4;
  font-size: 12px;
  letter-spacing: 2px;
}
</style>
