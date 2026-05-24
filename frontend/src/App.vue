<!--
  App.vue - 根组件
  根据路由显示登录页或主布局
-->
<template>
  <router-view />
</template>

<script setup>
// 根组件: 由路由决定显示 Login 或 AppLayout
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
}
#app {
  height: 100%;
}
</style>
