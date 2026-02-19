/**
 * 详情侧边栏组件
 * 显示选中节点的详细信息
 */

import { getNodeTypeLabel } from '../utils/dataTransform'
import { NODE_STYLES } from '../utils/dataTransform'

function Sidebar({ selectedNode, onClose }) {
  if (!selectedNode) return null
  
  const style = NODE_STYLES[selectedNode.type] || NODE_STYLES.intermediate
  
  return (
    <>
      {/* 遮罩层 */}
      <div
        className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 transition-opacity duration-300"
        onClick={onClose}
      />
      
      {/* 侧边栏 */}
      <div
        className={`
          fixed right-0 top-0 h-full w-96 bg-slate-800 shadow-2xl z-50
          transform transition-transform duration-300 ease-out
          ${selectedNode ? 'translate-x-0' : 'translate-x-full'}
        `}
      >
        <div className="h-full flex flex-col">
          {/* 头部 */}
          <div className="p-6 border-b border-slate-700">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className={`
                    px-2 py-1 rounded text-xs font-medium
                    ${style.bgColor} ${style.textColor}
                  `}>
                    {getNodeTypeLabel(selectedNode.type)}
                  </span>
                  {selectedNode.confidence && (
                    <span className="text-xs text-slate-400">
                      置信度 {(selectedNode.confidence * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
                <h2 className="text-xl font-bold text-white">
                  {selectedNode.label}
                </h2>
              </div>
              
              {/* 关闭按钮 */}
              <button
                onClick={onClose}
                className="text-slate-400 hover:text-white transition-colors p-1"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
          
          {/* 内容区域 */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {/* 节点描述 */}
            {selectedNode.description && (
              <div>
                <h3 className="text-sm font-semibold text-slate-300 mb-2">
                  详细描述
                </h3>
                <p className="text-slate-400 leading-relaxed">
                  {selectedNode.description}
                </p>
              </div>
            )}
            
            {/* 节点 ID */}
            <div>
              <h3 className="text-sm font-semibold text-slate-300 mb-2">
                节点 ID
              </h3>
              <code className="text-xs text-purple-400 bg-slate-900 px-2 py-1 rounded">
                {selectedNode.id}
              </code>
            </div>
            
            {/* 节点类型说明 */}
            <div>
              <h3 className="text-sm font-semibold text-slate-300 mb-2">
                类型说明
              </h3>
              <div className="text-sm text-slate-400 space-y-2">
                {selectedNode.type === 'cause' && (
                  <p>此节点是因果链的起点，代表导致其他事件发生的根本原因。</p>
                )}
                {selectedNode.type === 'effect' && (
                  <p>此节点是因果链的终点，代表最终产生的结果或影响。</p>
                )}
                {selectedNode.type === 'intermediate' && (
                  <p>此节点是连接原因和结果的中间环节，在因果传导中起到桥梁作用。</p>
                )}
                {selectedNode.type === 'hypothesis' && (
                  <p>此节点代表一个推测性的因果关系，需要进一步验证。</p>
                )}
                {selectedNode.type === 'evidence' && (
                  <p>此节点提供支撑因果关系的事实依据。</p>
                )}
              </div>
            </div>
            
            {/* 置信度说明 */}
            {selectedNode.confidence && (
              <div>
                <h3 className="text-sm font-semibold text-slate-300 mb-2">
                  置信度分析
                </h3>
                <div className="space-y-2">
                  {/* 置信度进度条 */}
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${style.bgColor}`}
                      style={{ width: `${selectedNode.confidence * 100}%` }}
                    />
                  </div>
                  <p className="text-sm text-slate-400">
                    {selectedNode.confidence >= 0.8 && '高置信度：该节点有充分的证据支持'}
                    {selectedNode.confidence >= 0.5 && selectedNode.confidence < 0.8 && '中等置信度：该节点有一定的证据支持'}
                    {selectedNode.confidence < 0.5 && '低置信度：该节点的证据较为薄弱'}
                  </p>
                </div>
              </div>
            )}
            
            {/* 元数据 */}
            {selectedNode.metadata && Object.keys(selectedNode.metadata).length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-slate-300 mb-2">
                  其他信息
                </h3>
                <div className="bg-slate-900 rounded-lg p-3 text-xs text-slate-400 space-y-1">
                  {Object.entries(selectedNode.metadata).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <span className="text-slate-500">{key}:</span>
                      <span>{String(value)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
          
          {/* 底部操作区 */}
          <div className="p-6 border-t border-slate-700">
            <button
              onClick={onClose}
              className="w-full py-2 px-4 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
            >
              关闭
            </button>
          </div>
        </div>
      </div>
    </>
  )
}

export default Sidebar








