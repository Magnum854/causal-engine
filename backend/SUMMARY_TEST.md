# 摘要生成功能测试文档

## 功能概述

动态生成因果关系分析简报，根据图的复杂度智能选择不同的分析策略：
- **简单场景** (edges ≤ 2): 生成一句话核心总结
- **复杂场景** (edges > 2): 生成结构化分析报告

## API 接口

### POST /api/v1/extract-causality

**请求参数：**
```json
{
  "news_text": "新闻文本内容",
  "generate_summary": true  // 可选，默认为 true
}
```

**响应格式：**
```json
{
  "nodes": [...],
  "edges": [...],
  "explanation": "...",
  "summary": {
    "type": "simple" | "complex",
    "complexity": "simple" | "complex",
    "content": "..." | {...}
  }
}
```

## 测试用例

### 测试 1: 简单场景（edges ≤ 2）

**请求：**
```bash
curl -X POST http://localhost:8000/api/v1/extract-causality \
  -H "Content-Type: application/json" \
  -d '{
    "news_text": "美联储宣布加息50个基点，导致美股大幅下跌。",
    "generate_summary": true
  }'
```

**预期响应：**
```json
{
  "nodes": [
    {
      "id": "n1",
      "label": "美联储加息",
      "type": "cause",
      "description": "加息50个基点",
      "confidence": 0.95
    },
    {
      "id": "n2",
      "label": "美股下跌",
      "type": "effect",
      "description": "股市大幅下跌",
      "confidence": 0.9
    }
  ],
  "edges": [
    {
      "source": "n1",
      "target": "n2",
      "label": "直接导致",
      "strength": 0.9
    }
  ],
  "explanation": "美联储加息直接导致美股下跌",
  "summary": {
    "type": "simple",
    "complexity": "simple",
    "content": "美联储加息50个基点直接打压市场流动性，对美股构成明显利空。"
  }
}
```

### 测试 2: 复杂场景（edges > 2）

**请求：**
```bash
curl -X POST http://localhost:8000/api/v1/extract-causality \
  -H "Content-Type: application/json" \
  -d '{
    "news_text": "俄乌冲突导致国际油价飙升，推高全球通胀预期。为应对通胀，多国央行被迫加息，高利率环境下企业融资成本上升，经济增长放缓。同时，能源价格上涨也直接冲击消费者购买力，零售数据持续疲软。",
    "generate_summary": true
  }'
```

**预期响应：**
```json
{
  "nodes": [
    {
      "id": "n1",
      "label": "俄乌冲突",
      "type": "cause",
      "description": "地缘政治冲突",
      "confidence": 0.95
    },
    {
      "id": "n2",
      "label": "油价飙升",
      "type": "intermediate",
      "description": "国际原油价格大幅上涨",
      "confidence": 0.9
    },
    {
      "id": "n3",
      "label": "通胀预期上升",
      "type": "intermediate",
      "description": "全球通胀压力加大",
      "confidence": 0.85
    },
    {
      "id": "n4",
      "label": "央行加息",
      "type": "intermediate",
      "description": "多国央行收紧货币政策",
      "confidence": 0.9
    },
    {
      "id": "n5",
      "label": "经济增长放缓",
      "type": "effect",
      "description": "经济活动减弱",
      "confidence": 0.8
    }
  ],
  "edges": [
    {
      "source": "n1",
      "target": "n2",
      "label": "直接导致",
      "strength": 0.95
    },
    {
      "source": "n2",
      "target": "n3",
      "label": "推高",
      "strength": 0.9
    },
    {
      "source": "n3",
      "target": "n4",
      "label": "迫使",
      "strength": 0.85
    },
    {
      "source": "n4",
      "target": "n5",
      "label": "导致",
      "strength": 0.8
    }
  ],
  "explanation": "俄乌冲突通过油价上涨推高通胀，迫使央行加息，最终导致经济放缓",
  "summary": {
    "type": "complex",
    "complexity": "complex",
    "content": {
      "type": "structured_analysis",
      "sections": [
        {
          "title": "核心传导路径",
          "body": "俄乌冲突作为地缘政治风险源头，直接冲击国际能源市场，导致油价飙升（强度0.95）。能源价格上涨迅速传导至整体物价水平，推高全球通胀预期（强度0.9）。面对通胀压力，各国央行被迫采取紧缩性货币政策，通过加息来抑制需求（强度0.85）。高利率环境增加企业融资成本，抑制投资和消费，最终导致经济增长放缓（强度0.8）。这条传导链条展示了从地缘冲突到宏观经济衰退的完整路径。"
        },
        {
          "title": "资产映射与策略",
          "body": "【大宗商品】能源和贵金属受益于地缘风险溢价，建议配置原油、黄金等避险资产。【股票市场】高利率和经济放缓对股市构成双重利空，建议降低权益仓位，关注防御性板块如公用事业、必需消费品。【债券市场】加息周期对债券价格不利，但经济衰退预期可能带来长期利率下行，建议采取哑铃型策略。【外汇市场】美元作为避险货币可能走强，新兴市场货币面临贬值压力。整体策略：降低风险敞口，增加现金和避险资产配置，等待市场企稳信号。"
        }
      ]
    }
  }
}
```

### 测试 3: 不生成摘要

**请求：**
```bash
curl -X POST http://localhost:8000/api/v1/extract-causality \
  -H "Content-Type: application/json" \
  -d '{
    "news_text": "美联储宣布加息50个基点，导致美股大幅下跌。",
    "generate_summary": false
  }'
```

**预期响应：**
```json
{
  "nodes": [...],
  "edges": [...],
  "explanation": "...",
  // 注意：没有 summary 字段
}
```

### 测试 4: 摘要生成失败（容错测试）

即使摘要生成失败，主体数据仍然正常返回：

**响应：**
```json
{
  "nodes": [...],
  "edges": [...],
  "explanation": "...",
  "summary": null  // 摘要生成失败时为 null
}
```

## Python 测试脚本

```python
import requests
import json

API_URL = "http://localhost:8000/api/v1/extract-causality"

def test_summary_generation(news_text: str, generate_summary: bool = True):
    """测试摘要生成功能"""
    
    response = requests.post(
        API_URL,
        json={
            "news_text": news_text,
            "generate_summary": generate_summary
        },
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    result = response.json()
    
    print(f"\n节点数: {len(result['nodes'])}")
    print(f"边数: {len(result['edges'])}")
    
    if "summary" in result and result["summary"]:
        summary = result["summary"]
        print(f"\n摘要类型: {summary['type']}")
        print(f"复杂度: {summary['complexity']}")
        print(f"\n摘要内容:")
        if summary['type'] == 'simple':
            print(summary['content'])
        else:
            print(json.dumps(summary['content'], indent=2, ensure_ascii=False))
    else:
        print("\n未生成摘要")
    
    print("-" * 80)
    return result

# 测试用例
if __name__ == "__main__":
    # 测试 1: 简单场景
    print("=" * 80)
    print("测试 1: 简单场景（edges ≤ 2）")
    print("=" * 80)
    simple_news = "美联储宣布加息50个基点，导致美股大幅下跌。"
    test_summary_generation(simple_news)
    
    # 测试 2: 复杂场景
    print("\n" + "=" * 80)
    print("测试 2: 复杂场景（edges > 2）")
    print("=" * 80)
    complex_news = """
    俄乌冲突导致国际油价飙升，推高全球通胀预期。
    为应对通胀，多国央行被迫加息，高利率环境下企业融资成本上升，经济增长放缓。
    同时，能源价格上涨也直接冲击消费者购买力，零售数据持续疲软。
    """
    test_summary_generation(complex_news)
    
    # 测试 3: 不生成摘要
    print("\n" + "=" * 80)
    print("测试 3: 不生成摘要")
    print("=" * 80)
    test_summary_generation(simple_news, generate_summary=False)
```

## TypeScript 前端调用示例

```typescript
interface SummaryContent {
  type: 'simple' | 'complex'
  complexity: 'simple' | 'complex'
  content: string | {
    type: 'structured_analysis'
    sections: Array<{
      title: string
      body: string
    }>
  }
}

interface AnalysisResultWithSummary extends AnalysisResult {
  summary?: SummaryContent | null
}

async function extractCausalityWithSummary(
  newsText: string,
  generateSummary: boolean = true
): Promise<AnalysisResultWithSummary> {
  const response = await fetch('/api/v1/extract-causality', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      news_text: newsText,
      generate_summary: generateSummary,
    }),
  })

  if (!response.ok) {
    throw new Error('提取失败')
  }

  return await response.json()
}

// 使用示例
const result = await extractCausalityWithSummary(
  '美联储宣布加息50个基点，导致美股大幅下跌。'
)

if (result.summary) {
  if (result.summary.type === 'simple') {
    console.log('一句话总结:', result.summary.content)
  } else {
    const structured = result.summary.content as any
    structured.sections.forEach(section => {
      console.log(`\n${section.title}:`)
      console.log(section.body)
    })
  }
}
```

## 环境变量配置

在 `backend/.env` 中可配置摘要生成模型：

```env
# 简单摘要使用的快速模型
OPENAI_SUMMARY_MODEL=gpt-4o-mini

# 复杂摘要使用的主模型
OPENAI_MODEL=gpt-4o

# 或使用 DeepSeek
OPENAI_SUMMARY_MODEL=deepseek-chat
OPENAI_MODEL=deepseek-chat
```

## 性能说明

- **简单摘要**: 通常 2-5 秒完成
- **复杂摘要**: 通常 5-15 秒完成
- **超时设置**: 默认 30 秒
- **容错机制**: 摘要失败不影响主体数据返回

## 注意事项

1. ✅ 摘要生成是可选的，通过 `generate_summary` 参数控制
2. ✅ 复杂度判断基于边的数量（edges.length）
3. ✅ 简单场景使用更快的模型以提高响应速度
4. ✅ 完全容错，摘要失败时返回 `summary: null`
5. ✅ 支持结构化和非结构化两种摘要格式








