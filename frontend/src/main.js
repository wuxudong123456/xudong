/**
 * Vue3 应用入口
 * 初始化 Vue 实例、挂载路由、状态管理、UI组件库
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

import App from './App.vue'
import router from './router'
import './assets/styles/global.scss'

const app = createApp(App)

// Pinia 状态管理
const pinia = createPinia()
app.use(pinia)

// Vue Router 路由
app.use(router)

// Element Plus UI 组件库 (中文语言包)
app.use(ElementPlus, { locale: zhCn })

// 全局注册 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')
