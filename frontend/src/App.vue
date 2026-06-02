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
  font-family: 'Microsoft YaHei', 'PingFang SC', -apple-system, sans-serif;
  background-color: #FAF0DC;
  color: #1A1A1C;
}
#app {
  height: 100%;
}
</style>
