/**
 * 全局数据源面板组件（现代极简白风格）
 * 展示分析引用的所有数据源
 */

import { useState } from 'react'

function DataSourcesPanel({ nodes }) {
  const [isExpanded, setIsExpanded] = useState(true)
  
  // 提取所有节点的数据源并去重
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
  
  // 如果没有数据源，不显示面板
  if (allSources.length === 0) {
    return null
  }
  
  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 shadow-lg z-40 transition-all duration-300">
      {/* 面板头部 */}
      <div 
        className="flex items-center justify-between px-8 py-3 bg-slate-50 cursor-pointer hover:bg-slate-100 transition-colors border-b border-slate-200"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          <span className="text-xl">📚</span>
          <div>
            <h3 className="font-semibold text-slate-900 text-sm">分析引用的数据源</h3>
            <p className="text-xs text-slate-600 mt-0.5">
              共 {allSources.length} 条来源 · 点击展开/收起
            </p>
          </div>
        </div>
        
        <button className="text-slate-500 hover:text-slate-700 transition-colors">
          {isExpanded ? (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
            </svg>
          )}
        </button>
      </div>
      
      {/* 面板内容 */}
      {isExpanded && (
        <div className="max-h-64 overflow-y-auto px-8 py-4 bg-white">
          <div className="space-y-2">
            {allSources.map((source, index) => (
              <div 
                key={index}
                className="flex items-start gap-3 p-3 bg-slate-50 rounded-md hover:bg-slate-100 transition-colors group border border-slate-200"
              >
                {/* 序号 */}
                <div className="flex-shrink-0 w-6 h-6 bg-slate-200 text-slate-700 rounded-full flex items-center justify-center font-medium text-xs">
                  {index + 1}
                </div>
                
                {/* 内容 */}
                <div className="flex-1 min-w-0">
                  {/* 节点名称 */}
                  <div className="text-xs text-slate-500 mb-1">
                    来自节点: <span className="font-medium text-slate-700">{source.nodeLabel}</span>
                  </div>
                  
                  {/* 新闻标题 */}
                  <div className="font-medium text-slate-900 text-sm mb-1.5 line-clamp-2 leading-snug">
                    {source.title}
                  </div>
                  
                  {/* 链接 */}
                  <a 
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1.5 group-hover:gap-2 transition-all"
                  >
                    <span className="font-mono text-xs bg-slate-200 px-1.5 py-0.5 rounded">
                      {source.domain}
                    </span>
                    <span>查看原文</span>
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default DataSourcesPanel

