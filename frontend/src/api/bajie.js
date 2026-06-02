/**
 * 八戒功能API封装
 */
import request from './request'

/**
 * 获取灯谜
 * @param {string} difficulty - 难度: easy/medium/hard
 */
export function getRiddle(difficulty = '') {
  return request.get('/bajie/riddle', { params: { difficulty } })
}

/**
 * 检查灯谜答案
 * @param {Object} data - {riddle_text, answer}
 */
export function checkRiddle(data) {
  return request.post('/bajie/riddle/check', data)
}

/**
 * 获取诗词对句
 */
export function getPoetry() {
  return request.get('/bajie/poetry')
}

/**
 * 检查诗词对句
 * @param {Object} data - {line, answer}
 */
export function checkPoetry(data) {
  return request.post('/bajie/poetry/check', data)
}

/**
 * 生成聊天话术
 * @param {Object} data - {scenario, personality, extra_info}
 */
export function generateChatLines(data) {
  return request.post('/bajie/chat-lines', data)
}

/**
 * 代写情书
 * @param {Object} data - {to, style, memory}
 */
export function writeLoveLetter(data) {
  return request.post('/bajie/love-letter', data)
}

/** 飞花令单字接龙 */
export function startFeihualing(data) {
  return request.post('/bajie/feihualing/start', data || {})
}
export function checkFeihualing(data) {
  return request.post('/bajie/feihualing/check', data)
}

/** LLM 灯谜 */
export function getRiddleLLM(topic) {
  return request.get('/bajie/riddle/llm', { params: { topic } })
}
export function checkRiddleLLM(data) {
  return request.post('/bajie/riddle/check/llm', data)
}

/** 成语接龙 */
export function startChengyu(data) {
  return request.post('/bajie/chengyu/start', data || {})
}
export function checkChengyu(data) {
  return request.post('/bajie/chengyu/check', data)
}
