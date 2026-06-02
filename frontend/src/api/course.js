import request from './request'

export function getCourseList(params) { return request.get('/courses/', { params }) }
export function createCourse(data) { return request.post('/courses/', data) }
export function updateCourse(id, data) { return request.put(`/courses/${id}`, data) }
export function deleteCourse(id) { return request.delete(`/courses/${id}`) }
