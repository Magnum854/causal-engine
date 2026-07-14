# 双阶段架构 + 数据溯源系统 - 完整指南

## 架构概述

### 核心问题
传统因果引擎只能生成静态拓扑图，无法获取节点的实时状态，也无法追溯数据来源。

### 解决方案：Two-Pass Pipeline with Data Provenance

```
Pass 1: 拓扑生成
  输入: "黄金价格的影响因素"
  LLM 分析 → 生成因果图谱
  每个节点包含 search_query 字段
  ↓
  输出: {
    nodes: [
      {id: "n1", label: "美元指数", search_query: "美元指数最新走势"},
      {id: "n2", label: "美联储利率", search_query: "美联储利率决议"}
    ],
    edges: [...]
  }

Pass 2: 动态富化 + 数据溯源
  提取所有 search_query
  并发调用搜索引擎（真实 API 或 Mock）
  LLM 解析搜索结果
  ↓
  输出: {
    nodes: [
      {
        id: "n1",
        label: "美元指数",
        realtime_state: {
          latest_value: "103.5",
          sources: [
            {
              title: "美元指数升至103.5",
              url: "https://www.reuters.com/...",
              domain: "reuters.com"
            }
          ],
          updated_at: "2024-02-19T10:30:00Z"
        }
      }
    ]
  }
```

---

## API 使用

### POST `/api/v1/analyze-v2`

**请求：**

```json
{
  "query": "黄金价格的影响因素",
  "context": "分析当前市场环境",
  "max_depth": 3
}
```

**响应：**

```json
{
  "nodes": [
    {
      "id": "n1",
      "label": "美元指数",
      "type": "cause",
      "description": "美元相对其他主要货币的强弱指标",
      "search_query": "美元指数最新走势 US Dollar Index DXY latest",
      "realtime_state": {
        "latest_value": "103.5",
        "sources": [
          {
            "title": "美元指数升至103.5，创两个月新高",
            "url": "https://www.reuters.com/markets/currencies/dollar-index-2024",
            "domain": "reuters.com"
          },
          {
            "title": "US Dollar Index Rises on Fed Hawkish Stance",
            "url": "https://www.bloomberg.com/news/dollar-strength-2024",
            "domain": "bloomberg.com"
          }
        ],
        "updated_at": "2024-02-19T10:30:00Z"
      }
    }
  ],
  "edges": [...],
  "explanation": "..."
}
```

---

## 前端 UI 特性

### 1. 节点卡片增强

**实时状态栏（底部）：**
- 显示 `latest_value`（如 "103.5"）
- 显示更新时间

**数据源角标（右上角）：**
- 显示 🔗 图标 + 域名（如 "reuters.com"）
- Hover 显示完整标题
- 如果有多个来源，显示 "+N 个其他来源"

### 2. 全局数据源面板（底部）

**功能：**
- 自动提取所有节点的数据源并去重
- 列表展示：[节点名称] - [新闻标题] - [可点击链接]
- 点击展开/收起
- 最大高度 264px，超出滚动

**示例：**

```
📚 分析引用的数据源
共 5 条来源 · 点击展开/收起

1. 来自节点: 美元指数
   美元指数升至103.5，创两个月新高
   reuters.com 查看原文 ↗

2. 来自节点: 美联储利率
   美联储维持利率在5.25%-5.50%不变
   federalreserve.gov 查看原文 ↗
```

---

## Mock 模式

### 为什么需要 Mock？

在开发/测试环境中，可能没有配置真实的搜索引擎 API。Mock 模式允许你：
- 无需 API 密钥即可测试完整流程
- 模拟真实的网络延迟（500ms-1500ms）
- 返回符合真实场景的模拟数据

### Mock 数据示例

**查询：** "美元指数最新走势"

**Mock 返回：**
```json
[
  {
    "title": "美元指数升至103.5，创两个月新高",
    "url": "https://www.reuters.com/markets/currencies/dollar-index-2024",
    "snippet": "美元指数周三升至103.5，受美联储鹰派立场支撑..."
  },
  {
    "title": "US Dollar Index Rises on Fed Hawkish Stance",
    "url": "https://www.bloomberg.com/news/dollar-strength-2024",
    "snippet": "The US Dollar Index (DXY) climbed to 103.5..."
  }
]
```

### 启用 Mock 模式

**自动启用：** 如果 `.env` 中未配置 `TAVILY_API_KEY` 和 `SERPER_API_KEY`，系统自动使用 Mock 模式。

**日志提示：**
```
[搜索引擎] 未配置真实 API，将使用 Mock 模式
[Mock Search] 模拟搜索: 美元指数最新走势
[Mock Search] 返回 2 条模拟结果
```

---

## 数据流转详解

### Pass 1: 拓扑生成

**LLM Prompt 关键要求：**
```
每个节点必须包含 search_query 字段
search_query 应该是精准的搜索关键词
对于数值型节点，search_query 应包含"最新"、"latest"等时效词
```

**验证逻辑：**
```python
for node in result["nodes"]:
    if "search_query" not in node:
        logger.warning(f"节点 {node.get('id')} 缺少 search_query，自动生成")
        node["search_query"] = f"{node.get('label', '')} latest news"
```

### Pass 2: 动态富化

**并发处理：**
```python
enriched_nodes = await asyncio.gather(
    *[self._enrich_single_node(node) for node in nodes],
    return_exceptions=True
)
```

**搜索引擎调用：**
```python
if self.use_mock:
    return await self._mock_search_api(query)
elif self.tavily_api_key:
    return await self._search_tavily(query)
elif self.serper_api_key:
    return await self._search_serper(query)
```

**LLM 解析：**
```python
system_prompt = """
提取规则：
1. 如果有明确数值，提取数值
2. 如果没有明确数值，用简短描述
3. 如果完全无法确定，设为 "unknown"
4. 不要编造数据，严格基于搜索结果
"""
```

**数据溯源：**
```python
sources = []
for r in search_results[:3]:
    url = r.get("url", "")
    domain = urlparse(url).netloc
    
    sources.append({
        "title": r.get("title", ""),
        "url": url,
        "domain": domain
    })
```

---

## 环境配置

### 开发环境（Mock 模式）

```bash
# backend/.env
OPENAI_API_KEY=your-deepseek-api-key
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-reasoner

# 不配置搜索引擎 API，自动使用 Mock
```

### 生产环境（真实 API）

```bash
# backend/.env
OPENAI_API_KEY=your-deepseek-api-key
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-reasoner

# 配置至少一个搜索引擎 API
TAVILY_API_KEY=your-tavily-api-key
SERPER_API_KEY=your-serper-api-key
```

---

## 测试流程

### 1. 启动后端

```bash
cd backend
python main.py
```

### 2. 启动前端

```bash
cd frontend
npm run dev
```

### 3. 测试分析

**输入：** "黄金价格的影响因素"

**预期结果：**
- Pass 1: 生成 3-5 个节点（美元指数、美联储利率、地缘政治等）
- Pass 2: 每个节点显示实时状态（如 "103.5"）
- 节点右上角显示数据源角标（如 "reuters.com"）
- 底部面板显示所有引用来源

### 4. 验证数据溯源

**检查节点卡片：**
- Hover 右上角 🔗 图标
- 应显示完整新闻标题

**检查底部面板：**
- 点击展开
- 应显示所有节点的数据源
- 点击链接应跳转到原文

---

## 性能指标

### Pass 1: 拓扑生成
- **耗时**: 5-8 秒
- **LLM 调用**: 1 次

### Pass 2: 动态富化
- **耗时**: 10-15 秒（并发）
- **搜索引擎调用**: N 次（N = 节点数）
- **LLM 调用**: N 次（解析搜索结果）

### 总耗时
- **开发环境（Mock）**: 15-20 秒
- **生产环境（真实 API）**: 20-30 秒

---

## 故障排查

### 问题 1: 节点没有显示实时状态

**原因：**
- Pass 1 生成的节点缺少 `search_query`
- Pass 2 搜索失败

**解决：**
- 检查日志：`[Pass 1]` 和 `[Pass 2]`
- 确认节点包含 `search_query` 字段
- 检查搜索引擎 API 配置

### 问题 2: 数据源面板为空

**原因：**
- 节点的 `realtime_state.sources` 为空
- 搜索结果未返回 `url` 字段

**解决：**
- 检查 Mock 数据是否包含 `url`
- 检查真实 API 返回格式

### 问题 3: Mock 模式不工作

**原因：**
- 配置了搜索引擎 API，但 API 无效

**解决：**
- 删除 `.env` 中的 `TAVILY_API_KEY` 和 `SERPER_API_KEY`
- 重启后端

---

## 扩展方向

### 1. 时间序列追踪
- 记录节点状态的历史变化
- 显示趋势图表

### 2. 多语言支持
- 自动检测查询语言
- 生成对应语言的 `search_query`

### 3. 自定义数据源
- 允许用户指定搜索引擎
- 支持企业内部数据源

### 4. 实时推送
- WebSocket 连接
- 节点状态变化时自动更新

---

## 技术亮点

✅ **模块解耦** - Pass 1 和 Pass 2 完全独立  
✅ **并发处理** - 使用 `asyncio.gather` 提升性能  
✅ **降级策略** - Mock 模式确保开发体验  
✅ **数据溯源** - 每个数据点都可追溯到原始来源  
✅ **反幻觉机制** - 无数据时返回 "unknown"，不捏造  
✅ **用户体验** - 节点卡片 + 全局面板双重展示  

---

## 总结

双阶段架构 + 数据溯源系统实现了：

1. **实时联网感知** - 节点自动获取最新状态
2. **严格数据溯源** - 每个数据点都有来源
3. **完整可追溯性** - 用户可点击查看原文
4. **开发友好** - Mock 模式无需真实 API
5. **生产就绪** - 支持真实搜索引擎 API

这是因果引擎从"静态拓扑图"到"动态智能系统"的关键升级！



















