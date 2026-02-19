# 节点自主感知 API 文档

## 概述

节点自主感知（Autonomous Node Sensing）功能允许因果图谱中的节点自动获取最新的实时状态信息。系统会根据节点配置的搜索查询，自动调用搜索引擎 API，并使用 LLM 将搜索结果解析为结构化数据。

---

## API 端点

### POST `/api/v1/enrich-nodes`

批量更新节点的实时状态。

**请求体：**

```json
{
  "nodes": [
    {
      "id": "n1",
      "label": "美联储利率",
      "type": "cause",
      "description": "美国联邦储备系统的基准利率",
      "sensing_config": {
        "auto_queries": [
          "美联储最新利率决议 2024",
          "Federal Reserve interest rate latest"
        ]
      }
    },
    {
      "id": "n2",
      "label": "黄金价格",
      "type": "intermediate",
      "sensing_config": {
        "auto_queries": [
          "黄金价格最新行情",
          "gold price today USD"
        ]
      }
    }
  ]
}
```

**响应：**

```json
{
  "success": true,
  "total": 2,
  "nodes": [
    {
      "id": "n1",
      "label": "美联储利率",
      "type": "cause",
      "description": "美国联邦储备系统的基准利率",
      "sensing_config": {
        "auto_queries": [
          "美联储最新利率决议 2024",
          "Federal Reserve interest rate latest"
        ]
      },
      "current_state": {
        "value": "5.25%-5.50%",
        "trend": "stable",
        "narrative_context": "美联储维持利率不变，等待更多经济数据"
      },
      "last_updated": "2024-02-19T10:30:00Z"
    },
    {
      "id": "n2",
      "label": "黄金价格",
      "type": "intermediate",
      "sensing_config": {
        "auto_queries": [
          "黄金价格最新行情",
          "gold price today USD"
        ]
      },
      "current_state": {
        "value": "2025美元/盎司",
        "trend": "rising",
        "narrative_context": "地缘政治紧张推动避险需求上升"
      },
      "last_updated": "2024-02-19T10:30:05Z"
    }
  ]
}
```

---

## 节点配置说明

### sensing_config 字段

每个需要自动更新状态的节点必须包含 `sensing_config` 配置：

```json
{
  "sensing_config": {
    "auto_queries": [
      "查询关键词1",
      "查询关键词2",
      "查询关键词3"
    ]
  }
}
```

**配置建议：**

1. **查询数量**：建议 2-3 个查询，覆盖中英文
2. **查询精度**：包含时间限定词（如 "2024"、"latest"、"最新"）
3. **查询多样性**：使用不同角度的关键词提高召回率

**示例配置：**

```json
// 金融指标
{
  "auto_queries": [
    "美联储利率决议 2024",
    "Federal Reserve interest rate decision latest"
  ]
}

// 商品价格
{
  "auto_queries": [
    "原油价格今日行情",
    "crude oil price today Brent"
  ]
}

// 经济指标
{
  "auto_queries": [
    "美国CPI数据最新",
    "US CPI inflation rate 2024"
  ]
}

// 地缘政治
{
  "auto_queries": [
    "中东局势最新进展",
    "Middle East conflict latest news"
  ]
}
```

---

## current_state 字段说明

更新后的节点会包含 `current_state` 字段：

```typescript
interface CurrentState {
  value: string;              // 当前值或状态描述
  trend: "rising" | "falling" | "stable";  // 趋势
  narrative_context: string;  // 背景说明
}
```

### value 字段

- **有明确数值**：提取具体数值（如 `"5.25%"`, `"2025美元/盎司"`）
- **无明确数值**：使用描述性文字（如 `"持续上涨"`, `"保持稳定"`）
- **无法确定**：设为 `"unknown"`（反幻觉机制）

### trend 字段

只能是以下三个值之一：

- `"rising"` - 上升趋势
- `"falling"` - 下降趋势
- `"stable"` - 稳定/持平

### narrative_context 字段

一句话总结当前状态的背景原因，基于搜索结果提取。

---

## 环境变量配置

在 `backend/.env` 文件中添加搜索引擎 API 密钥：

```bash
# DeepSeek API（必需）
OPENAI_API_KEY=your-deepseek-api-key
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-reasoner

# Tavily API（推荐，专为 LLM 设计）
TAVILY_API_KEY=your-tavily-api-key

# Serper API（备用）
SERPER_API_KEY=your-serper-api-key
```

### 获取 API 密钥

**Tavily API（推荐）：**
- 官网：https://tavily.com
- 特点：专为 LLM 设计，返回结构化数据
- 免费额度：1000 次/月

**Serper API（备用）：**
- 官网：https://serper.dev
- 特点：Google 搜索 API 封装
- 免费额度：2500 次/月

---

## 使用示例

### Python 示例

```python
import requests

url = "http://localhost:8000/api/v1/enrich-nodes"

payload = {
    "nodes": [
        {
            "id": "n1",
            "label": "比特币价格",
            "type": "intermediate",
            "sensing_config": {
                "auto_queries": [
                    "比特币价格最新",
                    "Bitcoin price today USD"
                ]
            }
        }
    ]
}

response = requests.post(url, json=payload)
result = response.json()

print(f"更新成功: {result['success']}")
print(f"节点状态: {result['nodes'][0]['current_state']}")
```

### JavaScript 示例

```javascript
const url = 'http://localhost:8000/api/v1/enrich-nodes';

const payload = {
  nodes: [
    {
      id: 'n1',
      label: '美元指数',
      type: 'cause',
      sensing_config: {
        auto_queries: [
          '美元指数最新走势',
          'US Dollar Index DXY latest'
        ]
      }
    }
  ]
};

const response = await fetch(url, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload)
});

const result = await response.json();
console.log('更新后的节点:', result.nodes);
```

### cURL 示例

```bash
curl -X POST http://localhost:8000/api/v1/enrich-nodes \
  -H "Content-Type: application/json" \
  -d '{
    "nodes": [
      {
        "id": "n1",
        "label": "原油价格",
        "type": "cause",
        "sensing_config": {
          "auto_queries": [
            "布伦特原油价格今日",
            "Brent crude oil price today"
          ]
        }
      }
    ]
  }'
```

---

## 工作流程

```
1. 接收节点列表
   ↓
2. 读取 sensing_config.auto_queries
   ↓
3. 并发调用搜索引擎 API
   ├─ Tavily API（优先）
   └─ Serper API（降级）
   ↓
4. 获取 Top-3 搜索结果片段
   ↓
5. 构建 LLM Prompt（搜索结果 + 系统提示词）
   ↓
6. LLM 解析为结构化 JSON
   ├─ value: 提取数值或描述
   ├─ trend: 判断趋势
   └─ narrative_context: 总结背景
   ↓
7. 验证 JSON 格式
   ├─ 必需字段检查
   ├─ trend 枚举值验证
   └─ 反幻觉机制（无数据 → unknown）
   ↓
8. 注入 current_state 到节点
   ↓
9. 返回更新后的节点列表
```

---

## 性能特性

### 并发处理

- 使用 `asyncio.gather` 并发处理多个节点
- 默认最大并发数：5（可配置）
- 单个节点失败不影响其他节点

### 超时控制

- 搜索 API 超时：10 秒
- LLM 解析超时：30 秒
- 总体超时：60 秒

### 降级策略

1. **搜索失败**：返回 `unknown` 状态，不中断流程
2. **LLM 解析失败**：返回保守的 `unknown` 状态
3. **部分节点失败**：继续处理其他节点，返回部分结果

---

## 日志示例

```
2024-02-19 10:30:00 [INFO] node_sensing_service: [批量感知] 开始处理 3 个节点
2024-02-19 10:30:00 [INFO] node_sensing_service: [节点感知] 开始处理节点: n1 (美联储利率)
2024-02-19 10:30:00 [INFO] node_sensing_service: [节点感知] 节点 n1 配置了 2 个搜索查询
2024-02-19 10:30:01 [INFO] node_sensing_service: [搜索引擎] 开始执行 2 个搜索查询
2024-02-19 10:30:02 [INFO] node_sensing_service: [搜索引擎] 搜索完成，获取 3 条有效结果
2024-02-19 10:30:02 [INFO] node_sensing_service: [LLM 解析] 开始解析节点 '美联储利率' 的状态
2024-02-19 10:30:04 [INFO] node_sensing_service: [LLM 解析] 节点 '美联储利率' 解析成功: value=5.25%-5.50%, trend=stable
2024-02-19 10:30:04 [INFO] node_sensing_service: [节点感知] 节点 n1 状态更新完成: value=5.25%-5.50%, trend=stable
2024-02-19 10:30:05 [INFO] node_sensing_service: [批量感知] 批量处理完成，成功 3 个节点
```

---

## 错误处理

### 常见错误

**1. 缺少 sensing_config**

```json
{
  "error": "节点 n1 缺少 auto_queries 配置，跳过"
}
```

**解决方案**：为节点添加 `sensing_config.auto_queries` 字段

**2. 搜索 API 密钥未配置**

```json
{
  "error": "所有搜索引擎均不可用"
}
```

**解决方案**：在 `.env` 文件中配置 `TAVILY_API_KEY` 或 `SERPER_API_KEY`

**3. LLM 返回格式错误**

```json
{
  "error": "LLM 返回缺少字段: value"
}
```

**解决方案**：系统会自动降级为 `unknown` 状态，无需人工干预

---

## 最佳实践

### 1. 查询优化

```json
// ✅ 好的查询
{
  "auto_queries": [
    "美联储利率决议 2024年2月",
    "Federal Reserve interest rate February 2024"
  ]
}

// ❌ 不好的查询
{
  "auto_queries": [
    "利率",  // 太宽泛
    "美联储"  // 缺少具体指标
  ]
}
```

### 2. 批量处理

一次请求建议不超过 10 个节点，避免超时。

### 3. 缓存策略

对于变化不频繁的节点（如政策类），可以在前端缓存 `current_state`，减少 API 调用。

### 4. 错误监控

关注日志中的 `[节点感知]` 和 `[LLM 解析]` 标签，及时发现问题。

---

## 与现有功能集成

### 在因果分析中使用

```javascript
// 1. 先进行因果分析
const analysisResult = await fetch('/api/v1/extract-causality', {
  method: 'POST',
  body: JSON.stringify({ news_text: '...' })
}).then(r => r.json());

// 2. 为节点补充实时状态
const enrichedResult = await fetch('/api/v1/enrich-nodes', {
  method: 'POST',
  body: JSON.stringify({ nodes: analysisResult.nodes })
}).then(r => r.json());

// 3. 渲染带有实时状态的因果图谱
renderGraph(enrichedResult.nodes, analysisResult.edges);
```

---

## 未来扩展

- [ ] 支持自定义搜索引擎（Google Custom Search）
- [ ] 支持时间序列数据（历史状态追踪）
- [ ] 支持多语言搜索结果解析
- [ ] 支持图片/视频等多模态数据源
- [ ] 支持 WebSocket 实时推送状态变化

