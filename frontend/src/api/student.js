/**
 * 学生管理 API
 */
import request from './request'

export function getStudentList(params) {
  return request.get('/students/', { params })
}

export function getStudentDetail(id) {
  return request.get(`/students/${id}`)
}

export function createStudent(data) {
  return request.post('/students/', data)
}

export function updateStudent(id, data) {
  return request.put(`/students/${id}`, data)
}

export function deleteStudent(id) {
  return request.delete(`/students/${id}`)
}

export function batchDeleteStudents(ids) {
  return request.post('/students/batch-delete', { ids })
}

export function exportStudents(params) {
  return request.get('/students/export', { params, responseType: 'blob' })
}

export function importStudents(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/students/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
