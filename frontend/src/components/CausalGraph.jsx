import { useCallback, useEffect } from 'react'
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import CustomNode from './CustomNode'

const nodeTypes = {
  customNode: CustomNode,
}

// 节点类型颜色配置（用于 MiniMap）
const nodeTypeColors = {
  cause: '#ef4444',
  effect: '#10b981',
  intermediate: '#3b82f6',
  hypothesis: '#a855f7',
  evidence: '#f59e0b'
}

function CausalGraph({ data, onNodesChange: onNodesChangeCallback }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])

  useEffect(() => {
    if (!data) return

    console.log('[CausalGraph] 接收到数据:', data)

    // 转换节点数据 - 使用自定义节点组件
    const flowNodes = data.nodes.map((node, index) => ({
      id: node.id,
      type: 'customNode',
      data: {
        label: node.label,
        type: node.type,
        description: node.description,
        confidence: node.confidence,
        realtime_state: node.realtime_state,
      },
      position: { x: (index % 3) * 300, y: Math.floor(index / 3) * 220 },
    }))

    console.log('[CausalGraph] 转换后的节点:', flowNodes)

    // 转换边数据 - 使用柔和的石板灰
    const flowEdges = data.edges.map((edge) => ({
      id: `${edge.source}-${edge.target}`,
      source: edge.source,
      target: edge.target,
      label: edge.label,
      type: 'smoothstep',
      animated: true,
      style: {
        stroke: '#94a3b8', // 柔和的石板灰
        strokeWidth: 1.5 + (edge.strength || 0.5) * 1,
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: '#94a3b8',
        width: 20,
        height: 20,
      },
      labelStyle: {
        fill: '#475569',
        fontSize: 11,
        fontWeight: 500,
      },
      labelBgStyle: {
        fill: '#ffffff',
        fillOpacity: 0.9,
        stroke: '#e2e8f0',
        strokeWidth: 1,
      },
    }))

    console.log('[CausalGraph] 转换后的边:', flowEdges)

    setNodes(flowNodes)
    setEdges(flowEdges)
    
    // 通知父组件节点已更新
    if (onNodesChangeCallback) {
      onNodesChangeCallback(flowNodes)
    }
  }, [data, setNodes, setEdges])

  return (
    <div className="w-full h-full bg-slate-50">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-left"
      >
        {/* 浅灰色点阵背景 */}
        <Background 
          variant="dots" 
          color="#e2e8f0" 
          gap={16} 
          size={1}
        />
        
        {/* 控制按钮 - 白色主题 */}
        <Controls 
          className="bg-white border border-slate-200 rounded-md shadow-sm"
          style={{
            button: {
              backgroundColor: 'white',
              borderBottom: '1px solid #e2e8f0',
            }
          }}
        />
        
        {/* MiniMap - 白色主题 */}
        <MiniMap
          nodeColor={(node) => {
            const nodeData = data?.nodes.find((n) => n.id === node.id)
            return nodeTypeColors[nodeData?.type] || '#64748b'
          }}
          className="bg-white border border-slate-200 rounded-md shadow-sm"
          maskColor="rgb(248, 250, 252, 0.6)"
        />
      </ReactFlow>

      {/* 图例 - 白色主题 */}
      <div className="absolute bottom-4 left-4 bg-white border border-slate-200 rounded-md shadow-sm p-3">
        <div className="text-xs font-semibold text-slate-700 mb-2">节点类型</div>
        <div className="space-y-1.5">
          {Object.entries(nodeTypeColors).map(([type, color]) => (
            <div key={type} className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-sm border border-slate-200"
                style={{ backgroundColor: color }}
              />
              <span className="text-xs text-slate-600">
                {type === 'cause' && '原因'}
                {type === 'effect' && '结果'}
                {type === 'intermediate' && '中间'}
                {type === 'hypothesis' && '假设'}
                {type === 'evidence' && '证据'}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default CausalGraph

