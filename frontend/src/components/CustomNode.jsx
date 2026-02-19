/**
 * 自定义节点组件（现代极简白风格）
 * Notion/Linear 风格 - 纯白背景 + 左侧彩色边线
 */

import { Handle, Position } from '@xyflow/react'
import { useState } from 'react'

// 节点类型配置 - 使用左侧边线区分
const NODE_TYPE_CONFIG = {
  cause: {
    label: '原因',
    borderColor: 'border-l-red-500',
    badgeColor: 'bg-red-100 text-red-700'
  },
  effect: {
    label: '结果',
    borderColor: 'border-l-green-500',
    badgeColor: 'bg-green-100 text-green-700'
  },
  intermediate: {
    label: '中间',
    borderColor: 'border-l-blue-500',
    badgeColor: 'bg-blue-100 text-blue-700'
  },
  hypothesis: {
    label: '假设',
    borderColor: 'border-l-purple-500',
    badgeColor: 'bg-purple-100 text-purple-700'
  },
  evidence: {
    label: '证据',
    borderColor: 'border-l-amber-500',
    badgeColor: 'bg-amber-100 text-amber-700'
  }
}

function CustomNode({ data, selected }) {
  const config = NODE_TYPE_CONFIG[data.type] || NODE_TYPE_CONFIG.intermediate
  const [showSourceTooltip, setShowSourceTooltip] = useState(false)
  
  // 提取实时状态数据
  const realtimeState = data.realtime_state
  const hasRealtimeData = realtimeState && realtimeState.latest_value
  const sources = realtimeState?.sources || []
  const primarySource = sources[0]
  
  return (
    <div
      className={`
        bg-white border border-slate-200 ${config.borderColor} border-l-4
        rounded-lg shadow-sm
        transition-all duration-200
        ${selected ? 'ring-2 ring-slate-400 shadow-md' : 'hover:shadow-md'}
        w-full h-full p-4 flex flex-col justify-between
        relative
      `}
    >
      {/* 输入连接点 */}
      <Handle
        type="target"
        position={Position.Left}
        className="w-2.5 h-2.5 !bg-slate-400 !border-2 !border-white"
      />
      
      {/* 数据源角标（右上角） */}
      {primarySource && (
        <div 
          className="absolute top-3 right-3 cursor-pointer"
          onMouseEnter={() => setShowSourceTooltip(true)}
          onMouseLeave={() => setShowSourceTooltip(false)}
        >
          <div className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-700 transition-colors">
            <span className="text-sm">🔗</span>
            <span className="font-mono text-xs">{primarySource.domain}</span>
          </div>
          
          {/* Tooltip */}
          {showSourceTooltip && (
            <div className="absolute top-full right-0 mt-2 w-72 bg-slate-900 text-white text-xs p-3 rounded-md shadow-xl z-50">
              <div className="font-medium mb-1.5 text-slate-200">数据来源</div>
              <div className="text-slate-300 leading-relaxed">{primarySource.title}</div>
              {sources.length > 1 && (
                <div className="mt-2 text-slate-400 text-xs">
                  +{sources.length - 1} 个其他来源
                </div>
              )}
            </div>
          )}
        </div>
      )}
      
      {/* 节点内容 */}
      <div className="flex-1 flex flex-col justify-center pr-16">
        {/* 节点类型徽章 */}
        <div className="mb-2">
          <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${config.badgeColor}`}>
            {config.label}
          </span>
        </div>
        
        {/* 节点标题 */}
        <div className="font-semibold text-sm text-slate-800 leading-snug mb-1">
          {data.label}
        </div>
        
        {/* 描述（如果有） */}
        {data.description && (
          <div className="text-xs text-slate-600 leading-relaxed mt-1 line-clamp-2">
            {data.description}
          </div>
        )}
        
        {/* 置信度 */}
        {data.confidence && (
          <div className="text-xs text-slate-500 mt-2">
            置信度 {(data.confidence * 100).toFixed(0)}%
          </div>
        )}
      </div>
      
      {/* 实时状态栏（底部） */}
      {hasRealtimeData && (
        <div className="mt-3 pt-3 border-t border-slate-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="text-xs text-slate-500 font-medium">实时状态</div>
              {/* 趋势指示器 */}
              {realtimeState.trend && (
                <span className="text-xs">
                  {realtimeState.trend === 'rising' && '📈'}
                  {realtimeState.trend === 'falling' && '📉'}
                  {realtimeState.trend === 'stable' && '➡️'}
                </span>
              )}
            </div>
            <div className="flex flex-col items-end">
              <div className="text-sm font-bold text-slate-900">
                {realtimeState.latest_value}
              </div>
              {/* 涨跌幅 */}
              {realtimeState.change_percent && realtimeState.change_percent !== 'N/A' && (
                <div className={`text-xs font-medium ${
                  realtimeState.change_percent.startsWith('+') ? 'text-green-600' : 
                  realtimeState.change_percent.startsWith('-') ? 'text-red-600' : 
                  'text-slate-500'
                }`}>
                  {realtimeState.change_percent}
                </div>
              )}
            </div>
          </div>
          {realtimeState.updated_at && (
            <div className="text-xs text-slate-400 mt-1">
              {new Date(realtimeState.updated_at).toLocaleTimeString('zh-CN', {
                hour: '2-digit',
                minute: '2-digit'
              })}
            </div>
          )}
        </div>
      )}
      
      {/* 输出连接点 */}
      <Handle
        type="source"
        position={Position.Right}
        className="w-2.5 h-2.5 !bg-slate-400 !border-2 !border-white"
      />
    </div>
  )
}

export default CustomNode








