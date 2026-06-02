/**
 * 多智能体API封装
 */
import request from './request'

/**
 * 非流式对话
 * @param {string} message - 用户消息
 * @param {Array} history - 对话历史 [{role, content}]
 */
export function agentChat(message, history = [], character = 'bajie') {
  return request.post('/agent/chat', { message, history, character })
}

/**
 * 流式对话 (SSE)
 * 使用 fetch + ReadableStream 实现 POST SSE
 * @param {string} message - 用户消息
 * @param {Array} history - 对话历史
 * @param {Object} callbacks - 回调函数 {onIntent, onContent, onDone, onError}
 */
export async function agentChatStream(message, history = [], callbacks = {}, character = 'bajie', sessionId = null) {
  const { onIntent, onContent, onDone, onError } = callbacks

  try {
    const response = await fetch('/api/v1/agent/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      },
      body: JSON.stringify({ message, history, character, session_id: sessionId }),
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim()
        if (!line) continue

        // 处理 event: intent
        if (line.startsWith('event:')) {
          const eventType = line.slice(6).trim()
          // 读取下一行的 data
          if (i + 1 < lines.length && lines[i + 1].startsWith('data:')) {
            const dataStr = lines[i + 1].slice(5).trim()
            try {
              const data = JSON.parse(dataStr)
              if (eventType === 'intent' && data.intent) {
                onIntent?.(data.intent)
              }
            } catch (e) {
              // ignore
            }
            i++ // 跳过已处理的 data 行
          }
          continue
        }

        // 处理 data: {...}
        if (line.startsWith('data:')) {
          const dataStr = line.slice(5).trim()
          if (dataStr === '[DONE]') {
            onDone?.()
            return
          }
          try {
            const data = JSON.parse(dataStr)
            if (data.content) {
              onContent?.(data.content)
            }
            if (data.error) {
              onError?.(new Error(data.error))
              return
            }
          } catch (e) {
            // 非JSON数据，直接作为内容
            if (dataStr) {
              onContent?.(dataStr)
            }
          }
        }
      }
    }

    onDone?.()
  } catch (error) {
    onError?.(error)
  }
}
