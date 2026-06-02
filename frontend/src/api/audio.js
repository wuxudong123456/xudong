import request from './request'

export function recognizeSpeech(audioFile) {
  const formData = new FormData()
  formData.append('file', audioFile)
  return request.post('/audio/recognize', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function synthesizeSpeech(text) {
  return request.post('/audio/synthesize', { text })
}
