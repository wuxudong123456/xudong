<!--
  AppLayout.vue - 主布局组件
  包含侧边栏 + 顶部导航 + 主内容区
-->
<template>
  <el-container class="app-layout">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="app-sidebar">
      <Sidebar :is-collapse="isCollapse" />
    </el-aside>
    <!-- 右侧区域 -->
    <el-container>
      <!-- 顶部导航 -->
      <el-header class="app-header" height="60px">
        <HeaderBar v-model:is-collapse="isCollapse" />
      </el-header>
      <!-- 主内容区 -->
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import Sidebar from './Sidebar.vue'
import HeaderBar from './HeaderBar.vue'

const isCollapse = ref(false)
</script>

<style lang="scss" scoped>
.app-layout {
  height: 100vh;
}

.app-sidebar {
  background-color: #304156;
  transition: width 0.3s;
  overflow-x: hidden;
}

.app-header {
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  padding: 0 16px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.app-main {
  background: #f0f2f5;
  padding: 16px;
  overflow-y: auto;
}
</style>
