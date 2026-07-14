# NodeDetailDrawer 组件文档

## 概述

`NodeDetailDrawer` 是一个专业的商业情报风格右侧详情面板组件，用于展示因果图谱节点的详细信息。组件采用固定定位，从右侧滑出，包含元信息、因果拓扑、时空动态演化和证据信源四大核心区块。

## 特性

- ✨ **商业情报风格设计**：专业的视觉层次和信息密度
- 🎯 **模块化架构**：内部拆分为多个子组件，易于维护
- ⏱️ **时间轴可视化**：垂直时间轴展示过去-现在-未来
- 📊 **场景分析**：Base Case 和 Tail Risk 双场景推演
- 🔗 **信源追溯**：展示新闻来源和 AI 置信度
- 🎨 **响应式交互**：流畅的动画和悬停效果

## 安装依赖

```bash
npm install lucide-react
```

## 基本用法

```jsx
import { useState } from 'react'
import NodeDetailDrawer from './components/NodeDetailDrawer'

function MyComponent() {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)
  const [nodeData, setNodeData] = useState(null)

  const handleNodeClick = (node) => {
    setNodeData(node)
    setIsDrawerOpen(true)
  }

  return (
    <>
      {/* 你的图谱或列表 */}
      <button onClick={() => handleNodeClick(someNodeData)}>
        查看详情
      </button>

      {/* 详情抽屉 */}
      <NodeDetailDrawer
        nodeData={nodeData}
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
      />
    </>
  )
}
```

## Props

| 属性 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `nodeData` | `Object` | 是 | 节点数据对象，包含 meta、topology、temporal_dynamics、evidence |
| `isOpen` | `Boolean` | 是 | 控制抽屉的显示/隐藏状态 |
| `onClose` | `Function` | 是 | 关闭抽屉的回调函数 |

## 数据结构

### nodeData 完整结构

```javascript
{
  // 1. 元信息区块
  meta: {
    title: "节点标题",                    // 必需
    category: "分类标签",                 // 可选
    risk_level: "high" | "medium" | "low", // 可选：风险等级
    current_metric: {                     // 可选：当前指标
      label: "指标名称",
      value: "指标值",
      trend: "up" | "down" | "stable"    // 趋势方向
    }
  },

  // 2. 因果拓扑区块
  topology: {
    causes: ["原因A", "原因B"],           // 可选：上游原因节点
    effects: ["结果X", "结果Y"]           // 可选：下游结果节点
  },

  // 3. 时空动态区块
  temporal_dynamics: {
    past: {                               // 可选：过去回顾
      summary: "历史情况描述"
    },
    present: {                            // 可选：当前状态
      summary: "现状描述"
    },
    future: {                             // 可选：未来推演
      base_case: {                        // 基准情景
        title: "情景标题",
        probability: "65%",               // 概率
        description: "情景描述",
        key_metrics: [                    // 关键指标
          { label: "指标1", value: "值1" },
          { label: "指标2", value: "值2" }
        ]
      },
      tail_risk: {                        // 尾部风险
        title: "风险标题",
        probability: "25%",
        description: "风险描述",
        key_metrics: [
          { label: "指标1", value: "值1" }
        ]
      }
    }
  },

  // 4. 证据信源区块
  evidence: {
    confidence_score: 0.85,               // 可选：AI 置信度 (0-1)
    sources: [                            // 可选：新闻来源列表
      {
        title: "新闻标题",
        url: "https://...",
        date: "2024-01-15"
      }
    ]
  }
}
```

## 组件结构

### 内部子组件

1. **DrawerHeader** - 顶部元信息区
   - 标题和关闭按钮
   - 分类和风险等级标签
   - 当前指标卡片

2. **TopologySection** - 因果脉络区
   - 简洁的因果链可视化
   - 原因 → 当前节点 → 结果

3. **TemporalDynamicsSection** - 时空动态区
   - 垂直时间轴布局
   - 过去/现在/未来三阶段
   - 场景卡片展示

4. **ScenarioCard** - 场景卡片
   - Base Case / Tail Risk 样式
   - 概率标签
   - 关键指标列表

5. **TimelineNode** - 时间轴节点
   - 不同阶段的视觉样式
   - 连接线和圆点

6. **EvidenceSection** - 证据信源区
   - AI 置信度进度条
   - 新闻来源列表

## 样式定制

### 风险等级颜色

```javascript
// 在 DrawerHeader 组件中
const getRiskColor = (level) => {
  const colors = {
    high: 'bg-red-100 text-red-700 border-red-300',
    medium: 'bg-amber-100 text-amber-700 border-amber-300',
    low: 'bg-green-100 text-green-700 border-green-300'
  }
  return colors[level] || colors.medium
}
```

### 置信度颜色

```javascript
// 在 EvidenceSection 组件中
const getConfidenceColor = (score) => {
  if (score >= 0.8) return 'bg-green-500'
  if (score >= 0.6) return 'bg-amber-500'
  return 'bg-red-500'
}
```

## 使用示例

### 示例 1：基本使用

```jsx
const nodeData = {
  meta: {
    title: "美联储加息预期",
    category: "货币政策",
    risk_level: "high",
    current_metric: {
      label: "联邦基金利率",
      value: "5.25%",
      trend: "up"
    }
  },
  topology: {
    causes: ["通胀压力", "就业市场强劲"],
    effects: ["美元走强", "股市波动"]
  }
}

<NodeDetailDrawer
  nodeData={nodeData}
  isOpen={true}
  onClose={() => console.log('关闭')}
/>
```

### 示例 2：与 React Flow 集成

```jsx
import { ReactFlow } from '@xyflow/react'
import NodeDetailDrawer from './NodeDetailDrawer'

function CausalGraph() {
  const [selectedNode, setSelectedNode] = useState(null)

  const handleNodeClick = (event, node) => {
    setSelectedNode(node.data.originalData)
  }

  return (
    <>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodeClick={handleNodeClick}
      />
      
      <NodeDetailDrawer
        nodeData={selectedNode}
        isOpen={!!selectedNode}
        onClose={() => setSelectedNode(null)}
      />
    </>
  )
}
```

### 示例 3：最小化数据

```jsx
// 只需要 meta.title 即可正常渲染
const minimalData = {
  meta: {
    title: "简单节点"
  }
}

<NodeDetailDrawer
  nodeData={minimalData}
  isOpen={true}
  onClose={handleClose}
/>
```

## 设计理念

### 视觉层次

1. **Header（高优先级）**
   - 大标题 + 关键指标
   - 吸引注意力的渐变卡片

2. **Topology（中优先级）**
   - 快速理解上下文
   - 简洁的箭头流程

3. **Temporal Dynamics（核心内容）**
   - 时间轴强化叙事感
   - 场景卡片突出概率

4. **Evidence（支撑信息）**
   - 底部放置，不干扰主要内容
   - 可点击的新闻链接

### 交互设计

- **遮罩层点击关闭**：点击背景即可关闭抽屉
- **关闭按钮**：右上角明显的 X 按钮
- **悬停效果**：新闻链接悬停时高亮
- **滚动优化**：内容过长时平滑滚动

## 技术栈

- **React 18+**
- **Tailwind CSS 3+**
- **Lucide React**（图标库）

## 浏览器兼容性

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 性能优化

- 使用 `backdrop-blur` 实现毛玻璃效果
- 条件渲染避免不必要的 DOM 节点
- 事件处理函数使用 `useCallback` 优化

## 常见问题

### Q: 如何修改抽屉宽度？

A: 修改主容器的 `w-[420px]` 类名：

```jsx
<div className="fixed right-0 top-0 h-screen w-[500px] ...">
```

### Q: 如何添加动画效果？

A: 可以使用 Tailwind 的 transition 类或 Framer Motion：

```jsx
import { motion } from 'framer-motion'

<motion.div
  initial={{ x: '100%' }}
  animate={{ x: 0 }}
  exit={{ x: '100%' }}
  transition={{ type: 'spring', damping: 20 }}
  className="fixed right-0 ..."
>
```

### Q: 如何自定义时间轴颜色？

A: 修改 `TimelineNode` 组件中的 `getPhaseStyles` 函数。

## 更新日志

### v1.0.0 (2024-02-24)
- 🎉 初始版本发布
- ✨ 完整的四区块布局
- 🎨 商业情报风格设计
- 📱 响应式支持

## 许可证

MIT

## 作者

CausalFlow Team












