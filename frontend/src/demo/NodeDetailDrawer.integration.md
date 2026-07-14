# NodeDetailDrawer 集成指南

## 与 CausalGraphViewer 集成

NodeDetailDrawer 已自动集成到 `CausalGraphViewer.jsx` 中，替代了原有的 Sidebar 组件。

### 集成代码

```jsx
// CausalGraphViewer.jsx
import NodeDetailDrawer from './NodeDetailDrawer'

function CausalGraphViewer({ analysisResult }) {
  const [selectedNode, setSelectedNode] = useState(null)

  const handleNodeClick = useCallback((event, node) => {
    // 设置选中节点（用于详情抽屉展示）
    setSelectedNode(node.data.originalData)
  }, [])

  return (
    <div className="relative w-full h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodeClick={handleNodeClick}
      />

      {/* 使用 NodeDetailDrawer 替代 Sidebar */}
      <NodeDetailDrawer
        nodeData={selectedNode}
        isOpen={!!selectedNode}
        onClose={() => setSelectedNode(null)}
      />
    </div>
  )
}
```

---

## 数据格式要求

### 后端需要返回的节点数据结构

为了让 NodeDetailDrawer 正常工作，后端返回的节点数据应包含以下字段：

```typescript
interface NodeData {
  // 必需字段
  meta: {
    title: string                    // 节点标题
    category?: string                // 分类标签
    risk_level?: 'high' | 'medium' | 'low'  // 风险等级
    current_metric?: {               // 当前指标
      label: string
      value: string
      trend: 'up' | 'down' | 'stable'
    }
  }

  // 可选字段
  topology?: {
    causes?: string[]                // 上游原因节点
    effects?: string[]               // 下游结果节点
  }

  temporal_dynamics?: {
    past?: {
      summary: string                // 历史回顾
    }
    present?: {
      summary: string                // 当前状态
    }
    future?: {
      base_case?: {                  // 基准情景
        title: string
        probability: string
        description: string
        key_metrics?: Array<{
          label: string
          value: string
        }>
      }
      tail_risk?: {                  // 尾部风险
        title: string
        probability: string
        description: string
        key_metrics?: Array<{
          label: string
          value: string
        }>
      }
    }
  }

  evidence?: {
    confidence_score?: number        // AI 置信度 (0-1)
    sources?: Array<{                // 新闻来源
      title: string
      url: string
      date: string
    }>
  }
}
```

---

## 后端 API 示例

### Python FastAPI 示例

```python
from pydantic import BaseModel
from typing import List, Optional

class CurrentMetric(BaseModel):
    label: str
    value: str
    trend: str  # 'up' | 'down' | 'stable'

class Meta(BaseModel):
    title: str
    category: Optional[str] = None
    risk_level: Optional[str] = None  # 'high' | 'medium' | 'low'
    current_metric: Optional[CurrentMetric] = None

class Topology(BaseModel):
    causes: Optional[List[str]] = None
    effects: Optional[List[str]] = None

class KeyMetric(BaseModel):
    label: str
    value: str

class Scenario(BaseModel):
    title: str
    probability: str
    description: str
    key_metrics: Optional[List[KeyMetric]] = None

class Future(BaseModel):
    base_case: Optional[Scenario] = None
    tail_risk: Optional[Scenario] = None

class TemporalPhase(BaseModel):
    summary: str

class TemporalDynamics(BaseModel):
    past: Optional[TemporalPhase] = None
    present: Optional[TemporalPhase] = None
    future: Optional[Future] = None

class Source(BaseModel):
    title: str
    url: str
    date: str

class Evidence(BaseModel):
    confidence_score: Optional[float] = None
    sources: Optional[List[Source]] = None

class NodeDetailData(BaseModel):
    meta: Meta
    topology: Optional[Topology] = None
    temporal_dynamics: Optional[TemporalDynamics] = None
    evidence: Optional[Evidence] = None

# API 端点
@app.get("/api/node/{node_id}/detail")
async def get_node_detail(node_id: str) -> NodeDetailData:
    # 查询节点详情
    node = await fetch_node_from_db(node_id)
    
    return NodeDetailData(
        meta=Meta(
            title=node.title,
            category=node.category,
            risk_level=node.risk_level,
            current_metric=CurrentMetric(
                label="当前指标",
                value=node.metric_value,
                trend=node.trend
            )
        ),
        topology=Topology(
            causes=node.upstream_nodes,
            effects=node.downstream_nodes
        ),
        temporal_dynamics=TemporalDynamics(
            past=TemporalPhase(summary=node.past_summary),
            present=TemporalPhase(summary=node.present_summary),
            future=Future(
                base_case=Scenario(
                    title="基准情景",
                    probability="65%",
                    description=node.base_case_desc,
                    key_metrics=[
                        KeyMetric(label="指标1", value="值1")
                    ]
                )
            )
        ),
        evidence=Evidence(
            confidence_score=node.confidence,
            sources=[
                Source(
                    title=source.title,
                    url=source.url,
                    date=source.date
                )
                for source in node.sources
            ]
        )
    )
```

---

## 前端数据转换

如果后端数据结构与组件要求不完全一致，可以在前端进行转换：

```jsx
// utils/nodeDataTransform.js

/**
 * 转换后端节点数据为 NodeDetailDrawer 所需格式
 */
export function transformNodeData(backendNode) {
  if (!backendNode) return null

  return {
    meta: {
      title: backendNode.name || backendNode.label || '未命名节点',
      category: backendNode.category || backendNode.type,
      risk_level: mapRiskLevel(backendNode.risk),
      current_metric: backendNode.current_value ? {
        label: backendNode.metric_name || '当前值',
        value: backendNode.current_value,
        trend: backendNode.trend || 'stable'
      } : undefined
    },
    
    topology: (backendNode.causes || backendNode.effects) ? {
      causes: backendNode.causes || backendNode.upstream_nodes,
      effects: backendNode.effects || backendNode.downstream_nodes
    } : undefined,
    
    temporal_dynamics: backendNode.temporal ? {
      past: backendNode.temporal.past ? {
        summary: backendNode.temporal.past
      } : undefined,
      present: backendNode.temporal.present ? {
        summary: backendNode.temporal.present
      } : undefined,
      future: backendNode.temporal.future ? {
        base_case: backendNode.temporal.future.base_case,
        tail_risk: backendNode.temporal.future.tail_risk
      } : undefined
    } : undefined,
    
    evidence: {
      confidence_score: backendNode.confidence,
      sources: backendNode.sources || backendNode.news_sources
    }
  }
}

/**
 * 映射风险等级
 */
function mapRiskLevel(risk) {
  if (typeof risk === 'number') {
    if (risk >= 0.7) return 'high'
    if (risk >= 0.4) return 'medium'
    return 'low'
  }
  return risk // 'high' | 'medium' | 'low'
}
```

### 在 CausalGraphViewer 中使用转换函数

```jsx
import { transformNodeData } from '../utils/nodeDataTransform'

function CausalGraphViewer({ analysisResult }) {
  const [selectedNode, setSelectedNode] = useState(null)

  const handleNodeClick = useCallback((event, node) => {
    // 转换后端数据
    const transformedData = transformNodeData(node.data.originalData)
    setSelectedNode(transformedData)
  }, [])

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

---

## 完整集成流程

### 1. 后端准备

```python
# backend/app/api/causal_router.py

@router.get("/node/{node_id}/detail")
async def get_node_detail(node_id: str):
    """获取节点详细信息"""
    # 实现节点详情查询逻辑
    return {
        "meta": {
            "title": "节点标题",
            "category": "分类",
            "risk_level": "high",
            "current_metric": {
                "label": "指标名",
                "value": "指标值",
                "trend": "up"
            }
        },
        # ... 其他字段
    }
```

### 2. 前端调用

```jsx
// services/nodeService.js

export async function fetchNodeDetail(nodeId) {
  const response = await fetch(`/api/node/${nodeId}/detail`)
  return response.json()
}
```

### 3. 组件集成

```jsx
// CausalGraphViewer.jsx

import { fetchNodeDetail } from '../services/nodeService'

function CausalGraphViewer() {
  const [selectedNode, setSelectedNode] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleNodeClick = useCallback(async (event, node) => {
    setIsLoading(true)
    try {
      // 从后端获取详细数据
      const detailData = await fetchNodeDetail(node.id)
      setSelectedNode(detailData)
    } catch (error) {
      console.error('获取节点详情失败:', error)
    } finally {
      setIsLoading(false)
    }
  }, [])

  return (
    <>
      <ReactFlow onNodeClick={handleNodeClick} />
      
      {isLoading && <LoadingSpinner />}
      
      <NodeDetailDrawer
        nodeData={selectedNode}
        isOpen={!!selectedNode}
        onClose={() => setSelectedNode(null)}
      />
    </>
  )
}
```

---

## 测试集成

### 使用测试数据验证

```jsx
import { fedRateHikeData } from './components/NodeDetailDrawer.testData'

function TestIntegration() {
  const [selectedNode, setSelectedNode] = useState(null)

  return (
    <>
      <button onClick={() => setSelectedNode(fedRateHikeData)}>
        测试打开抽屉
      </button>

      <NodeDetailDrawer
        nodeData={selectedNode}
        isOpen={!!selectedNode}
        onClose={() => setSelectedNode(null)}
      />
    </>
  )
}
```

---

## 注意事项

1. **数据验证**: 确保后端返回的数据符合格式要求
2. **错误处理**: 添加适当的错误处理和加载状态
3. **性能优化**: 对于大量节点，考虑按需加载详情数据
4. **缓存策略**: 可以缓存已加载的节点详情，避免重复请求

---

## 下一步

- 查看 `NODEDETAILDRAWER_QUICKSTART.md` 了解快速启动
- 查看 `NodeDetailDrawer.README.md` 了解完整文档
- 运行 `NodeDetailDrawerDemo.jsx` 查看演示效果












