/**
 * 人物关系图谱API封装
 */
import request from './request'

/**
 * 查询人物信息
 * @param {string} name - 人物姓名
 */
export function getPersonInfo(name) {
  return request.get(`/graph/person/${encodeURIComponent(name)}`)
}

/**
 * 查询人物关系路径
 * @param {string} fromName - 起始人物
 * @param {string} toName - 目标人物
 */
export function findRelationPath(fromName, toName) {
  return request.get('/graph/path', {
    params: { from_name: fromName, to_name: toName }
  })
}

/**
 * 获取名著人物列表
 * @param {string} bookName - 名著标识
 */
export function getBookCharacters(bookName) {
  return request.get(`/graph/book/${bookName}`)
}

/**
 * 获取图谱可视化数据
 * @param {Object} params - {book, center}
 */
export function getGraphVisualization(params = {}) {
  return request.get('/graph/visualization', { params })
}

/**
 * 搜索人物
 * @param {string} keyword - 搜索关键词
 */
export function searchPerson(keyword) {
  return request.get('/graph/search', { params: { keyword } })
}
