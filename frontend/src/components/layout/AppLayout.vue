<!-- AppLayout.vue - 主布局：侧边栏 + 顶部栏 + TabBar + 内容区 -->
<template>
  <el-container class="app-layout">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="app-sidebar">
      <Sidebar :is-collapse="isCollapse" />
    </el-aside>
    <el-container>
      <el-header class="app-header" height="60px">
        <HeaderBar v-model:is-collapse="isCollapse" />
      </el-header>
      <!-- TabBar -->
      <div class="app-tabbar">
        <div class="tabbar-scroll">
          <div v-for="tab in tabs" :key="tab.path"
            :class="['tab-item', { active: tab.path === activeTab }]"
            @click="switchTab(tab)" @contextmenu.prevent="closeTab(tab)">
            <span class="tab-title">{{ tab.title }}</span>
            <el-icon v-if="tabs.length > 1" class="tab-close" @click.stop="closeTab(tab)"><Close /></el-icon>
          </div>
        </div>
      </div>
      <el-main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Close } from '@element-plus/icons-vue'
import Sidebar from './Sidebar.vue'
import HeaderBar from './HeaderBar.vue'

const route = useRoute()
const router = useRouter()
const isCollapse = ref(false)

const tabs = ref([])
const activeTab = ref('/dashboard')

watch(() => route.path, (path) => {
  if (path === '/' || path === '/login') return
  activeTab.value = path
  if (!tabs.value.find(t => t.path === path)) {
    tabs.value.push({ path, title: route.meta?.title || path, query: route.query })
  }
}, { immediate: true })

function switchTab(tab) {
  activeTab.value = tab.path
  router.push({ path: tab.path, query: tab.query })
}
function closeTab(tab) {
  const idx = tabs.value.findIndex(t => t.path === tab.path)
  if (idx < 0) return
  tabs.value.splice(idx, 1)
  if (tab.path === activeTab.value && tabs.value.length) {
    const next = tabs.value[idx] || tabs.value[idx - 1]
    if (next) switchTab(next)
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.app-layout { height: 100vh; }
.app-sidebar { background-color: $indigo-dark; transition: width 0.3s; overflow-x: hidden; }

.app-header {
  @include plaque-header;
  display: flex; align-items: center; padding: 0 20px;
  box-shadow: 0 2px 6px rgba(#1A1A1C, 0.06);
  border-bottom: 1px solid $gold-border;
}

.app-tabbar {
  height: 40px; background: $rice-paper;
  border-bottom: 1px solid $rice-paper-border;
  display: flex; align-items: stretch; overflow: hidden;
}
.tabbar-scroll {
  display: flex; align-items: stretch; overflow-x: auto; flex: 1;
  &::-webkit-scrollbar { height: 2px; }
}
.tab-item {
  display: flex; align-items: center; gap: 6px; padding: 0 14px;
  font-size: 13px; color: $ink-secondary; cursor: pointer;
  border-right: 1px solid $rice-paper-border; white-space: nowrap; transition: all 0.2s;
  &:hover { background: rgba($gold, 0.08); color: $ink-black; }
  &.active {
    color: $vermilion; background: $rice-paper-light;
    &::after { content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 2px; background: $vermilion; }
  }
  .tab-title { font-family: $font-family-title; letter-spacing: 1px; }
  .tab-close { font-size: 12px; border-radius: 50%; padding: 2px;
    &:hover { background: rgba($vermilion, 0.12); color: $vermilion; } }
}

.app-main { background: $rice-paper-light; padding: 20px; overflow-y: auto; }

.fade-slide-enter-active, .fade-slide-leave-active { transition: all 0.25s ease; }
.fade-slide-enter-from { opacity: 0; transform: translateX(12px); }
.fade-slide-leave-to { opacity: 0; transform: translateX(-12px); }
</style>
