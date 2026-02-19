# 因果图谱可视化组件文档

## 📋 概述

基于 `@xyflow/react` 和 `dagre` 开发的交互式因果关系图谱可视化组件，支持自动布局、节点详情展示和流畅的用户交互。

## 🎯 核心组件

### 1. CausalGraphViewer（主组件）

完整的因果图谱查看器，整合了图谱展示和侧边栏。

**Props:**
```typescript
interface CausalGraphViewerProps {
  analysisResult: AnalysisResult  // 后端返回的分析结果
  onNodeClick?: (node: any) => void  // 节点点击回调（可选）
  layoutDirection?: 'LR' | 'TB' | 'RL' | 'BT'  // 布局方向（默认 'LR'）
}
```

**使用示例:**
```jsx
import CausalGraphViewer from './components/CausalGraphViewer'

function App() {
  const [analysisResult, setAnalysisResult] = useState(null)
  
  return (
    <div className="h-screen">
      <CausalGraphViewer
        analysisResult={analysisResult}
        onNodeClick={(node) => console.log('点击节点:', node)}
        layoutDirection="LR"
      />
    </div>
  )
}
```

### 2. CustomNode（自定义节点）

渲染因果图谱中的节点，支持不同类型的样式。

**特性:**
- ✅ 5 种节点类型（原因、结果、中间、假设、证据）
- ✅ 不同颜色区分类型
- ✅ 显示置信度
- ✅ 选中高亮效果
- ✅ 悬停缩放动画

### 3. Sidebar（详情侧边栏）

从右侧滑出的侧边栏，展示选中节点的详细信息。

**特性:**
- ✅ 平滑滑入/滑出动画
- ✅ 显示节点完整信息
- ✅ 置信度可视化
- ✅ 类型说明
- ✅ 点击遮罩关闭

## 🛠️ 工具函数

### layoutUtils.js

**getLayoutedElements(nodes, edges, direction)**

使用 Dagre 算法计算图布局。

```javascript
import { getLayoutedElements } from './utils/layoutUtils'

const { nodes: layoutedNodes, edges: layoutedEdges } = 
  getLayoutedElements(nodes, edges, 'LR')
```

**参数:**
- `nodes`: React Flow 节点数组
- `edges`: React Flow 边数组
- `direction`: 布局方向
  - `'LR'`: 从左到右（默认，适合因果流）
  - `'TB'`: 从上到下
  - `'RL'`: 从右到左
  - `'BT'`: 从下到上

**布局配置:**
```javascript
{
  rankdir: 'LR',      // 布局方向
  align: 'UL',        // 对齐方式
  nodesep: 80,        // 同层节点间距
  ranksep: 120,       // 不同层级间距
  marginx: 20,        // 左右边距
  marginy: 20         // 上下边距
}
```

### dataTransform.js

**convertAnalysisResult(analysisResult)**

将后端 AnalysisResult 转换为 React Flow 格式。

```javascript
import { convertAnalysisResult } from './utils/dataTransform'

const { nodes, edges } = convertAnalysisResult(analysisResult)
```

**节点类型样式:**
```javascript
const NODE_STYLES = {
  cause: {
    bgColor: 'bg-red-500',      // 红色 - 原因
    borderColor: 'border-red-600',
    textColor: 'text-white',
    label: '原因'
  },
  effect: {
    bgColor: 'bg-green-500',    // 绿色 - 结果
    borderColor: 'border-green-600',
    textColor: 'text-white',
    label: '结果'
  },
  intermediate: {
    bgColor: 'bg-blue-500',     // 蓝色 - 中间节点
    borderColor: 'border-blue-600',
    textColor: 'text-white',
    label: '中间节点'
  },
  hypothesis: {
    bgColor: 'bg-amber-500',    // 橙色 - 假设
    borderColor: 'border-amber-600',
    textColor: 'text-white',
    label: '假设'
  },
  evidence: {
    bgColor: 'bg-purple-500',   // 紫色 - 证据
    borderColor: 'border-purple-600',
    textColor: 'text-white',
    label: '证据'
  }
}
```

**边强度样式:**
```javascript
const EDGE_STYLES = {
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
    animated: true,      // 强关联带动画
    color: '#c084fc'
  }
}
```

## 📦 安装依赖

### 1. 更新 package.json

```bash
npm install @xyflow/react@^12.0.4 dagre@^0.8.5
```

或手动更新 `package.json`:
```json
{
  "dependencies": {
    "@xyflow/react": "^12.0.4",
    "dagre": "^0.8.5"
  }
}
```

### 2. 安装依赖

```bash
cd frontend
npm install
```

## 🚀 快速开始

### 基础使用

```jsx
import { useState, useEffect } from 'react'
import CausalGraphViewer from './components/CausalGraphViewer'

function App() {
  const [analysisResult, setAnalysisResult] = useState(null)
  
  // 从后端获取数据
  useEffect(() => {
    fetch('/api/v1/extract-causality', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ news_text: '新闻内容...' })
    })
      .then(res => res.json())
      .then(data => setAnalysisResult(data))
  }, [])
  
  return (
    <div className="h-screen">
      <CausalGraphViewer analysisResult={analysisResult} />
    </div>
  )
}
```

### 完整示例

```jsx
import { useState } from 'react'
import CausalGraphViewer from './components/CausalGraphViewer'

function CausalAnalysisPage() {
  const [analysisResult, setAnalysisResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [layoutDirection, setLayoutDirection] = useState('LR')
  
  const handleAnalyze = async (newsText) => {
    setLoading(true)
    try {
      const response = await fetch('/api/v1/extract-causality', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          news_text: newsText,
          generate_summary: true 
        })
      })
      const data = await response.json()
      setAnalysisResult(data)
    } catch (error) {
      console.error('分析失败:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const handleNodeClick = (node) => {
    console.log('节点详情:', node)
    // 可以在这里添加自定义逻辑
  }
  
  return (
    <div className="min-h-screen bg-slate-900">
      {/* 头部控制区 */}
      <header className="p-6 border-b border-slate-700">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-white">
            因果关系分析
          </h1>
          
          {/* 布局方向切换 */}
          <select
            value={layoutDirection}
            onChange={(e) => setLayoutDirection(e.target.value)}
            className="bg-slate-800 text-white px-3 py-2 rounded-lg"
          >
            <option value="LR">从左到右</option>
            <option value="TB">从上到下</option>
            <option value="RL">从右到左</option>
            <option value="BT">从下到上</option>
          </select>
        </div>
      </header>
      
      {/* 图谱展示区 */}
      <div className="h-[calc(100vh-100px)]">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-white">加载中...</div>
          </div>
        ) : analysisResult ? (
          <CausalGraphViewer
            analysisResult={analysisResult}
            onNodeClick={handleNodeClick}
            layoutDirection={layoutDirection}
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-slate-400">请输入内容开始分析</div>
          </div>
        )}
      </div>
    </div>
  )
}
```

## 🎨 自定义样式

### 修改节点样式

编辑 `src/utils/dataTransform.js`:

```javascript
export const NODE_STYLES = {
  cause: {
    bgColor: 'bg-red-600',      // 修改背景色
    borderColor: 'border-red-700',
    textColor: 'text-white',
    label: '根本原因'            // 修改标签
  },
  // ... 其他类型
}
```

### 修改布局参数

编辑 `src/utils/layoutUtils.js`:

```javascript
dagreGraph.setGraph({
  rankdir: direction,
  align: 'UL',
  nodesep: 100,      // 增加节点间距
  ranksep: 150,      // 增加层级间距
  marginx: 30,
  marginy: 30
})
```

### 修改节点尺寸

编辑 `src/utils/layoutUtils.js`:

```javascript
const NODE_WIDTH = 250   // 增加宽度
const NODE_HEIGHT = 120  // 增加高度
```

## 🎯 交互功能

### 1. 节点点击

点击节点时，侧边栏从右侧滑出，显示详细信息。

### 2. 画布操作

- **拖拽**: 按住鼠标左键拖动画布
- **缩放**: 鼠标滚轮缩放
- **框选**: 按住 Shift + 鼠标拖拽框选节点

### 3. 控制面板

- **放大/缩小**: 点击 +/- 按钮
- **适应视图**: 点击适应按钮自动调整视图
- **锁定**: 锁定画布禁止交互

### 4. 小地图

右下角的小地图显示整体布局，点击可快速导航。

## 📊 数据格式

### 输入格式（AnalysisResult）

```typescript
interface AnalysisResult {
  nodes: Array<{
    id: string
    label: string
    type: 'cause' | 'effect' | 'intermediate' | 'hypothesis' | 'evidence'
    description?: string
    confidence?: number  // 0-1
    metadata?: object
  }>
  edges: Array<{
    source: string
    target: string
    label?: string
    description?: string
    strength?: number  // 0-1
  }>
  explanation: string
  metadata?: object
}
```

### 示例数据

```javascript
const analysisResult = {
  nodes: [
    {
      id: 'n1',
      label: '全球变暖',
      type: 'cause',
      description: '地球平均温度持续上升',
      confidence: 0.95
    },
    {
      id: 'n2',
      label: '海平面上升',
      type: 'effect',
      description: '全球海平面显著上升',
      confidence: 0.85
    }
  ],
  edges: [
    {
      source: 'n1',
      target: 'n2',
      label: '导致',
      description: '温度上升导致冰川融化',
      strength: 0.9
    }
  ],
  explanation: '全球变暖导致海平面上升'
}
```

## 🔧 故障排除

### 问题 1: 节点重叠

**原因**: Dagre 布局参数不合适

**解决**: 增加 `nodesep` 和 `ranksep` 值

```javascript
dagreGraph.setGraph({
  nodesep: 100,   // 增加到 100
  ranksep: 150    // 增加到 150
})
```

### 问题 2: 样式不生效

**原因**: Tailwind CSS 未正确配置

**解决**: 确保 `tailwind.config.js` 包含组件路径

```javascript
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  // ...
}
```

### 问题 3: 侧边栏不显示

**原因**: z-index 层级问题

**解决**: 检查父容器是否有 `overflow: hidden`

## 📚 相关文档

- [@xyflow/react 官方文档](https://reactflow.dev/)
- [Dagre 布局算法](https://github.com/dagrejs/dagre)
- [Tailwind CSS 文档](https://tailwindcss.com/)

## 🎉 完成清单

- ✅ Dagre 自动布局
- ✅ 自定义节点组件
- ✅ 详情侧边栏
- ✅ 平滑动画
- ✅ 交互式控制
- ✅ 小地图导航
- ✅ 图例展示
- ✅ 模块化设计
- ✅ TypeScript 类型支持
- ✅ 完整文档

---

现在你可以开始使用因果图谱可视化组件了！🚀








