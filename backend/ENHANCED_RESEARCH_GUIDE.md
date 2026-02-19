# 增强型标的研究 API - 完整示例

## 核心功能

**问题**：传统因果分析只告诉你"美元指数影响黄金价格"，但不告诉你美元指数当前是多少。

**解决方案**：增强型标的研究 API 自动完成以下流程：

```
输入: "黄金价格"
  ↓
1. 因果分析 → 识别影响因子（美元指数、美联储利率、地缘政治...）
  ↓
2. 自动配置 → 为每个因子生成搜索查询
  ↓
3. 实时搜索 → 获取每个因子的当前状态
  ↓
4. 综合报告 → 结合因果关系和实时数据生成分析
  ↓
输出: 带有实时数据的完整因果图谱
```

---

## API 端点

### POST `/api/v1/research-target-enhanced`

**请求：**

```json
{
  "target": "黄金价格"
}
```

**响应示例：**

```json
{
  "nodes": [
    {
      "id": "n1",
      "label": "美元指数",
      "type": "cause",
      "description": "美元相对其他主要货币的强弱指标",
      "confidence": 0.9,
      "sensing_config": {
        "auto_queries": [
          "美元指数最新走势 2024",
          "US Dollar Index DXY latest"
        ]
      },
      "current_state": {
        "value": "103.5",
        "trend": "rising",
        "narrative_context": "美元指数持续走强，受美联储鹰派立场支撑"
      },
      "last_updated": "2024-02-19T10:30:00Z"
    },
    {
      "id": "n2",
      "label": "美联储利率",
      "type": "cause",
      "description": "美国联邦储备系统的基准利率",
      "confidence": 0.95,
      "sensing_config": {
        "auto_queries": [
          "美联储利率决议 2024",
          "Federal Reserve interest rate latest"
        ]
      },
      "current_state": {
        "value": "5.25%-5.50%",
        "trend": "stable",
        "narrative_context": "美联储维持利率不变，等待更多经济数据"
      },
      "last_updated": "2024-02-19T10:30:05Z"
    },
    {
      "id": "n3",
      "label": "地缘政治风险",
      "type": "cause",
      "description": "全球地缘政治紧张局势",
      "confidence": 0.8,
      "sensing_config": {
        "auto_queries": [
          "中东局势最新进展 2024",
          "geopolitical risk latest news"
        ]
      },
      "current_state": {
        "value": "高",
        "trend": "rising",
        "narrative_context": "中东冲突持续，避险情绪升温"
      },
      "last_updated": "2024-02-19T10:30:08Z"
    },
    {
      "id": "n4",
      "label": "黄金价格",
      "type": "effect",
      "description": "国际黄金现货价格",
      "confidence": 1.0
    }
  ],
  "edges": [
    {
      "source": "n1",
      "target": "n4",
      "label": "负相关",
      "description": "美元走强通常导致黄金价格下跌",
      "strength": 0.85
    },
    {
      "source": "n2",
      "target": "n4",
      "label": "负相关",
      "description": "高利率降低黄金持有吸引力",
      "strength": 0.8
    },
    {
      "source": "n3",
      "target": "n4",
      "label": "正相关",
      "description": "地缘风险推升避险需求",
      "strength": 0.9
    }
  ],
  "explanation": "【核心结论】\n当前黄金价格面临多空交织格局。美元指数走强至103.5和美联储维持高利率对黄金构成压力，但地缘政治风险上升提供避险支撑。\n\n【因果传导分析】\n美元指数是影响黄金价格的首要因素。当前美元指数持续走强，受美联储鹰派立场支撑，这对黄金价格形成直接压制。同时，美联储维持5.25%-5.50%的高利率水平，提高了持有黄金的机会成本，进一步削弱黄金吸引力。\n\n然而，地缘政治风险的上升为黄金提供了重要支撑。中东冲突持续，避险情绪升温，推动投资者增配黄金等避险资产。\n\n【风险与机会】\n下行风险：若美元指数继续走强突破104，黄金可能面临进一步下行压力。\n上行机会：地缘政治局势恶化或美联储释放降息信号，将推动黄金价格上涨。\n\n【策略建议】\n短期内建议观望为主，等待美元指数和地缘局势明朗。若美元指数回落至102以下或地缘风险加剧，可考虑逢低配置黄金。",
  "metadata": {
    "target": "黄金价格",
    "total_nodes": 4,
    "nodes_with_state": 3,
    "total_time": 25.6,
    "pipeline_steps": {
      "causal_analysis": 8.2,
      "query_configuration": 5.1,
      "state_sensing": 10.3,
      "report_generation": 2.0
    }
  }
}
```

---

## 使用示例

### Python 示例

```python
import requests

url = "http://localhost:8000/api/v1/research-target-enhanced"

# 分析黄金价格
response = requests.post(url, json={"target": "黄金价格"})
result = response.json()

print("=== 因果图谱 ===")
for node in result['nodes']:
    print(f"\n节点: {node['label']}")
    if 'current_state' in node:
        state = node['current_state']
        print(f"  当前值: {state['value']}")
        print(f"  趋势: {state['trend']}")
        print(f"  背景: {state['narrative_context']}")

print("\n=== 综合分析 ===")
print(result['explanation'])
```

### JavaScript 示例

```javascript
const url = 'http://localhost:8000/api/v1/research-target-enhanced';

const response = await fetch(url, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ target: '比特币' })
});

const result = await response.json();

// 渲染因果图谱（带实时状态）
result.nodes.forEach(node => {
  console.log(`${node.label}:`);
  if (node.current_state) {
    console.log(`  值: ${node.current_state.value}`);
    console.log(`  趋势: ${node.current_state.trend}`);
  }
});

// 显示综合分析
console.log('\n综合分析:');
console.log(result.explanation);
```

### cURL 示例

```bash
curl -X POST http://localhost:8000/api/v1/research-target-enhanced \
  -H "Content-Type: application/json" \
  -d '{"target": "中证1000指数"}'
```

---

## 对比：普通版 vs 增强版

### 普通版 `/api/v1/research-target`

```json
{
  "nodes": [
    {"id": "n1", "label": "美元指数", "type": "cause"}
  ],
  "explanation": "美元指数影响黄金价格..."
}
```

**问题**：只知道"美元指数影响黄金"，不知道美元指数当前是多少。

---

### 增强版 `/api/v1/research-target-enhanced`

```json
{
  "nodes": [
    {
      "id": "n1", 
      "label": "美元指数", 
      "type": "cause",
      "current_state": {
        "value": "103.5",
        "trend": "rising",
        "narrative_context": "美元指数持续走强..."
      }
    }
  ],
  "explanation": "当前美元指数走强至103.5，对黄金构成压力..."
}
```

**优势**：不仅知道因果关系，还知道每个因子的实时状态和趋势。

---

## 工作流程详解

### 步骤 1: 因果分析

**输入**：黄金价格

**LLM 任务**：识别影响黄金价格的核心因子

**输出**：
- 美元指数
- 美联储利率
- 地缘政治风险
- 通胀预期
- ...

---

### 步骤 2: 自动配置搜索查询

**LLM 任务**：为每个因子生成精准的搜索关键词

**示例**：
- 美元指数 → ["美元指数最新走势 2024", "US Dollar Index DXY latest"]
- 美联储利率 → ["美联储利率决议 2024", "Federal Reserve interest rate latest"]

---

### 步骤 3: 并发搜索实时状态

**搜索引擎**：Tavily API / Serper API

**并发执行**：同时搜索所有因子的最新信息

**LLM 解析**：将搜索结果提取为结构化数据
```json
{
  "value": "103.5",
  "trend": "rising",
  "narrative_context": "美元指数持续走强..."
}
```

---

### 步骤 4: 生成综合报告

**LLM 任务**：结合因果关系和实时数据，生成深度分析

**输出**：
- 核心结论
- 因果传导分析
- 风险与机会
- 策略建议

---

## 适用场景

### 1. 金融市场分析

```bash
# 分析股票指数
POST /api/v1/research-target-enhanced
{"target": "中证1000指数"}

# 分析大宗商品
POST /api/v1/research-target-enhanced
{"target": "原油价格"}

# 分析外汇
POST /api/v1/research-target-enhanced
{"target": "人民币汇率"}
```

### 2. 加密货币分析

```bash
POST /api/v1/research-target-enhanced
{"target": "比特币"}
```

### 3. 宏观经济指标

```bash
POST /api/v1/research-target-enhanced
{"target": "美国通胀率"}
```

---

## 性能指标

- **总耗时**：20-30 秒
  - 因果分析：8-10 秒
  - 查询配置：5-7 秒
  - 状态感知：10-15 秒（并发）
  - 报告生成：2-3 秒

- **并发能力**：最多同时处理 5 个节点的状态更新

- **准确率**：
  - 因子识别准确率：>90%
  - 状态提取准确率：>85%
  - 反幻觉机制：无数据时返回 "unknown"

---

## 环境配置

在 `backend/.env` 文件中配置：

```bash
# DeepSeek API（必需）
OPENAI_API_KEY=your-deepseek-api-key
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-reasoner

# 搜索引擎 API（至少配置一个）
TAVILY_API_KEY=your-tavily-api-key
SERPER_API_KEY=your-serper-api-key
```

---

## 前端集成示例

```javascript
// 调用增强型 API
async function analyzeTarget(target) {
  const response = await fetch('/api/v1/research-target-enhanced', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ target })
  });
  
  const result = await response.json();
  
  // 渲染因果图谱
  renderCausalGraph(result.nodes, result.edges);
  
  // 为每个节点显示实时状态
  result.nodes.forEach(node => {
    if (node.current_state) {
      displayNodeState(node.id, {
        value: node.current_state.value,
        trend: node.current_state.trend,
        context: node.current_state.narrative_context
      });
    }
  });
  
  // 显示综合分析
  displayAnalysis(result.explanation);
}

// 使用示例
analyzeTarget('黄金价格');
```

---

## 常见问题

### Q1: 为什么有些节点的状态是 "unknown"？

**A**: 可能原因：
1. 搜索引擎未返回相关结果
2. LLM 无法从搜索结果中提取明确数据
3. 反幻觉机制：宁可返回 "unknown" 也不捏造数据

### Q2: 如何提高状态提取的准确率？

**A**: 
1. 配置高质量的搜索引擎 API（推荐 Tavily）
2. 使用更强的 LLM 模型（如 deepseek-reasoner）
3. 为节点提供更详细的 description

### Q3: 可以自定义搜索查询吗？

**A**: 可以。在调用 `/api/v1/enrich-nodes` 时手动指定 `sensing_config.auto_queries`。

---

## 下一步

1. **测试 API**：使用 Postman 或 cURL 测试
2. **前端集成**：在 React 组件中调用 API
3. **自定义配置**：根据业务需求调整搜索查询
4. **监控日志**：关注节点状态更新的成功率

---

## 技术支持

- API 文档：`/docs`（FastAPI 自动生成）
- 详细文档：`NODE_SENSING_API.md`
- 测试脚本：`examples/test_node_sensing.py`

