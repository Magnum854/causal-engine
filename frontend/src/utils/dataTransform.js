/**
 * 数据转换工具
 * 将后端 AnalysisResult 转换为 React Flow 格式
 */

import { MarkerType } from '@xyflow/react'

/**
 * 节点类型样式配置
 */
export const NODE_STYLES = {
  cause: {
    bgColor: 'bg-red-500',
    borderColor: 'border-red-600',
    textColor: 'text-white',
    label: '原因'
  },
  effect: {
    bgColor: 'bg-green-500',
    borderColor: 'border-green-600',
    textColor: 'text-white',
    label: '结果'
  },
  intermediate: {
    bgColor: 'bg-blue-500',
    borderColor: 'border-blue-600',
    textColor: 'text-white',
    label: '中间节点'
  },
  hypothesis: {
    bgColor: 'bg-amber-500',
    borderColor: 'border-amber-600',
    textColor: 'text-white',
    label: '假设'
  },
  evidence: {
    bgColor: 'bg-purple-500',
    borderColor: 'border-purple-600',
    textColor: 'text-white',
    label: '证据'
  }
}

/**
 * 边强度样式配置
 */
export const EDGE_STYLES = {
  weak: {
    strokeWidth: 1.5,
    animated: false,
    color: '#94a3b8'
  },
  moderate: {
    strokeWidth: 2.5,
    animated: false,
    color: '#a78bfa'
  },
  strong: {
    strokeWidth: 3.5,
    animated: true,
    color: '#c084fc'
  }
}

/**
 * 根据强度值获取强度等级
 */
function getStrengthLevel(strength) {
  if (!strength) return 'moderate'
  if (strength < 0.3) return 'weak'
  if (strength < 0.7) return 'moderate'
  return 'strong'
}

/**
 * 转换后端节点数据为 React Flow 节点
 */
export function convertNodesToReactFlow(nodes) {
  return nodes.map((node) => {
    const style = NODE_STYLES[node.type] || NODE_STYLES.intermediate
    
    return {
      id: node.id,
      type: 'custom',
      data: {
        label: node.label,
        type: node.type,
        description: node.description,
        confidence: node.confidence,
        originalData: node
      },
      position: { x: 0, y: 0 }, // 初始位置，会被 Dagre 重新计算
      style: {
        width: 220,
        height: 100
      }
    }
  })
}

/**
 * 转换后端边数据为 React Flow 边
 */
export function convertEdgesToReactFlow(edges) {
  return edges.map((edge) => {
    const strengthLevel = getStrengthLevel(edge.strength)
    const style = EDGE_STYLES[strengthLevel]
    
    return {
      id: `${edge.source}-${edge.target}`,
      source: edge.source,
      target: edge.target,
      type: 'smoothstep',
      animated: style.animated,
      label: edge.label,
      data: {
        description: edge.description,
        strength: edge.strength,
        strengthLevel,
        originalData: edge
      },
      style: {
        stroke: style.color,
        strokeWidth: style.strokeWidth
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: style.color,
        width: 20,
        height: 20
      },
      labelStyle: {
        fill: '#e2e8f0',
        fontSize: 12,
        fontWeight: 500
      },
      labelBgStyle: {
        fill: '#1e293b',
        fillOpacity: 0.8
      }
    }
  })
}

/**
 * 转换完整的 AnalysisResult
 */
export function convertAnalysisResult(analysisResult) {
  if (!analysisResult || !analysisResult.nodes || !analysisResult.edges) {
    return { nodes: [], edges: [] }
  }
  
  const nodes = convertNodesToReactFlow(analysisResult.nodes)
  const edges = convertEdgesToReactFlow(analysisResult.edges)
  
  return { nodes, edges }
}

/**
 * 获取节点类型的中文标签
 */
export function getNodeTypeLabel(type) {
  return NODE_STYLES[type]?.label || '未知'
}

/**
 * 获取强度等级的中文标签
 */
export function getStrengthLabel(strengthLevel) {
  const labels = {
    weak: '弱关联',
    moderate: '中等关联',
    strong: '强关联'
  }
  return labels[strengthLevel] || '未知'
}








