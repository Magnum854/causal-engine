/**
 * 因果推演图类型定义
 * 适配 React Flow 使用
 */

import { Node, Edge } from 'reactflow'

/**
 * 节点类型枚举
 */
export enum NodeType {
  CAUSE = 'cause',           // 原因节点
  EFFECT = 'effect',         // 结果节点
  INTERMEDIATE = 'intermediate', // 中间节点
  HYPOTHESIS = 'hypothesis', // 假设节点
  EVIDENCE = 'evidence'      // 证据节点
}

/**
 * 边的强度等级
 */
export enum EdgeStrength {
  WEAK = 'weak',       // 弱关联 (0-0.3)
  MODERATE = 'moderate', // 中等关联 (0.3-0.7)
  STRONG = 'strong'    // 强关联 (0.7-1.0)
}

/**
 * 因果节点数据
 */
export interface CausalNodeData {
  id: string
  label: string
  type: NodeType
  description?: string
  confidence?: number  // 置信度 0-1
  metadata?: Record<string, any>
}

/**
 * 因果边数据
 */
export interface CausalEdgeData {
  source: string
  target: string
  label?: string
  description?: string
  strength?: number    // 因果强度 0-1
  strengthLevel?: EdgeStrength
  bidirectional?: boolean  // 是否双向因果
  metadata?: Record<string, any>
}

/**
 * 分析结果（后端返回格式）
 */
export interface AnalysisResult {
  nodes: CausalNodeData[]
  edges: CausalEdgeData[]
  explanation: string
  query?: string
  timestamp?: string
  metadata?: {
    depth?: number
    totalNodes?: number
    totalEdges?: number
    analysisTime?: number
  }
}

/**
 * React Flow 节点扩展
 */
export interface CausalFlowNode extends Node {
  data: {
    label: string
    nodeData: CausalNodeData
  }
}

/**
 * React Flow 边扩展
 */
export interface CausalFlowEdge extends Edge {
  data?: {
    edgeData: CausalEdgeData
  }
}

/**
 * 图谱配置
 */
export interface GraphConfig {
  layout?: 'horizontal' | 'vertical' | 'radial' | 'force'
  nodeSpacing?: number
  edgeType?: 'default' | 'smoothstep' | 'step' | 'straight'
  animated?: boolean
  showMiniMap?: boolean
  showControls?: boolean
}

/**
 * 查询请求
 */
export interface CausalQuery {
  query: string
  context?: string
  max_depth?: number
  options?: {
    includeEvidence?: boolean
    includeHypothesis?: boolean
    minConfidence?: number
  }
}

/**
 * 节点样式配置
 */
export interface NodeStyleConfig {
  [NodeType.CAUSE]: {
    color: string
    bgColor: string
    borderColor: string
  }
  [NodeType.EFFECT]: {
    color: string
    bgColor: string
    borderColor: string
  }
  [NodeType.INTERMEDIATE]: {
    color: string
    bgColor: string
    borderColor: string
  }
  [NodeType.HYPOTHESIS]: {
    color: string
    bgColor: string
    borderColor: string
  }
  [NodeType.EVIDENCE]: {
    color: string
    bgColor: string
    borderColor: string
  }
}

/**
 * 边样式配置
 */
export interface EdgeStyleConfig {
  [EdgeStrength.WEAK]: {
    strokeWidth: number
    opacity: number
    color: string
  }
  [EdgeStrength.MODERATE]: {
    strokeWidth: number
    opacity: number
    color: string
  }
  [EdgeStrength.STRONG]: {
    strokeWidth: number
    opacity: number
    color: string
  }
}

/**
 * 导出数据格式
 */
export interface ExportData {
  version: string
  timestamp: string
  query: string
  result: AnalysisResult
  graph: {
    nodes: CausalFlowNode[]
    edges: CausalFlowEdge[]
  }
}








