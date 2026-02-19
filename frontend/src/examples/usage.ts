/**
 * 使用示例和说明文档
 */

import { AnalysisResult, CausalQuery, NodeType } from './types/causal'
import { convertAnalysisResult, validateGraphData } from './utils/graphUtils'

// ============================================
// 1. 后端 API 返回的数据格式示例
// ============================================

const exampleApiResponse: AnalysisResult = {
  nodes: [
    {
      id: 'node1',
      label: '全球变暖',
      type: NodeType.CAUSE,
      description: '地球平均温度持续上升',
      confidence: 0.95,
    },
    {
      id: 'node2',
      label: '冰川融化',
      type: NodeType.INTERMEDIATE,
      description: '极地和高山冰川加速融化',
      confidence: 0.9,
    },
    {
      id: 'node3',
      label: '海平面上升',
      type: NodeType.EFFECT,
      description: '全球海平面显著上升',
      confidence: 0.85,
    },
  ],
  edges: [
    {
      source: 'node1',
      target: 'node2',
      label: '导致',
      description: '温度上升直接导致冰川融化',
      strength: 0.9,
    },
    {
      source: 'node2',
      target: 'node3',
      label: '引发',
      description: '冰川融化使海平面上升',
      strength: 0.85,
    },
  ],
  explanation: '全球变暖通过冰川融化最终导致海平面上升，形成一条清晰的因果链。',
  query: '全球变暖会导致什么后果？',
  timestamp: '2024-01-01T00:00:00Z',
  metadata: {
    depth: 3,
    totalNodes: 3,
    totalEdges: 2,
    analysisTime: 1500,
  },
}

// ============================================
// 2. 前端发送的查询请求示例
// ============================================

const exampleQuery: CausalQuery = {
  query: '全球变暖会导致什么后果？',
  context: '关注环境和气候变化',
  max_depth: 3,
  options: {
    includeEvidence: true,
    includeHypothesis: false,
    minConfidence: 0.7,
  },
}

// ============================================
// 3. 在 React 组件中使用
// ============================================

/*
import { useState } from 'react'
import ReactFlow from 'reactflow'
import { AnalysisResult } from './types/causal'
import { convertAnalysisResult, validateGraphData } from './utils/graphUtils'

function CausalGraphComponent() {
  const [nodes, setNodes] = useState([])
  const [edges, setEdges] = useState([])

  const handleAnalysisResult = (result: AnalysisResult) => {
    // 验证数据
    const validation = validateGraphData(result)
    if (!validation.valid) {
      console.error('数据验证失败:', validation.errors)
      return
    }

    // 转换为 React Flow 格式
    const { nodes, edges } = convertAnalysisResult(result, 'horizontal')
    setNodes(nodes)
    setEdges(edges)
  }

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      fitView
    />
  )
}
*/

// ============================================
// 4. API 调用示例
// ============================================

/*
async function analyzeCausalChain(query: CausalQuery): Promise<AnalysisResult> {
  const response = await fetch('/api/v1/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(query),
  })

  if (!response.ok) {
    throw new Error('分析失败')
  }

  const result: AnalysisResult = await response.json()
  return result
}

// 使用
const query: CausalQuery = {
  query: '经济衰退的原因是什么？',
  max_depth: 3,
}

analyzeCausalChain(query)
  .then((result) => {
    console.log('分析结果:', result)
    // 转换并显示图谱
    const { nodes, edges } = convertAnalysisResult(result)
  })
  .catch((error) => {
    console.error('分析错误:', error)
  })
*/

// ============================================
// 5. 自定义节点组件示例
// ============================================

/*
import { Handle, Position } from 'reactflow'
import { CausalNodeData } from './types/causal'
import { getNodeTypeLabel } from './utils/graphUtils'

function CustomCausalNode({ data }: { data: { nodeData: CausalNodeData } }) {
  const { nodeData } = data

  return (
    <div className="custom-node">
      <Handle type="target" position={Position.Left} />
      
      <div className="node-header">
        <span className="node-type">{getNodeTypeLabel(nodeData.type)}</span>
        {nodeData.confidence && (
          <span className="confidence">{(nodeData.confidence * 100).toFixed(0)}%</span>
        )}
      </div>
      
      <div className="node-label">{nodeData.label}</div>
      
      {nodeData.description && (
        <div className="node-description">{nodeData.description}</div>
      )}
      
      <Handle type="source" position={Position.Right} />
    </div>
  )
}
*/

// ============================================
// 6. 导出图数据示例
// ============================================

/*
import { exportGraphData } from './utils/graphUtils'

function ExportButton({ result, nodes, edges }) {
  const handleExport = () => {
    const jsonData = exportGraphData(result, nodes, edges)
    
    // 下载为文件
    const blob = new Blob([jsonData], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `causal-graph-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  return <button onClick={handleExport}>导出图谱</button>
}
*/

export {}








