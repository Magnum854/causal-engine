import { useState } from 'react'
import CausalGraph from './components/CausalGraph'
import QueryPanel from './components/QueryPanel'

function App() {
  // ============================================
  // 核心状态管理
  // ============================================
  const [hasAnalyzed, setHasAnalyzed] = useState(false)
  const [graphData, setGraphData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [nodes, setNodes] = useState([])
  const [showSources, setShowSources] = useState(false)

  // ============================================
  // 分析处理函数
  // ============================================
  const handleAnalyze = async (query, context, maxDepth) => {
    setLoading(true)
    setHasAnalyzed(true) // 触发布局切换
    
    try {
      const response = await fetch('causal-engine-production.up.railway.app/api/v1/analyze-v2', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          context,
          max_depth: maxDepth,
        }),
      })
      
      if (!response.ok) {
        throw new Error('分析失败')
      }
      
      const data = await response.json()
      console.log('[App] 接收到后端数据:', data)
      setGraphData(data)
    } catch (error) {
      console.error('分析错误:', error)
      alert('分析失败，请检查后端服务是否正常运行')
    } finally {
      setLoading(false)
    }
  }

  // ============================================
  // 提取所有数据源
  // ============================================
  const allSources = []
  const seenUrls = new Set()
  
  nodes.forEach(node => {
    const sources = node.data?.realtime_state?.sources || []
    sources.forEach(source => {
      if (source.url && !seenUrls.has(source.url)) {
        seenUrls.add(source.url)
        allSources.push({
          nodeLabel: node.data.label,
          ...source
        })
      }
    })
  })

  // ============================================
  // Phase 1: 初始状态 - 居中输入框
  // ============================================
  if (!hasAnalyzed) {
    return (
      <div className="h-screen w-screen flex flex-col items-center justify-center bg-gradient-to-br from-slate-50 via-slate-100 to-slate-50">
        {/* Logo 和标题 */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">
            CausalFlow
          </h1>
          <p className="text-slate-600 text-sm">
            基于大模型的智能因果推演引擎
          </p>
        </div>

        {/* 居中输入表单 */}
        <div className="max-w-2xl w-full px-6">
          <QueryPanel onAnalyze={handleAnalyze} loading={loading} />
        </div>

        {/* 底部提示 */}
        <div className="absolute bottom-8 text-center text-xs text-slate-500">
          <p>实时联网感知 · 数据溯源 · Yahoo Finance 直连</p>
        </div>
      </div>
    )
  }

  // ============================================
  // Phase 2: 分析状态 - 三栏布局
  // ============================================
  return (
    <div className="h-screen w-screen flex overflow-hidden bg-slate-50">
      {/* ========== Left Sidebar: 输入区 ========== */}
      <div className="w-[320px] h-full border-r border-slate-200 bg-white overflow-y-auto flex-shrink-0">
        <div className="p-4 border-b border-slate-200">
          <h2 className="text-lg font-semibold text-slate-900">CausalFlow</h2>
          <p className="text-xs text-slate-600 mt-1">因果推演引擎</p>
        </div>
        
        <div className="p-4">
          <QueryPanel onAnalyze={handleAnalyze} loading={loading} />
        </div>
      </div>

      {/* ========== Center Stage: 无限画布 ========== */}
      <div className="flex-1 h-full relative bg-slate-50">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="inline-block w-12 h-12 border-4 border-slate-300 border-t-slate-900 rounded-full animate-spin mb-4"></div>
              <p className="text-slate-900 font-semibold text-lg">正在分析因果关系</p>
              <p className="text-slate-500 text-sm mt-2">Pass 1: 生成拓扑结构 → Pass 2: 联网获取实时数据</p>
            </div>
          </div>
        ) : graphData ? (
          <CausalGraph 
            data={graphData} 
            onNodesChange={(newNodes) => setNodes(newNodes)}
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-slate-400">
              <svg className="w-24 h-24 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
              <p className="text-lg font-medium text-slate-600">等待分析结果</p>
            </div>
          </div>
        )}
      </div>

      {/* ========== Right Sidebar: 分析说明 ========== */}
      <div className="w-[380px] h-full border-l border-slate-200 bg-white overflow-y-auto flex-shrink-0">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <svg className="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            分析说明
          </h3>
          
          {graphData ? (
            <div className="prose prose-sm prose-slate max-w-none">
              <p className="text-slate-700 leading-relaxed">{graphData.explanation}</p>
              
              {/* 统计信息 */}
              <div className="mt-6 pt-6 border-t border-slate-200">
                <h4 className="text-sm font-semibold text-slate-900 mb-3">图谱统计</h4>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">节点数量</span>
                    <span className="font-medium text-slate-900">{graphData.nodes?.length || 0}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">因果关系</span>
                    <span className="font-medium text-slate-900">{graphData.edges?.length || 0}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">数据源</span>
                    <span className="font-medium text-slate-900">{allSources.length}</span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-sm text-slate-500">
              <p>分析完成后，这里将显示详细的因果关系解释。</p>
            </div>
          )}
        </div>
      </div>

      {/* ========== Phase 3: 悬浮数据源按钮 (FAB) ========== */}
      {allSources.length > 0 && (
        <>
          {/* FAB 按钮 */}
          <button
            onClick={() => setShowSources(!showSources)}
            className="fixed bottom-8 right-8 z-50 flex items-center gap-2 px-5 py-3 bg-slate-900 hover:bg-slate-800 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 group"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            <span className="font-medium text-sm">引用来源</span>
            <span className="bg-white text-slate-900 px-2 py-0.5 rounded-full text-xs font-semibold">
              {allSources.length}
            </span>
          </button>

          {/* 数据源 Popover */}
          {showSources && (
            <>
              {/* 遮罩层 */}
              <div 
                className="fixed inset-0 bg-black bg-opacity-20 z-40"
                onClick={() => setShowSources(false)}
              />
              
              {/* Popover 内容 */}
              <div className="fixed bottom-24 right-8 z-50 w-[480px] max-h-[60vh] bg-white rounded-lg shadow-2xl border border-slate-200 overflow-hidden">
                {/* 头部 */}
                <div className="px-5 py-4 border-b border-slate-200 bg-slate-50">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-slate-900">分析引用的数据源</h3>
                    <button
                      onClick={() => setShowSources(false)}
                      className="text-slate-400 hover:text-slate-600 transition-colors"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                  <p className="text-xs text-slate-600 mt-1">共 {allSources.length} 条来源</p>
                </div>

                {/* 列表 */}
                <div className="overflow-y-auto max-h-[calc(60vh-80px)] p-4">
                  <div className="space-y-3">
                    {allSources.map((source, index) => (
                      <div 
                        key={index}
                        className="p-3 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors border border-slate-200"
                      >
                        <div className="flex items-start gap-3">
                          <div className="flex-shrink-0 w-6 h-6 bg-slate-300 text-slate-700 rounded-full flex items-center justify-center font-semibold text-xs">
                            {index + 1}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="text-xs text-slate-500 mb-1">
                              来自: <span className="font-medium text-slate-700">{source.nodeLabel}</span>
                            </div>
                            <div className="font-medium text-slate-900 text-sm mb-2 line-clamp-2">
                              {source.title}
                            </div>
                            <a 
                              href={source.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1.5"
                            >
                              <span className="font-mono bg-slate-200 px-1.5 py-0.5 rounded">
                                {source.domain}
                              </span>
                              <span>查看原文</span>
                              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                              </svg>
                            </a>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </>
          )}
        </>
      )}
    </div>
  )
}

export default App

