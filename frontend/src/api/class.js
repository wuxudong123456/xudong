import request from './request'

export function getClassList(params) { return request.get('/classes/', { params }) }
export function getClassDetail(id) { return request.get(`/classes/${id}`) }
export function createClass(data) { return request.post('/classes/', data) }
export function updateClass(id, data) { return request.put(`/classes/${id}`, data) }
export function deleteClass(id) { return request.delete(`/classes/${id}`) }
