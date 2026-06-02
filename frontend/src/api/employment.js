import request from './request'

export function getEmploymentList(params) { return request.get('/employment/', { params }) }
export function createEmployment(data) { return request.post('/employment/', data) }
export function updateEmployment(id, data) { return request.put(`/employment/${id}`, data) }
export function deleteEmployment(id) { return request.delete(`/employment/${id}`) }
export function getEmploymentStats() { return request.get('/employment/stats') }
