/**
 * 认证相关 API
 */
import request from './request'

/** 登录 */
export function loginApi(data) {
  return request.post('/auth/login', data)
}

/** 刷新Token */
export function refreshTokenApi(data) {
  return request.post('/auth/refresh', data)
}

/** 获取当前用户信息 */
export function getUserInfoApi() {
  return request.get('/auth/me')
}

/** 修改密码 */
export function changePasswordApi(data) {
  return request.put('/auth/me/password', data)
}
