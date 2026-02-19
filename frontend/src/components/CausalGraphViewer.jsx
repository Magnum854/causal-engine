/**
 * 因果图谱查看器组件
 * 主组件：整合图谱展示和侧边栏
 */

import { useState, useEffect, useCallback, useMemo } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Panel
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'

import CustomNode from './CustomNode'
import Sidebar from './Sidebar'
import { convertAnalysisResult } from '../utils/dataTransform'
import { getLayoutedElements } from '../utils/layoutUtils'
import { NODE_STYLES } from '../utils/dataTransform'

/**
 * 节点类型映射
 */
const nodeTypes = {
  custom: CustomNode
}

/**
 * 因果图谱查看器
 * 
 * @param {Object} props
 * @param {Object} props.analysisResult - 后端返回的 AnalysisResult 数据
 * @param {Function} props.onNodeClick - 节点点击回调（可选）
 * @param {string} props.layoutDirection - 布局方向 ('LR' | 'TB' | 'RL' | 'BT')
 */
function CausalGraphViewer({ 
  analysisResult, 
  onNodeClick,
  layoutDirection = 'LR' 
}) {
  // 状态管理
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [selectedNode, setSelectedNode] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  /**
   * 初始化图谱数据
   */
  useEffect(() => {
    if (!analysisResult) {
      setNodes([])
      setEdges([])
      return
    }

    setIsLoading(true)

    try {
      // 1. 转换后端数据为 React Flow 格式
      const { nodes: convertedNodes, edges: convertedEdges } = 
        convertAnalysisResult(analysisResult)

      // 2. 使用 Dagre 计算布局
      const { nodes: layoutedNodes, edges: layoutedEdges } = 
        getLayoutedElements(convertedNodes, convertedEdges, layoutDirection)

      // 3. 更新状态
      setNodes(layoutedNodes)
      setEdges(layoutedEdges)
    } catch (error) {
      console.error('图谱初始化失败:', error)
    } finally {
      setIsLoading(false)
    }
  }, [analysisResult, layoutDirection, setNodes, setEdges])

  /**
   * 处理节点点击事件
   */
  const handleNodeClick = useCallback((event, node) => {
    // 设置选中节点（用于侧边栏展示）
    setSelectedNode(node.data.originalData)
    
    // 触发外部回调
    if (onNodeClick) {
      onNodeClick(node.data.originalData)
    }
  }, [onNodeClick])

  /**
   * 关闭侧边栏
   */
  const handleCloseSidebar = useCallback(() => {
    setSelectedNode(null)
  }, [])

  /**
   * MiniMap 节点颜色配置
   */
  const nodeColor = useCallback((node) => {
    const type = node.data?.type || 'intermediate'
    const style = NODE_STYLES[type] || NODE_STYLES.intermediate
    
    // 将 Tailwind 类名转换为实际颜色
    const colorMap = {
      'bg-red-500': '#ef4444',
      'bg-green-500': '#10b981',
      'bg-blue-500': '#3b82f6',
      'bg-amber-500': '#f59e0b',
      'bg-purple-500': '#8b5cf6'
    }
    
    return colorMap[style.bgColor] || '#3b82f6'
  }, [])

  /**
   * 图例数据
   */
  const legendItems = useMemo(() => [
    { type: 'cause', label: '原因', color: '#ef4444' },
    { type: 'effect', label: '结果', color: '#10b981' },
    { type: 'intermediate', label: '中间节点', color: '#3b82f6' },
    { type: 'hypothesis', label: '假设', color: '#f59e0b' },
    { type: 'evidence', label: '证据', color: '#8b5cf6' }
  ], [])

  return (
    <div className="relative w-full h-full">
      {/* 加载状态 */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-slate-900/50 z-50">
          <div className="text-white text-center">
            <div className="inline-block w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mb-4" />
            <p>正在生成因果图谱...</p>
          </div>
        </div>
      )}

      {/* React Flow 画布 */}
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{
          padding: 0.2,
          includeHiddenNodes: false
        }}
        minZoom={0.1}
        maxZoom={2}
        defaultEdgeOptions={{
          type: 'smoothstep',
          animated: false
        }}
        className="bg-slate-900"
      >
        {/* 背景网格 */}
        <Background
          color="#475569"
          gap={16}
          size={1}
          variant="dots"
        />

        {/* 控制面板 */}
        <Controls
          className="bg-slate-800 border border-slate-700 rounded-lg"
          showInteractive={false}
        />

        {/* 小地图 */}
        <MiniMap
          nodeColor={nodeColor}
          className="bg-slate-800 border border-slate-700 rounded-lg"
          maskColor="rgba(0, 0, 0, 0.6)"
        />

        {/* 图例面板 */}
        <Panel position="top-left" className="bg-slate-800/90 backdrop-blur-sm rounded-lg p-4 border border-slate-700">
          <div className="text-sm font-semibold text-slate-300 mb-3">
            节点类型
          </div>
          <div className="space-y-2">
            {legendItems.map((item) => (
              <div key={item.type} className="flex items-center gap-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: item.color }}
                />
                <span className="text-xs text-slate-300">{item.label}</span>
              </div>
            ))}
          </div>
        </Panel>

        {/* 统计信息面板 */}
        <Panel position="top-right" className="bg-slate-800/90 backdrop-blur-sm rounded-lg p-4 border border-slate-700">
          <div className="text-xs text-slate-400 space-y-1">
            <div>节点数: <span className="text-white font-semibold">{nodes.length}</span></div>
            <div>边数: <span className="text-white font-semibold">{edges.length}</span></div>
          </div>
        </Panel>
      </ReactFlow>

      {/* 详情侧边栏 */}
      <Sidebar
        selectedNode={selectedNode}
        onClose={handleCloseSidebar}
      />
    </div>
  )
}

export default CausalGraphViewer








