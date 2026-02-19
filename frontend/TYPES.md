# TypeScript 类型定义文档

## 📋 概述

为因果推演引擎定义了完整的 TypeScript 接口，确保类型安全并完美适配 React Flow。

## 📁 文件结构

```
frontend/src/
├── types/
│   └── causal.ts          # 核心类型定义
├── utils/
│   └── graphUtils.ts      # 转换和工具函数
└── examples/
    └── usage.ts           # 使用示例
```

## 🎯 核心类型

### 1. NodeType（节点类型枚举）

```typescript
export enum NodeType {
  CAUSE = 'cause',           // 原因节点
  EFFECT = 'effect',         // 结果节点
  INTERMEDIATE = 'intermediate', // 中间节点
  HYPOTHESIS = 'hypothesis', // 假设节点
  EVIDENCE = 'evidence'      // 证据节点
}
```

### 2. CausalNodeData（节点数据）

```typescript
export interface CausalNodeData {
  id: string              // 唯一标识
  label: string           // 显示标签
  type: NodeType          // 节点类型
  description?: string    // 详细描述
  confidence?: number     // 置信度 0-1
  metadata?: Record<string, any>  // 扩展元数据
}
```

### 3. CausalEdgeData（边数据）

```typescript
export interface CausalEdgeData {
  source: string          // 源节点 ID
  target: string          // 目标节点 ID
  label?: string          // 边标签
  description?: string    // 关系描述
  strength?: number       // 因果强度 0-1
  strengthLevel?: EdgeStrength  // 强度等级
  bidirectional?: boolean // 是否双向
  metadata?: Record<string, any>
}
```

### 4. AnalysisResult（分析结果）

```typescript
export interface AnalysisResult {
  nodes: CausalNodeData[]  // 节点列表
  edges: CausalEdgeData[]  // 边列表
  explanation: string      // 文字解释
  query?: string          // 原始查询
  timestamp?: string      // 时间戳
  metadata?: {
    depth?: number
    totalNodes?: number
    totalEdges?: number
    analysisTime?: number
  }
}
```

## 🔧 工具函数

### convertAnalysisResult()

将后端返回的数据转换为 React Flow 格式：

```typescript
const { nodes, edges } = convertAnalysisResult(result, 'horizontal')
```

### validateGraphData()

验证图数据的完整性：

```typescript
const validation = validateGraphData(result)
if (!validation.valid) {
  console.error('验证失败:', validation.errors)
}
```

### exportGraphData()

导出图数据为 JSON：

```typescript
const jsonData = exportGraphData(result, nodes, edges)
```

## 🎨 样式配置

### 节点样式

- **原因节点**: 红色 (#ef4444)
- **结果节点**: 绿色 (#10b981)
- **中间节点**: 蓝色 (#3b82f6)
- **假设节点**: 橙色 (#f59e0b)
- **证据节点**: 紫色 (#8b5cf6)

### 边样式

- **弱关联** (0-0.3): 细线，低透明度
- **中等关联** (0.3-0.7): 中等粗细
- **强关联** (0.7-1.0): 粗线，带动画

## 📝 使用示例

### 基础用法

```typescript
import { AnalysisResult } from './types/causal'
import { convertAnalysisResult } from './utils/graphUtils'

// 后端返回的数据
const result: AnalysisResult = {
  nodes: [
    { id: 'n1', label: '全球变暖', type: NodeType.CAUSE },
    { id: 'n2', label: '海平面上升', type: NodeType.EFFECT }
  ],
  edges: [
    { source: 'n1', target: 'n2', strength: 0.9 }
  ],
  explanation: '因果关系说明'
}

// 转换为 React Flow 格式
const { nodes, edges } = convertAnalysisResult(result)
```

### 在 React 组件中使用

```typescript
function CausalGraph() {
  const [graphData, setGraphData] = useState<AnalysisResult | null>(null)
  
  const handleAnalyze = async (query: string) => {
    const response = await fetch('/api/v1/analyze', {
      method: 'POST',
      body: JSON.stringify({ query, max_depth: 3 })
    })
    const result: AnalysisResult = await response.json()
    setGraphData(result)
  }
  
  const { nodes, edges } = graphData 
    ? convertAnalysisResult(graphData) 
    : { nodes: [], edges: [] }
  
  return <ReactFlow nodes={nodes} edges={edges} />
}
```

## 🔄 数据流

```
用户输入查询
    ↓
CausalQuery → 后端 API
    ↓
AnalysisResult ← 后端返回
    ↓
convertAnalysisResult() → 转换
    ↓
CausalFlowNode[] + CausalFlowEdge[]
    ↓
React Flow 渲染
```

## ✅ 类型安全优势

1. **编译时检查**: TypeScript 在编译时捕获类型错误
2. **智能提示**: IDE 提供完整的代码补全
3. **重构安全**: 修改接口时自动检测影响范围
4. **文档化**: 类型定义即文档
5. **可维护性**: 清晰的数据结构便于团队协作

## 🚀 扩展建议

### 添加新节点类型

```typescript
// 在 NodeType 枚举中添加
export enum NodeType {
  // ... 现有类型
  CONDITION = 'condition',  // 条件节点
}

// 在 NODE_STYLES 中添加样式
export const NODE_STYLES = {
  // ... 现有样式
  [NodeType.CONDITION]: {
    color: '#ffffff',
    bgColor: '#06b6d4',
    borderColor: 'rgba(6, 182, 212, 0.5)',
  },
}
```

### 添加自定义元数据

```typescript
interface CustomNodeData extends CausalNodeData {
  metadata: {
    source?: string      // 数据来源
    timestamp?: string   // 时间信息
    tags?: string[]      // 标签
  }
}
```

## 📚 相关文件

- `frontend/src/types/causal.ts` - 类型定义
- `frontend/src/utils/graphUtils.ts` - 工具函数
- `frontend/src/examples/usage.ts` - 使用示例
- `frontend/src/components/CausalGraph.jsx` - 图谱组件

## 🎯 最佳实践

1. **始终验证数据**: 使用 `validateGraphData()` 验证后端返回的数据
2. **类型断言谨慎使用**: 尽量避免 `as` 类型断言
3. **使用枚举**: 用 `NodeType` 枚举代替字符串字面量
4. **扩展而非修改**: 通过继承接口来扩展类型
5. **保持一致性**: 前后端使用相同的数据结构

---

现在你的项目拥有完整的类型系统，可以安全地开发因果推演功能了！🎉








