/**
 * Vue Router 路由配置
 * 定义所有页面路由，含权限守卫
 */
import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuthStore } from '@/store/modules/auth'

const routes = [
  // 登录页 (无需认证)
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', noAuth: true },
  },
  // 主布局 (需认证)
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    redirect: '/dashboard',
    children: [
      // 数据看板
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表盘', icon: 'Monitor' },
      },
      // 学生管理
      {
        path: 'students',
        name: 'StudentList',
        component: () => import('@/views/student/StudentList.vue'),
        meta: { title: '学生管理', icon: 'User', perm: 'student:view' },
      },
      // 班级管理
      {
        path: 'classes',
        name: 'ClassList',
        component: () => import('@/views/class/ClassList.vue'),
        meta: { title: '班级管理', icon: 'School', perm: 'class:view' },
      },
      // 成绩管理
      {
        path: 'scores',
        name: 'ScoreList',
        component: () => import('@/views/score/ScoreList.vue'),
        meta: { title: '成绩管理', icon: 'Tickets', perm: 'score:view' },
      },
      // 就业管理
      {
        path: 'employment',
        name: 'EmploymentList',
        component: () => import('@/views/employment/EmploymentList.vue'),
        meta: { title: '就业管理', icon: 'Suitcase', perm: 'employment:view' },
      },
      // 课程管理
      {
        path: 'courses',
        name: 'CourseList',
        component: () => import('@/views/course/CourseList.vue'),
        meta: { title: '课程管理', icon: 'Reading', perm: 'course:view' },
      },
      // 操作日志
      {
        path: 'logs',
        name: 'OperationLogs',
        component: () => import('@/views/logs/OperationLogs.vue'),
        meta: { title: '操作日志', icon: 'Clock', perm: 'log:view' },
      },
      // 系统管理
      {
        path: 'system/users',
        name: 'UserManage',
        component: () => import('@/views/system/UserManage.vue'),
        meta: { title: '用户管理', icon: 'Setting', perm: 'user:manage' },
      },
      // ===== 猪八戒多智能体模块 =====
      {
        path: 'bajie/chat',
        name: 'BajieChat',
        component: () => import('@/views/bajie/BajieChat.vue'),
        meta: { title: '八戒对话', icon: 'ChatDotRound' },
      },
      {
        path: 'bajie/qa',
        name: 'KnowledgeQA',
        component: () => import('@/views/bajie/KnowledgeQA.vue'),
        meta: { title: '知识问答', icon: 'Collection' },
      },
      {
        path: 'bajie/games',
        name: 'BajieGames',
        component: () => import('@/views/bajie/BajieGames.vue'),
        meta: { title: '八戒游戏', icon: 'Trophy' },
      },
      {
        path: 'bajie/social',
        name: 'SocialAssistant',
        component: () => import('@/views/bajie/SocialAssistant.vue'),
        meta: { title: '社交助手', icon: 'Connection' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

// 全局路由守卫: 检查认证状态
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 学生管理系统` : '学生管理系统'

  // 无需认证的页面直接放行
  if (to.meta.noAuth) {
    return next()
  }
  // 检查是否已登录
  if (!authStore.token) {
    return next({ name: 'Login', query: { redirect: to.fullPath } })
  }
  next()
})

export default router
