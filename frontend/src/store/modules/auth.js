/**
 * 认证状态管理 (Pinia Store)
 * 存储用户登录状态、Token、权限信息
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { loginApi, getUserInfoApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  // --- 状态 ---
  const token = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('user_info') || '{}'))

  // --- 计算属性 ---
  const isLoggedIn = computed(() => !!token.value)
  const role = computed(() => userInfo.value.role || '')
  const permissions = computed(() => userInfo.value.permissions || [])

  // --- 方法 ---
  /**
   * 用户登录
   * @param {string} username 用户名 (如: super_admin / admin1 / teacher1 / student1)
   * @param {string} password 密码 (如: admin123 / 123456)
   */
  async function login(username, password) {
    const res = await loginApi({ username, password })
    const data = res.data.data
    token.value = data.access_token
    refreshToken.value = data.refresh_token
    userInfo.value = data.user_info
    // 持久化存储
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    localStorage.setItem('user_info', JSON.stringify(data.user_info))
    return data
  }

  /** 退出登录 */
  function logout() {
    token.value = ''
    refreshToken.value = ''
    userInfo.value = {}
    localStorage.clear()
  }

  /** 刷新用户信息 */
  async function fetchUserInfo() {
    const res = await getUserInfoApi()
    userInfo.value = res.data.data
    localStorage.setItem('user_info', JSON.stringify(res.data.data))
  }

  /** 检查是否拥有指定权限 */
  function hasPermission(permCode) {
    if (role.value === 'super_admin') return true // 超级管理员拥有所有权限
    return permissions.value.includes(permCode)
  }

  return { token, refreshToken, userInfo, isLoggedIn, role, permissions, login, logout, fetchUserInfo, hasPermission }
})
