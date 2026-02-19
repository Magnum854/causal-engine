# 新闻因果关系提取 API 测试

## 测试用例 1: 经济新闻

### 请求
```bash
curl -X POST http://localhost:8000/api/v1/extract-causality \
  -H "Content-Type: application/json" \
  -d '{
    "news_text": "由于全球供应链中断和能源价格飙升，多国央行被迫提高利率以遏制通货膨胀。高利率导致企业融资成本上升，许多中小企业面临资金链断裂的风险。消费者信心下降，零售销售额连续三个月下滑，经济学家警告可能出现经济衰退。"
  }'
```

### 预期响应
```json
{
  "nodes": [
    {
      "id": "n1",
      "label": "全球供应链中断",
      "type": "cause",
      "description": "疫情和地缘政治导致的供应链问题",
      "confidence": 0.95
    },
    {
      "id": "n2",
      "label": "能源价格飙升",
      "type": "cause",
      "description": "国际能源市场价格大幅上涨",
      "confidence": 0.95
    },
    {
      "id": "n3",
      "label": "通货膨胀",
      "type": "intermediate",
      "description": "物价水平持续上涨",
      "confidence": 0.9
    },
    {
      "id": "n4",
      "label": "央行提高利率",
      "type": "intermediate",
      "description": "货币政策收紧",
      "confidence": 0.9
    },
    {
      "id": "n5",
      "label": "企业融资成本上升",
      "type": "intermediate",
      "description": "借贷成本增加",
      "confidence": 0.85
    },
    {
      "id": "n6",
      "label": "经济衰退风险",
      "type": "effect",
      "description": "经济增长放缓或负增长",
      "confidence": 0.75
    }
  ],
  "edges": [
    {
      "source": "n1",
      "target": "n3",
      "label": "直接导致",
      "description": "供应链中断推高商品价格",
      "strength": 0.9
    },
    {
      "source": "n2",
      "target": "n3",
      "label": "直接导致",
      "description": "能源价格上涨推高整体物价",
      "strength": 0.9
    },
    {
      "source": "n3",
      "target": "n4",
      "label": "迫使",
      "description": "通胀压力迫使央行加息",
      "strength": 0.85
    },
    {
      "source": "n4",
      "target": "n5",
      "label": "直接导致",
      "description": "利率上升增加借贷成本",
      "strength": 0.95
    },
    {
      "source": "n5",
      "target": "n6",
      "label": "可能引发",
      "description": "融资困难影响企业运营和经济增长",
      "strength": 0.75
    }
  ],
  "explanation": "这是一条典型的经济因果链：全球供应链中断和能源价格飙升共同推高了通货膨胀，迫使央行采取加息政策。高利率虽然能抑制通胀，但也导致企业融资成本上升，最终可能引发经济衰退。这个因果链展示了宏观经济政策的两难困境。"
}
```

## 测试用例 2: 环境新闻

### 请求
```bash
curl -X POST http://localhost:8000/api/v1/extract-causality \
  -H "Content-Type: application/json" \
  -d '{
    "news_text": "亚马逊雨林的大规模砍伐导致生物多样性急剧下降。科学家发现，森林面积减少使得当地降雨量显著降低，进一步加剧了干旱问题。干旱又导致更多树木死亡，形成恶性循环。"
  }'
```

## 测试用例 3: 科技新闻

### 请求
```bash
curl -X POST http://localhost:8000/api/v1/extract-causality \
  -H "Content-Type: application/json" \
  -d '{
    "news_text": "人工智能技术的快速发展使得自动化程度大幅提升，许多重复性工作岗位面临被取代的风险。与此同时，AI 相关的新兴职业需求激增，但现有劳动力缺乏相应技能，导致结构性失业问题加剧。政府和企业开始投资职业再培训项目，试图缓解就业市场的转型压力。"
  }'
```

## 测试用例 4: 错误处理 - 空文本

### 请求
```bash
curl -X POST http://localhost:8000/api/v1/extract-causality \
  -H "Content-Type: application/json" \
  -d '{
    "news_text": ""
  }'
```

### 预期响应
```json
{
  "detail": "数据验证失败: 新闻文本不能为空"
}
```
HTTP Status: 400

## 测试用例 5: 错误处理 - 文本过短

### 请求
```bash
curl -X POST http://localhost:8000/api/v1/extract-causality \
  -H "Content-Type: application/json" \
  -d '{
    "news_text": "短文本"
  }'
```

### 预期响应
```json
{
  "detail": [
    {
      "loc": ["body", "news_text"],
      "msg": "ensure this value has at least 10 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```
HTTP Status: 422

## Python 测试脚本

```python
import requests
import json

API_URL = "http://localhost:8000/api/v1/extract-causality"

def test_extract_causality(news_text: str):
    """测试因果关系提取 API"""
    
    response = requests.post(
        API_URL,
        json={"news_text": news_text},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print("-" * 80)
    
    return response.json()

# 测试用例
if __name__ == "__main__":
    # 测试 1: 经济新闻
    news1 = """
    由于全球供应链中断和能源价格飙升，多国央行被迫提高利率以遏制通货膨胀。
    高利率导致企业融资成本上升，许多中小企业面临资金链断裂的风险。
    消费者信心下降，零售销售额连续三个月下滑，经济学家警告可能出现经济衰退。
    """
    
    print("测试 1: 经济新闻")
    test_extract_causality(news1)
    
    # 测试 2: 环境新闻
    news2 = """
    亚马逊雨林的大规模砍伐导致生物多样性急剧下降。
    科学家发现，森林面积减少使得当地降雨量显著降低，进一步加剧了干旱问题。
    干旱又导致更多树木死亡，形成恶性循环。
    """
    
    print("测试 2: 环境新闻")
    test_extract_causality(news2)
```

## JavaScript/TypeScript 测试脚本

```typescript
interface NewsExtractionRequest {
  news_text: string
}

interface AnalysisResult {
  nodes: Array<{
    id: string
    label: string
    type: string
    description?: string
    confidence?: number
  }>
  edges: Array<{
    source: string
    target: string
    label?: string
    description?: string
    strength?: number
  }>
  explanation: string
}

async function extractCausality(newsText: string): Promise<AnalysisResult> {
  const response = await fetch('http://localhost:8000/api/v1/extract-causality', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ news_text: newsText }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(`API Error: ${error.detail}`)
  }

  return await response.json()
}

// 使用示例
const newsText = `
由于全球供应链中断和能源价格飙升，多国央行被迫提高利率以遏制通货膨胀。
高利率导致企业融资成本上升，许多中小企业面临资金链断裂的风险。
`

extractCausality(newsText)
  .then(result => {
    console.log('分析结果:', result)
    console.log(`发现 ${result.nodes.length} 个节点`)
    console.log(`发现 ${result.edges.length} 条因果关系`)
  })
  .catch(error => {
    console.error('提取失败:', error)
  })
```

## 注意事项

1. **API Key 配置**: 确保 `.env` 文件中配置了有效的 `OPENAI_API_KEY`
2. **模型选择**: 默认使用 `gpt-4o`，可在 `.env` 中修改 `OPENAI_MODEL`
3. **超时处理**: 大模型调用可能需要 10-30 秒，前端需要设置合理的超时时间
4. **错误重试**: 建议实现重试机制，处理偶发的 API 失败
5. **成本控制**: 每次调用会消耗 token，建议添加请求频率限制








