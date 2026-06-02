/**
 * Axios 封装 - 统一请求拦截器和响应处理
 */
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建 Axios 实例
const request = axios.create({
  baseURL: '/api/v1',    // 通过 Vite proxy 转发到后端
  timeout: 30000,        // 30秒超时
})

// 请求拦截器: 自动附加 JWT Token
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器: 统一错误处理
request.interceptors.response.use(
  (response) => {
    const { code, message } = response.data
    // 业务层错误
    if (code !== 200 && code !== undefined) {
      ElMessage.error(message || '请求失败')
      return Promise.reject(new Error(message))
    }
    return response
  },
  (error) => {
    // HTTP错误处理
    if (error.response) {
      const { status, data } = error.response
      switch (status) {
        case 401:
          // 显示后端返回的实际错误信息，而非固定的"登录已过期"
          ElMessage.error(data?.message || '登录已过期，请重新登录')
          // 如果是Token过期而非登录失败，清除状态并跳转登录页
          if (data?.message && data.message !== '用户名或密码错误') {
            localStorage.clear()
            window.location.hash = '#/login'
          }
          break
        case 403:
          ElMessage.error('权限不足')
          break
        case 422:
          ElMessage.error(data?.data?.[0] || '参数校验失败')
          break
        default:
          ElMessage.error(data?.message || `服务器错误 (${status})`)
      }
    } else {
      ElMessage.error('网络连接失败，请检查网络')
    }
    return Promise.reject(error)
  }
)

export default request
