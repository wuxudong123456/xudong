import request from './request'

export function getScoreList(params) { return request.get('/scores/', { params }) }
export function createScore(data) { return request.post('/scores/', data) }
export function updateScore(id, data) { return request.put(`/scores/${id}`, data) }
export function deleteScore(id) { return request.delete(`/scores/${id}`) }
export function importScores(file) {
  const fd = new FormData(); fd.append('file', file)
  return request.post('/scores/import', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
}
export function exportScores(params) { return request.get('/scores/export', { params, responseType: 'blob' }) }
export function getScoreStats(params) { return request.get('/scores/stats', { params }) }
export function getScoreRankings(params) { return request.get('/scores/rankings', { params }) }
