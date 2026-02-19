/**
 * Dagre 自动布局工具函数
 * 用于计算因果图谱的节点位置
 */

import dagre from 'dagre'

/**
 * 节点尺寸配置
 */
const NODE_WIDTH = 220
const NODE_HEIGHT = 100

/**
 * 使用 Dagre 算法计算图布局
 * 
 * @param {Array} nodes - React Flow 节点数组
 * @param {Array} edges - React Flow 边数组
 * @param {string} direction - 布局方向 ('LR' | 'TB' | 'RL' | 'BT')
 * @returns {Object} - 包含布局后的 nodes 和 edges
 */
export function getLayoutedElements(nodes, edges, direction = 'LR') {
  // 创建 Dagre 图实例
  const dagreGraph = new dagre.graphlib.Graph()
  
  // 设置图的默认配置
  dagreGraph.setDefaultEdgeLabel(() => ({}))
  
  // 配置布局参数
  dagreGraph.setGraph({
    rankdir: direction,      // 布局方向：LR(左到右), TB(上到下), RL(右到左), BT(下到上)
    align: 'UL',             // 对齐方式
    nodesep: 80,             // 同一层级节点之间的间距
    ranksep: 120,            // 不同层级之间的间距
    marginx: 20,             // 图的左右边距
    marginy: 20              // 图的上下边距
  })
  
  // 添加节点到 Dagre 图
  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, {
      width: NODE_WIDTH,
      height: NODE_HEIGHT
    })
  })
  
  // 添加边到 Dagre 图
  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target)
  })
  
  // 执行布局计算
  dagre.layout(dagreGraph)
  
  // 将计算后的位置应用到节点
  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id)
    
    // Dagre 返回的是节点中心点坐标，需要转换为左上角坐标
    const x = nodeWithPosition.x - NODE_WIDTH / 2
    const y = nodeWithPosition.y - NODE_HEIGHT / 2
    
    return {
      ...node,
      position: { x, y }
    }
  })
  
  return {
    nodes: layoutedNodes,
    edges
  }
}

/**
 * 重新计算布局（用于动态更新）
 * 
 * @param {Array} nodes - 当前节点
 * @param {Array} edges - 当前边
 * @param {string} direction - 布局方向
 * @returns {Object} - 新的布局
 */
export function relayoutGraph(nodes, edges, direction = 'LR') {
  return getLayoutedElements(nodes, edges, direction)
}

/**
 * 获取图的边界框（用于自动缩放）
 * 
 * @param {Array} nodes - 节点数组
 * @returns {Object} - 边界框 {minX, minY, maxX, maxY}
 */
export function getGraphBounds(nodes) {
  if (!nodes || nodes.length === 0) {
    return { minX: 0, minY: 0, maxX: 0, maxY: 0 }
  }
  
  let minX = Infinity
  let minY = Infinity
  let maxX = -Infinity
  let maxY = -Infinity
  
  nodes.forEach((node) => {
    const { x, y } = node.position
    minX = Math.min(minX, x)
    minY = Math.min(minY, y)
    maxX = Math.max(maxX, x + NODE_WIDTH)
    maxY = Math.max(maxY, y + NODE_HEIGHT)
  })
  
  return { minX, minY, maxX, maxY }
}








