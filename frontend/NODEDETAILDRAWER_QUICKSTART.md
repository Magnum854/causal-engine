# NodeDetailDrawer 快速启动指南

## 🚀 快速开始

### 1. 查看演示页面

在 `App.jsx` 中导入演示页面：

```jsx
import NodeDetailDrawerDemo from './NodeDetailDrawerDemo'

function App() {
  return <NodeDetailDrawerDemo />
}

export default App
```

然后启动开发服务器：

```bash
cd frontend
npm run dev
```

访问 `http://localhost:5173` 即可看到完整的演示页面。

---

## 📦 文件清单

已创建的文件：

```
frontend/src/components/
├── NodeDetailDrawer.jsx              # 主组件
├── NodeDetailDrawer.example.jsx     # 基础使用示例
├── NodeDetailDrawer.testData.js     # 测试数据
└── NodeDetailDrawer.README.md       # 完整文档

frontend/src/
└── NodeDetailDrawerDemo.jsx          # 完整演示页面
```

---

## 🎯 三种使用方式

### 方式 1: 查看完整演示（推荐）

```jsx
// App.jsx
import NodeDetailDrawerDemo from './NodeDetailDrawerDemo'

function App() {
  return <NodeDetailDrawerDemo />
}
```

**特点**: 包含 6 个测试场景，精美的卡片布局，一键查看所有功能。

---

### 方式 2: 集成到现有图谱

```jsx
// CausalGraphViewer.jsx (已自动集成)
import NodeDetailDrawer from './NodeDetailDrawer'

function CausalGraphViewer({ analysisResult }) {
  const [selectedNode, setSelectedNode] = useState(null)

  const handleNodeClick = (event, node) => {
    setSelectedNode(node.data.originalData)
  }

  return (
    <>
      <ReactFlow onNodeClick={handleNodeClick} />
      
      <NodeDetailDrawer
        nodeData={selectedNode}
        isOpen={!!selectedNode}
        onClose={() => setSelectedNode(null)}
      />
    </>
  )
}
```

**特点**: 已自动集成到 `CausalGraphViewer`，点击图谱节点即可弹出详情。

---

### 方式 3: 独立使用

```jsx
import { useState } from 'react'
import NodeDetailDrawer from './components/NodeDetailDrawer'
import { fedRateHikeData } from './components/NodeDetailDrawer.testData'

function MyComponent() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      <button onClick={() => setIsOpen(true)}>
        查看详情
      </button>

      <NodeDetailDrawer
        nodeData={fedRateHikeData}
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
      />
    </>
  )
}
```

---

## 🧪 测试数据说明

`NodeDetailDrawer.testData.js` 提供了 6 个测试场景：

| 场景 | 说明 | 数据完整度 |
|------|------|-----------|
| `fedRateHikeData` | 美联储加息 | ⭐⭐⭐⭐⭐ 完整 |
| `chinaRealEstateData` | 中国房地产 | ⭐⭐⭐⭐⭐ 完整 |
| `aiTechData` | AI 技术 | ⭐⭐⭐⭐⭐ 完整 |
| `minimalData` | 最小化 | ⭐ 仅标题 |
| `topologyOnlyData` | 供应链 | ⭐⭐⭐ 元信息+拓扑 |
| `temporalOnlyData` | 气候变化 | ⭐⭐⭐⭐ 元信息+时间动态 |

使用方式：

```jsx
import testDataCollection from './components/NodeDetailDrawer.testData'

// 使用完整数据
<NodeDetailDrawer nodeData={testDataCollection.fedRateHike} />

// 使用最小化数据
<NodeDetailDrawer nodeData={testDataCollection.minimal} />
```

---

## 🎨 自定义样式

### 修改抽屉宽度

```jsx
// NodeDetailDrawer.jsx 第 280 行
<div className="fixed right-0 top-0 h-screen w-[420px] ...">
  {/* 改为 w-[500px] 或其他宽度 */}
</div>
```

### 修改风险等级颜色

```jsx
// NodeDetailDrawer.jsx DrawerHeader 组件
const getRiskColor = (level) => {
  const colors = {
    high: 'bg-red-100 text-red-700 border-red-300',
    medium: 'bg-amber-100 text-amber-700 border-amber-300',
    low: 'bg-green-100 text-green-700 border-green-300'
  }
  return colors[level] || colors.medium
}
```

### 修改置信度阈值

```jsx
// NodeDetailDrawer.jsx EvidenceSection 组件
const getConfidenceColor = (score) => {
  if (score >= 0.8) return 'bg-green-500'  // 高置信度
  if (score >= 0.6) return 'bg-amber-500'  // 中等置信度
  return 'bg-red-500'                       // 低置信度
}
```

---

## 🔧 与后端数据对接

如果你的后端返回的数据结构不同，需要进行转换：

```jsx
// 示例：转换后端数据
function transformBackendData(backendNode) {
  return {
    meta: {
      title: backendNode.name,
      category: backendNode.category,
      risk_level: backendNode.risk,
      current_metric: {
        label: backendNode.metric_name,
        value: backendNode.metric_value,
        trend: backendNode.trend
      }
    },
    topology: {
      causes: backendNode.upstream_nodes,
      effects: backendNode.downstream_nodes
    },
    temporal_dynamics: backendNode.temporal_data,
    evidence: {
      confidence_score: backendNode.confidence,
      sources: backendNode.news_sources
    }
  }
}

// 使用转换后的数据
const transformedData = transformBackendData(rawBackendData)
<NodeDetailDrawer nodeData={transformedData} />
```

---

## 📱 响应式支持

组件默认宽度为 420px，适合桌面端。如需移动端支持：

```jsx
// 添加响应式类名
<div className="fixed right-0 top-0 h-screen w-full sm:w-[420px] ...">
```

---

## ⚡ 性能优化建议

### 1. 懒加载组件

```jsx
import { lazy, Suspense } from 'react'

const NodeDetailDrawer = lazy(() => import('./components/NodeDetailDrawer'))

function App() {
  return (
    <Suspense fallback={<div>加载中...</div>}>
      <NodeDetailDrawer {...props} />
    </Suspense>
  )
}
```

### 2. 使用 memo 优化

```jsx
import { memo } from 'react'

const NodeDetailDrawer = memo(function NodeDetailDrawer({ nodeData, isOpen, onClose }) {
  // ...
}, (prevProps, nextProps) => {
  return prevProps.isOpen === nextProps.isOpen && 
         prevProps.nodeData === nextProps.nodeData
})
```

---

## 🐛 常见问题

### Q1: 抽屉不显示？

检查 `isOpen` 和 `nodeData` 是否正确传递：

```jsx
console.log('isOpen:', isOpen)
console.log('nodeData:', nodeData)
```

### Q2: 样式错乱？

确保 Tailwind CSS 已正确配置，检查 `tailwind.config.js`：

```js
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  // ...
}
```

### Q3: 图标不显示？

确认 lucide-react 已安装：

```bash
npm install lucide-react
```

### Q4: 点击遮罩层无法关闭？

检查 `onClose` 回调是否正确绑定：

```jsx
<NodeDetailDrawer
  onClose={() => {
    console.log('关闭抽屉')
    setIsOpen(false)
  }}
/>
```

---

## 📚 更多资源

- **完整文档**: `NodeDetailDrawer.README.md`
- **测试数据**: `NodeDetailDrawer.testData.js`
- **使用示例**: `NodeDetailDrawer.example.jsx`
- **演示页面**: `NodeDetailDrawerDemo.jsx`

---

## 🎉 开始使用

最快的方式是运行演示页面：

```bash
# 1. 进入前端目录
cd frontend

# 2. 启动开发服务器
npm run dev

# 3. 在 App.jsx 中导入演示页面
# import NodeDetailDrawerDemo from './NodeDetailDrawerDemo'
# function App() { return <NodeDetailDrawerDemo /> }

# 4. 访问 http://localhost:5173
```

点击任意卡片即可查看详情抽屉效果！

---

**祝你使用愉快！** 🚀












