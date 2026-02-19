# 标的逆向推演与实时分析 API 文档

## 📋 概述

`/api/v1/research-target` 接口实现了一个完整的三步走 Pipeline，用于分析金融/商业标的的最新动态和因果影响。

## 🔄 Pipeline 流程

```
用户输入标的
    ↓
【步骤 1】逆向因子提取与关键词生成
    - LLM 分析标的
    - 提取核心影响因子
    - 生成 3-5 个精准搜索词
    ↓
【步骤 2】并发联网搜索
    - Promise.all 并发执行搜索
    - 支持 Tavily/Serper/DuckDuckGo
    - 合并搜索结果为上下文
    ↓
【步骤 3】综合分析与因果图生成
    - 结合标的 + 实时上下文
    - LLM 生成因果关系图谱
    - 输出标准 AnalysisResult 格式
    ↓
返回完整分析结果
```

## 🎯 API 接口

### POST /api/v1/research-target

**请求参数：**
```json
{
  "target": "中证1000指数"
}
```

**响应格式：**
```json
{
  "nodes": [
    {
      "id": "n1",
      "label": "节点标签",
      "type": "cause|effect|intermediate",
      "description": "详细描述",
      "confidence": 0.9
    }
  ],
  "edges": [
    {
      "source": "n1",
      "target": "n2",
      "label": "因果关系",
      "description": "传导机制",
      "strength": 0.85
    }
  ],
  "explanation": "整体分析说明",
  "metadata": {
    "target": "中证1000指数",
    "factors": ["因子1", "因子2", "因子3"],
    "search_queries": ["查询1", "查询2", "查询3"],
    "context_length": 5000,
    "total_time": 15.5
  }
}
```

## 📝 测试用例

### 测试 1: 股票指数分析

**请求：**
```bash
curl -X POST http://localhost:8000/api/v1/research-target \
  -H "Content-Type: application/json" \
  -d '{
    "target": "中证1000指数"
  }'
```

**预期流程：**
```
[步骤 1] 开始逆向因子提取: 中证1000指数
  - 提取因子: 5 个
    1. 中小盘企业盈利能力
    2. 流动性环境
    3. 风险偏好
    4. 政策支持力度
    5. 市场风格轮动
  - 生成查询: 5 个
    1. 中证1000指数 最新走势
    2. 中小盘股票 政策利好
    3. A股市场 风格切换
    4. 流动性 货币政策
    5. 中证1000 成分股 业绩

[步骤 2] 开始并发搜索
  - 并发执行 5 个搜索查询
  - 获取上下文: 8500 字符

[步骤 3] 开始综合分析与因果图生成
  - 生成节点: 8 个
  - 生成边: 12 条

Pipeline 完成，总耗时: 18.5秒
```

### 测试 2: 加密货币分析

**请求：**
```bash
curl -X POST http://localhost:8000/api/v1/research-target \
  -H "Content-Type: application/json" \
  -d '{
    "target": "比特币"
  }'
```

### 测试 3: 大宗商品分析

**请求：**
```bash
curl -X POST http://localhost:8000/api/v1/research-target \
  -H "Content-Type: application/json" \
  -d '{
    "target": "黄金期货"
  }'
```

### 测试 4: 个股分析

**请求：**
```bash
curl -X POST http://localhost:8000/api/v1/research-target \
  -H "Content-Type: application/json" \
  -d '{
    "target": "特斯拉股票"
  }'
```

## 🔧 环境配置

### 必需配置

在 `backend/.env` 中配置：

```env
# OpenAI API（必需）
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat

# 搜索引擎 API（至少配置一个）
# 选项 1: Tavily (推荐)
TAVILY_API_KEY=your_tavily_key

# 选项 2: Serper.dev
SERPER_API_KEY=your_serper_key

# 选项 3: DuckDuckGo (免费，但需要安装库)
# pip install duckduckgo-search

# 默认搜索引擎
SEARCH_ENGINE=tavily  # tavily, serper, duckduckgo
```

### 搜索引擎选择

#### 1. Tavily (推荐)
- **优点**: 专为 AI 优化，结果质量高
- **价格**: 免费额度 1000 次/月
- **注册**: https://tavily.com/

#### 2. Serper.dev
- **优点**: 基于 Google，结果准确
- **价格**: 免费额度 2500 次
- **注册**: https://serper.dev/

#### 3. DuckDuckGo
- **优点**: 完全免费，无需 API Key
- **缺点**: 需要安装额外库
- **安装**: `pip install duckduckgo-search`

## 📦 依赖安装

```bash
# 基础依赖
pip install aiohttp

# 如果使用 DuckDuckGo
pip install duckduckgo-search
```

更新 `requirements.txt`:
```txt
aiohttp==3.9.1
duckduckgo-search==4.1.0  # 可选
```

## 🐍 Python 测试脚本

```python
import requests
import json

API_URL = "http://localhost:8000/api/v1/research-target"

def test_research_target(target: str):
    """测试标的研究 API"""
    
    print(f"\n{'='*80}")
    print(f"测试标的: {target}")
    print(f"{'='*80}\n")
    
    response = requests.post(
        API_URL,
        json={"target": target},
        headers={"Content-Type": "application/json"},
        timeout=60  # 设置较长的超时时间
    )
    
    print(f"Status Code: {response.status_code}\n")
    
    if response.status_code == 200:
        result = response.json()
        
        # 打印元数据
        metadata = result.get("metadata", {})
        print(f"标的: {metadata.get('target')}")
        print(f"总耗时: {metadata.get('total_time', 0):.2f}秒")
        print(f"\n核心因子:")
        for i, factor in enumerate(metadata.get('factors', []), 1):
            print(f"  {i}. {factor}")
        
        print(f"\n搜索查询:")
        for i, query in enumerate(metadata.get('search_queries', []), 1):
            print(f"  {i}. {query}")
        
        print(f"\n因果图:")
        print(f"  - 节点数: {len(result.get('nodes', []))}")
        print(f"  - 边数: {len(result.get('edges', []))}")
        
        print(f"\n分析说明:")
        print(f"  {result.get('explanation', '')[:200]}...")
        
    else:
        print(f"错误: {response.json()}")
    
    print(f"\n{'='*80}\n")

# 测试用例
if __name__ == "__main__":
    # 测试 1: 股票指数
    test_research_target("中证1000指数")
    
    # 测试 2: 加密货币
    test_research_target("比特币")
    
    # 测试 3: 个股
    test_research_target("特斯拉股票")
    
    # 测试 4: 大宗商品
    test_research_target("黄金期货")
```

## 💻 TypeScript 前端调用

```typescript
interface TargetResearchRequest {
  target: string
}

interface TargetResearchResult {
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
  metadata: {
    target: string
    factors: string[]
    search_queries: string[]
    context_length: number
    total_time: number
  }
}

async function researchTarget(target: string): Promise<TargetResearchResult> {
  const response = await fetch('/api/v1/research-target', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ target }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(`研究失败: ${error.detail}`)
  }

  return await response.json()
}

// 使用示例
async function analyzeTarget() {
  try {
    console.log('开始分析...')
    
    const result = await researchTarget('中证1000指数')
    
    console.log('分析完成！')
    console.log(`核心因子: ${result.metadata.factors.join(', ')}`)
    console.log(`发现 ${result.nodes.length} 个节点`)
    console.log(`发现 ${result.edges.length} 条因果关系`)
    console.log(`总耗时: ${result.metadata.total_time.toFixed(2)}秒`)
    
    // 可视化因果图
    renderCausalGraph(result.nodes, result.edges)
    
  } catch (error) {
    console.error('分析失败:', error)
  }
}
```

## ⚡ 性能优化

### 并发搜索优化
```python
# 在 search_service.py 中
# 使用 asyncio.gather 实现真正的并发
tasks = [self.search_single(query) for query in queries]
results = await asyncio.gather(*tasks, return_exceptions=True)
```

### 超时控制
- 步骤 1: LLM 调用，通常 3-8 秒
- 步骤 2: 并发搜索，通常 5-15 秒
- 步骤 3: LLM 分析，通常 5-10 秒
- **总计**: 15-35 秒

### 缓存策略（可选）
```python
# 可以添加 Redis 缓存搜索结果
# 相同查询在短时间内直接返回缓存
```

## 🔍 调试技巧

### 查看详细日志
每个步骤都会在控制台打印详细信息：
```
[步骤 1] 开始逆向因子提取: 中证1000指数
[步骤 1] 完成，耗时: 3.5秒
  - 提取因子: 5 个
  - 生成查询: 5 个

[步骤 2] 开始并发搜索
开始并发搜索，共 5 个查询...
搜索完成，获取到 8500 字符的上下文
[步骤 2] 完成，耗时: 12.3秒

[步骤 3] 开始综合分析与因果图生成
[步骤 3] 完成，耗时: 8.7秒
  - 生成节点: 8 个
  - 生成边: 12 条

Pipeline 完成，总耗时: 24.5秒
```

### 错误处理
```python
# 每个步骤都有独立的 try-catch
# 搜索失败不会中断整个流程
# 会使用空上下文继续分析
```

## 📊 示例输出

### 完整响应示例
```json
{
  "nodes": [
    {
      "id": "n1",
      "label": "货币政策宽松",
      "type": "cause",
      "description": "央行降准降息，市场流动性改善",
      "confidence": 0.9
    },
    {
      "id": "n2",
      "label": "风险偏好提升",
      "type": "intermediate",
      "description": "投资者风险偏好上升，资金流入权益市场",
      "confidence": 0.85
    },
    {
      "id": "n3",
      "label": "中小盘股受益",
      "type": "intermediate",
      "description": "中小盘股票估值修复，成交活跃",
      "confidence": 0.8
    },
    {
      "id": "n4",
      "label": "中证1000上涨",
      "type": "effect",
      "description": "中证1000指数持续上涨",
      "confidence": 0.85
    }
  ],
  "edges": [
    {
      "source": "n1",
      "target": "n2",
      "label": "推动",
      "description": "流动性宽松提升市场风险偏好",
      "strength": 0.9
    },
    {
      "source": "n2",
      "target": "n3",
      "label": "利好",
      "description": "风险偏好提升利好中小盘股",
      "strength": 0.85
    },
    {
      "source": "n3",
      "target": "n4",
      "label": "直接推动",
      "description": "成分股上涨直接推动指数上涨",
      "strength": 0.95
    }
  ],
  "explanation": "当前货币政策转向宽松，央行通过降准降息释放流动性，改善市场资金面。充裕的流动性推动投资者风险偏好提升，资金开始从防御性资产流向权益市场。在风险偏好提升的背景下，中小盘股票作为高弹性品种受益明显，估值修复加速，成交量显著放大。中证1000指数作为中小盘股票的代表性指数，其成分股的普遍上涨直接推动指数走强。",
  "metadata": {
    "target": "中证1000指数",
    "factors": [
      "货币政策",
      "市场流动性",
      "风险偏好",
      "中小盘股估值",
      "市场风格"
    ],
    "search_queries": [
      "中证1000指数 最新走势",
      "央行货币政策 降准降息",
      "中小盘股票 市场表现",
      "A股风格切换 中证1000",
      "流动性宽松 股市影响"
    ],
    "context_length": 8500,
    "total_time": 24.5
  }
}
```

## 🚨 常见问题

### Q1: 搜索 API 配置问题
**A**: 确保至少配置一个搜索引擎的 API Key，推荐使用 Tavily

### Q2: 请求超时
**A**: 整个 Pipeline 可能需要 15-35 秒，前端需要设置足够的超时时间

### Q3: 搜索失败怎么办
**A**: 搜索失败不会中断流程，会使用空上下文继续分析

### Q4: 如何提高分析质量
**A**: 
1. 使用更好的搜索引擎（Tavily > Serper > DuckDuckGo）
2. 增加搜索查询数量
3. 使用更强的 LLM 模型

## 📚 相关文档

- [API 测试文档](./API_TEST.md)
- [摘要生成文档](./SUMMARY_TEST.md)
- [主 README](../README.md)

---

现在你可以开始使用标的研究 API 了！🚀








