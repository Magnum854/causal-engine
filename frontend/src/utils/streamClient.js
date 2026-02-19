/**
 * 流式 API 客户端
 * 用于处理 Server-Sent Events (SSE) 流式响应
 */

/**
 * 流式事件类型
 */
export interface StreamEvent {
  status: 'start' | 'step1_start' | 'step1_complete' | 'step2_start' | 
          'step2_complete' | 'step3_start' | 'step3_complete' | 'success' | 'error'
  message: string
  data?: any
  timestamp: number
}

/**
 * 流式请求配置
 */
export interface StreamConfig {
  onProgress?: (event: StreamEvent) => void
  onComplete?: (data: any) => void
  onError?: (error: Error) => void
  signal?: AbortSignal
}

/**
 * 流式请求标的研究
 * 
 * @param target - 标的名称
 * @param config - 配置选项
 * @returns Promise<void>
 */
export async function streamResearchTarget(
  target: string,
  config: StreamConfig = {}
): Promise<void> {
  const { onProgress, onComplete, onError, signal } = config

  try {
    // 发起流式请求
    const response = await fetch('/api/v1/research-target/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ target }),
      signal, // 支持取消请求
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    if (!response.body) {
      throw new Error('响应体为空')
    }

    // 获取 ReadableStream
    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    // 读取流数据
    while (true) {
      const { done, value } = await reader.read()

      if (done) {
        break
      }

      // 解码数据块
      buffer += decoder.decode(value, { stream: true })

      // 按行分割处理
      const lines = buffer.split('\n')
      buffer = lines.pop() || '' // 保留不完整的行

      for (const line of lines) {
        // 跳过空行
        if (!line.trim()) {
          continue
        }

        // 解析 SSE 格式 (data: {...})
        if (line.startsWith('data: ')) {
          const jsonStr = line.slice(6) // 移除 "data: " 前缀

          try {
            const event: StreamEvent = JSON.parse(jsonStr)

            // 触发进度回调
            if (onProgress) {
              onProgress(event)
            }

            // 处理成功事件
            if (event.status === 'success' && event.data) {
              if (onComplete) {
                onComplete(event.data)
              }
            }

            // 处理错误事件
            if (event.status === 'error') {
              throw new Error(event.message)
            }
          } catch (parseError) {
            console.error('JSON 解析失败:', jsonStr, parseError)
          }
        }
      }
    }
  } catch (error) {
    if (error instanceof Error) {
      if (onError) {
        onError(error)
      } else {
        console.error('流式请求失败:', error)
      }
    }
  }
}

/**
 * React Hook: 使用流式标的研究
 * 
 * @returns 流式请求函数和状态
 */
export function useStreamResearch() {
  const [loading, setLoading] = React.useState(false)
  const [progress, setProgress] = React.useState<StreamEvent | null>(null)
  const [result, setResult] = React.useState<any>(null)
  const [error, setError] = React.useState<Error | null>(null)
  const abortControllerRef = React.useRef<AbortController | null>(null)

  const startResearch = React.useCallback(async (target: string) => {
    // 重置状态
    setLoading(true)
    setProgress(null)
    setResult(null)
    setError(null)

    // 创建 AbortController
    abortControllerRef.current = new AbortController()

    try {
      await streamResearchTarget(target, {
        signal: abortControllerRef.current.signal,
        onProgress: (event) => {
          setProgress(event)
        },
        onComplete: (data) => {
          setResult(data)
          setLoading(false)
        },
        onError: (err) => {
          setError(err)
          setLoading(false)
        },
      })
    } catch (err) {
      if (err instanceof Error) {
        setError(err)
      }
      setLoading(false)
    }
  }, [])

  const cancel = React.useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      setLoading(false)
    }
  }, [])

  // 组件卸载时取消请求
  React.useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [])

  return {
    loading,
    progress,
    result,
    error,
    startResearch,
    cancel,
  }
}

// 为了兼容性，添加 React 导入检查
let React: any
if (typeof window !== 'undefined') {
  try {
    React = require('react')
  } catch {
    // React 未加载
  }
}







