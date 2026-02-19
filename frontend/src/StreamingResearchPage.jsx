/**
 * 流式标的研究页面
 * 展示实时进度反馈的因果推演
 */

import { useState, useEffect, useRef } from 'react'
import CausalGraphViewer from './components/CausalGraphViewer'
import LoadingOverlay from './components/LoadingOverlay'

function StreamingResearchPage() {
  const [target, setTarget] = useState('')
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(null)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const abortControllerRef = useRef(null)

  /**
   * 流式请求标的研究
   */
  const handleStreamResearch = async () => {
    if (!target.trim()) {
      alert('请输入标的名称')
      return
    }

    // 重置状态
    setLoading(true)
    setProgress(null)
    setResult(null)
    setError(null)

    // 创建 AbortController 用于取消请求
    abortControllerRef.current = new AbortController()

    try {
      // 发起流式请求
      const response = await fetch('/api/v1/research-target/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ target }),
        signal: abortControllerRef.current.signal,
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
              const event = JSON.parse(jsonStr)

              console.log('收到事件:', event)

              // 更新进度
              setProgress(event)

              // 处理成功事件
              if (event.status === 'success' && event.data) {
                setResult(event.data)
                setLoading(false)
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
    } catch (err) {
      if (err.name === 'AbortError') {
        console.log('请求已取消')
      } else {
        console.error('流式请求失败:', err)
        setError(err)
      }
      setLoading(false)
    }
  }

  /**
   * 取消请求
   */
  const handleCancel = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      setLoading(false)
    }
  }

  /**
   * 组件卸载时取消请求
   */
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [])

  /**
   * 获取进度消息
   */
  const getProgressMessage = () => {
    if (!progress) return '初始化中...'

    const messages = {
      start: '开始分析...',
      step1_start: '正在提取核心影响因子...',
      step1_complete: '因子提取完成',
      step2_start: '正在搜索最新资讯...',
      step2_complete: '搜索完成',
      step3_start: '正在生成因果关系图谱...',
      step3_complete: '图谱生成完成',
      success: '分析完成！',
      error: '分析失败',
    }

    return progress.message || messages[progress.status] || '处理中...'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* 加载动画覆盖层 */}
      <LoadingOverlay
        isVisible={loading}
        message={getProgressMessage()}
        progress={progress}
      />

      {/* 头部 */}
      <header className="border-b border-white/10 backdrop-blur-sm bg-white/5">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400">
                流式因果推演引擎
              </h1>
              <p className="text-slate-300 mt-2 text-sm">
                实时展示分析进度 • 标的逆向推演 • 智能因果图谱
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* 主内容区 */}
      <div className="container mx-auto px-6 py-8">
        {/* 输入区域 */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-white/10 shadow-2xl p-6 mb-6">
          <div className="flex gap-4">
            <input
              type="text"
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleStreamResearch()}
              placeholder="输入标的名称（如：中证1000指数、比特币、特斯拉股票）"
              className="flex-1 px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              disabled={loading}
            />
            {loading ? (
              <button
                onClick={handleCancel}
                className="px-8 py-3 bg-red-600 hover:bg-red-700 text-white font-medium rounded-xl transition-all duration-200"
              >
                取消
              </button>
            ) : (
              <button
                onClick={handleStreamResearch}
                disabled={!target.trim()}
                className="px-8 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:from-slate-700 disabled:to-slate-700 text-white font-medium rounded-xl transition-all duration-200 transform hover:scale-105 active:scale-95 disabled:cursor-not-allowed disabled:transform-none shadow-lg"
              >
                开始分析
              </button>
            )}
          </div>

          {/* 示例标的 */}
          <div className="mt-4 flex flex-wrap gap-2">
            <span className="text-sm text-slate-400">快速选择:</span>
            {['中证1000指数', '比特币', '特斯拉股票', '黄金期货'].map((example) => (
              <button
                key={example}
                onClick={() => setTarget(example)}
                disabled={loading}
                className="px-3 py-1 bg-slate-700/50 hover:bg-slate-700 text-slate-300 text-sm rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {example}
              </button>
            ))}
          </div>
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/50 rounded-2xl p-6 mb-6">
            <div className="flex items-start gap-3">
              <svg className="w-6 h-6 text-red-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h3 className="text-red-400 font-semibold mb-1">分析失败</h3>
                <p className="text-red-300 text-sm">{error.message}</p>
              </div>
            </div>
          </div>
        )}

        {/* 图谱展示区 */}
        {result ? (
          <>
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-white/10 shadow-2xl overflow-hidden mb-6">
              <div className="p-6 border-b border-white/10">
                <h2 className="text-xl font-semibold text-white">
                  因果关系图谱
                </h2>
                <p className="text-slate-400 text-sm mt-1">
                  点击节点查看详细信息 • 拖拽移动视图 • 滚轮缩放
                </p>
              </div>
              <div className="h-[700px]">
                <CausalGraphViewer
                  analysisResult={result}
                  layoutDirection="LR"
                />
              </div>
            </div>

            {/* 分析说明 */}
            {result.explanation && (
              <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-white/10 shadow-2xl p-6">
                <h3 className="text-lg font-semibold text-white mb-3">
                  分析说明
                </h3>
                <p className="text-slate-300 leading-relaxed">
                  {result.explanation}
                </p>

                {/* 元数据 */}
                {result.metadata && (
                  <div className="mt-6 pt-6 border-t border-slate-700">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <div className="text-slate-500">节点数</div>
                        <div className="text-white font-semibold text-lg">
                          {result.nodes?.length || 0}
                        </div>
                      </div>
                      <div>
                        <div className="text-slate-500">边数</div>
                        <div className="text-white font-semibold text-lg">
                          {result.edges?.length || 0}
                        </div>
                      </div>
                      <div>
                        <div className="text-slate-500">核心因子</div>
                        <div className="text-white font-semibold text-lg">
                          {result.metadata.factors?.length || 0}
                        </div>
                      </div>
                      <div>
                        <div className="text-slate-500">总耗时</div>
                        <div className="text-white font-semibold text-lg">
                          {result.metadata.total_time?.toFixed(1)}s
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        ) : !loading && (
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-white/10 shadow-2xl p-12">
            <div className="text-center text-slate-400">
              <svg className="w-24 h-24 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
              <p className="text-lg">输入标的名称开始分析</p>
              <p className="text-sm mt-2">系统将实时展示分析进度</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default StreamingResearchPage







