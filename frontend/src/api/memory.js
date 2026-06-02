import request from './request'

export function listSessions(params) {
  return request.get('/memory/sessions', { params })
}
export function createSession(data) {
  return request.post('/memory/sessions', data)
}
export function loadHistory(sessionId, limit = 50) {
  return request.get(`/memory/sessions/${sessionId}`, { params: { limit } })
}
export function deleteSession(sessionId) {
  return request.delete(`/memory/sessions/${sessionId}`)
}
