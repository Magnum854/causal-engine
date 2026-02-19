/**
 * 工具函数：将后端返回的数据转换为 React Flow 格式
 */

import { Node, Edge, MarkerType } from 'reactflow'
import {
  AnalysisResult,
  CausalNodeData,
  CausalEdgeData,
  CausalFlowNode,
  CausalFlowEdge,
  NodeType,
  EdgeStrength,
} from '../types/causal'

/**
 * 节点样式配置
 */
export const NODE_STYLES = {
  [NodeType.CAUSE]: {
    color: '#ffffff',
    bgColor: '#ef4444',
    borderColor: 'rgba(239, 68, 68, 0.5)',
  },
  [NodeType.EFFECT]: {
    color: '#ffffff',
    bgColor: '#10b981',
    borderColor: 'rgba(16, 185, 129, 0.5)',
  },
  [NodeType.INTERMEDIATE]: {
    color: '#ffffff',
    bgColor: '#3b82f6',
    borderColor: 'rgba(59, 130, 246, 0.5)',
  },
  [NodeType.HYPOTHESIS]: {
    color: '#ffffff',
    bgColor: '#f59e0b',
    borderColor: 'rgba(245, 158, 11, 0.5)',
  },
  [NodeType.EVIDENCE]: {
    color: '#ffffff',
    bgColor: '#8b5cf6',
    borderColor: 'rgba(139, 92, 246, 0.5)',
  },
}

/**
 * 边样式配置
 */
export const EDGE_STYLES = {
  [EdgeStrength.WEAK]: {
    strokeWidth: 1.5,
    opacity: 0.4,
    color: '#94a3b8',
  },
  [EdgeStrength.MODERATE]: {
    strokeWidth: 2.5,
    opacity: 0.7,
    color: '#a78bfa',
  },
  [EdgeStrength.STRONG]: {
    strokeWidth: 3.5,
    opacity: 1,
    color: '#c084fc',
  },
}

/**
 * 根据强度值获取强度等级
 */
export function getStrengthLevel(strength: number): EdgeStrength {
  if (strength < 0.3) return EdgeStrength.WEAK
  if (strength < 0.7) return EdgeStrength.MODERATE
  return EdgeStrength.STRONG
}

/**
 * 计算节点位置（简单的层级布局）
 */
export function calculateNodePosition(
  index: number,
  totalNodes: number,
  layout: 'horizontal' | 'vertical' = 'horizontal'
): { x: number; y: number } {
  const cols = Math.ceil(Math.sqrt(totalNodes))
  const row = Math.floor(index / cols)
  const col = index % cols

  if (layout === 'horizontal') {
    return {
      x: col * 280,
      y: row * 180,
    }
  } else {
    return {
      x: row * 280,
      y: col * 180,
    }
  }
}

/**
 * 将后端节点数据转换为 React Flow 节点
 */
export function convertToFlowNodes(
  nodes: CausalNodeData[],
  layout: 'horizontal' | 'vertical' = 'horizontal'
): CausalFlowNode[] {
  return nodes.map((node, index) => {
    const style = NODE_STYLES[node.type] || NODE_STYLES[NodeType.INTERMEDIATE]
    const position = calculateNodePosition(index, nodes.length, layout)

    return {
      id: node.id,
      type: 'default',
      position,
      data: {
        label: node.label,
        nodeData: node,
      },
      style: {
        background: style.bgColor,
        color: style.color,
        border: `2px solid ${style.borderColor}`,
        borderRadius: '12px',
        padding: '12px 16px',
        minWidth: '180px',
        fontSize: '14px',
        fontWeight: '500',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3)',
      },
    }
  })
}

/**
 * 将后端边数据转换为 React Flow 边
 */
export function convertToFlowEdges(edges: CausalEdgeData[]): CausalFlowEdge[] {
  return edges.map((edge) => {
    const strength = edge.strength || 0.5
    const strengthLevel = getStrengthLevel(strength)
    const style = EDGE_STYLES[strengthLevel]

    return {
      id: `${edge.source}-${edge.target}`,
      source: edge.source,
      target: edge.target,
      type: 'smoothstep',
      animated: strengthLevel === EdgeStrength.STRONG,
      label: edge.label,
      data: {
        edgeData: {
          ...edge,
          strengthLevel,
        },
      },
      style: {
        stroke: style.color,
        strokeWidth: style.strokeWidth,
        opacity: style.opacity,
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: style.color,
        width: 20,
        height: 20,
      },
      labelStyle: {
        fill: '#e2e8f0',
        fontSize: 12,
        fontWeight: 500,
      },
      labelBgStyle: {
        fill: '#1e293b',
        fillOpacity: 0.8,
      },
    }
  })
}

/**
 * 转换完整的分析结果
 */
export function convertAnalysisResult(
  result: AnalysisResult,
  layout: 'horizontal' | 'vertical' = 'horizontal'
): {
  nodes: CausalFlowNode[]
  edges: CausalFlowEdge[]
} {
  const nodes = convertToFlowNodes(result.nodes, layout)
  const edges = convertToFlowEdges(result.edges)

  return { nodes, edges }
}

/**
 * 验证图数据的完整性
 */
export function validateGraphData(result: AnalysisResult): {
  valid: boolean
  errors: string[]
} {
  const errors: string[] = []

  // 检查节点
  if (!result.nodes || result.nodes.length === 0) {
    errors.push('节点数据为空')
  }

  // 检查节点 ID 唯一性
  const nodeIds = new Set<string>()
  result.nodes?.forEach((node) => {
    if (nodeIds.has(node.id)) {
      errors.push(`重复的节点 ID: ${node.id}`)
    }
    nodeIds.add(node.id)
  })

  // 检查边的引用
  result.edges?.forEach((edge) => {
    if (!nodeIds.has(edge.source)) {
      errors.push(`边引用了不存在的源节点: ${edge.source}`)
    }
    if (!nodeIds.has(edge.target)) {
      errors.push(`边引用了不存在的目标节点: ${edge.target}`)
    }
  })

  return {
    valid: errors.length === 0,
    errors,
  }
}

/**
 * 获取节点类型的中文标签
 */
export function getNodeTypeLabel(type: NodeType): string {
  const labels = {
    [NodeType.CAUSE]: '原因',
    [NodeType.EFFECT]: '结果',
    [NodeType.INTERMEDIATE]: '中间节点',
    [NodeType.HYPOTHESIS]: '假设',
    [NodeType.EVIDENCE]: '证据',
  }
  return labels[type] || '未知'
}

/**
 * 获取强度等级的中文标签
 */
export function getStrengthLabel(strength: EdgeStrength): string {
  const labels = {
    [EdgeStrength.WEAK]: '弱关联',
    [EdgeStrength.MODERATE]: '中等关联',
    [EdgeStrength.STRONG]: '强关联',
  }
  return labels[strength] || '未知'
}

/**
 * 导出图数据为 JSON
 */
export function exportGraphData(
  result: AnalysisResult,
  nodes: CausalFlowNode[],
  edges: CausalFlowEdge[]
): string {
  const exportData = {
    version: '1.0.0',
    timestamp: new Date().toISOString(),
    query: result.query || '',
    result,
    graph: {
      nodes,
      edges,
    },
  }

  return JSON.stringify(exportData, null, 2)
}








