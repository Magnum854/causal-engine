# 多路由工具调用架构 (Multi-Tool Router Architecture)

## 📋 概述

CausalFlow 因果引擎已从"单一搜索引擎"升级为"多路由工具调用"架构，支持：
- **结构化 API 数据**（精确数值）
- **非结构化新闻数据**（情绪/事件）
- **瀑布流降级搜索**（解决付费墙和数据稀缺问题）

---

## 🏗️ 架构组件

### 1. 配置文件 (`config/financial_sources.json`)

#### 1.1 搜索域名白名单（分层）

```json
{
  "tier_1_premium_news": {
    "description": "顶级付费墙媒体（高权威但可能数据稀缺）",
    "domains": ["bloomberg.com", "reuters.com", "ft.com", "wsj.com", "nikkei.com"]
  },
  "tier_2_aggregators": {
    "description": "财经聚合器（易抓取结构化数值，无付费墙）",
    "domains": ["tradingeconomics.com", "investing.com", "finance.yahoo.com", "cnbc.com", "marketwatch.com"]
  }
}
```

#### 1.2 结构化 API 配置

支持的 API（当前为 Mock 实现）：
- **FRED**: 美国宏观经济数据（美联储利率、CPI、失业率等）
- **Tushare**: 中国股票和宏观数据
- **SEC EDGAR**: 美股公司财报
- **CCXT**: 加密货币行情
- **Polygon.io**: 美股实时行情

#### 1.3 路由规则

根据节点类型自动选择数据源策略：

```json
{
  "macro_indicator": {
    "primary_strategy": "structured_api",
    "fallback_strategy": "news_search",
    "preferred_apis": ["fred", "tushare"],
    "tier_1_domains": ["imf.org", "bis.org", "federalreserve.gov"],
    "tier_2_domains": ["tradingeconomics.com", "investing.com"]
  }
}
```

---

## 🔄 核心流程

### Pass 1: 生成因果图谱拓扑

**优化点：极简 SEO 关键词生成**

```python
# ✅ 正确示例
search_query: "US Dollar Index DXY current value 2026"
search_query: "Federal Reserve interest rate current 2026"
search_query: "gold price per ounce current 2026"

# ❌ 错误示例
search_query: "请帮我查询美元指数的最新走势和分析报告"  # 太冗长
search_query: "美元指数"  # 缺少时效性
```

### Pass 2: 动态富化节点（多路由 + 瀑布流）

#### 路由决策树

```
节点类型判断
    ├─ macro_indicator / monetary_policy
    │   ├─ 尝试结构化 API (FRED, Tushare)
    │   │   ├─ 成功 → 返回精确数值
    │   │   └─ 失败 → 降级到新闻搜索
    │   └─ 新闻搜索（瀑布流）
    │       ├─ Attempt 1: Tier 1 + Tier 2 白名单（7天窗口）
    │       │   ├─ 有结果 + LLM 提取成功 → 返回
    │       │   └─ 无结果 / 提取失败 → Attempt 2
    │       └─ Attempt 2: 全网搜索（30天窗口 + 权威性判断）
    │           ├─ LLM 判断来源权威性
    │           └─ 返回结果（可能为 unknown）
    │
    └─ geopolitical_risk / market_sentiment
        └─ 直接新闻搜索（瀑布流）
```

---

## 🌊 瀑布流搜索详解

### Attempt 1: 白名单搜索

**配置**
```json
{
  "time_window": "7 days",
  "use_domain_filter": true,
  "domains": ["tier_1_premium_news", "tier_2_aggregators"]
}
```

**流程**
1. 使用 `search_query` 调用搜索引擎
2. 过滤结果：只保留白名单域名
3. LLM 提取数值（无权威性判断）
4. 如果提取到非 `unknown` 值 → 成功返回
5. 否则 → 进入 Attempt 2

### Attempt 2: 全网搜索 + 权威性判断

**配置**
```json
{
  "time_window": "30 days",
  "use_domain_filter": false,
  "llm_authority_check": true
}
```

**流程**
1. 重新搜索（无域名限制）
2. LLM 提取数值 + **权威性判断**
3. LLM Prompt 额外护栏：
   ```
   ⚠️ 这批数据来自无限制全网搜索，请严格判断来源权威性：
   - 如果来源是博客、内容农场、自媒体、论坛帖子，必须返回 "unknown"
   - 只接受：主流财经媒体、官方机构、知名金融网站
   ```

---

## 📊 数据流示例

### 示例 1: 宏观指标节点（美联储利率）

```
节点: "美联储利率"
类型: macro_indicator
search_query: "Federal Reserve interest rate current 2026"

路由决策:
  ├─ 尝试 FRED API
  │   └─ Mock 返回: "5.25%-5.50%"
  └─ 成功！无需搜索

最终结果:
{
  "latest_value": "5.25%-5.50%",
  "sources": [{
    "title": "FRED (Mock) - 美联储利率",
    "url": "https://api.stlouisfed.org/fred",
    "domain": "stlouisfed.org",
    "type": "structured_api"
  }],
  "strategy_used": "structured_api"
}
```

### 示例 2: 地缘政治风险节点（瀑布流）

```
节点: "地缘政治风险"
类型: geopolitical_risk
search_query: "geopolitical risk latest news 2026"

路由决策:
  └─ 新闻搜索（瀑布流）
      ├─ Attempt 1: 白名单搜索
      │   ├─ 搜索结果: 15 条
      │   ├─ 白名单过滤: 3 条（reuters.com, ft.com, bloomberg.com）
      │   ├─ LLM 提取: "中东局势紧张"
      │   └─ 成功！
      └─ 无需 Attempt 2

最终结果:
{
  "latest_value": "中东局势紧张",
  "sources": [
    {"domain": "reuters.com", "title": "..."},
    {"domain": "ft.com", "title": "..."}
  ],
  "strategy_used": "news_search",
  "attempt_number": 1
}
```

### 示例 3: 付费墙导致的降级（瀑布流完整流程）

```
节点: "美元指数"
类型: macro_indicator
search_query: "US Dollar Index DXY current value 2026"

路由决策:
  ├─ 尝试 FRED API
  │   └─ 失败（无对应 series_id）
  └─ 降级到新闻搜索
      ├─ Attempt 1: 白名单搜索
      │   ├─ 搜索结果: 8 条
      │   ├─ 白名单过滤: 0 条（全部付费墙）
      │   └─ 失败！
      └─ Attempt 2: 全网搜索
          ├─ 搜索结果: 50 条
          ├─ LLM 提取 + 权威性判断
          ├─ 识别到 tradingeconomics.com（权威）
          └─ 成功: "103.5"

最终结果:
{
  "latest_value": "103.5",
  "sources": [
    {"domain": "tradingeconomics.com", "title": "..."}
  ],
  "strategy_used": "news_search",
  "attempt_number": 2
}
```

---

## 🔧 关键代码片段

### 瀑布流搜索核心逻辑

```python
async def _try_news_search(self, node_label, search_query, rule):
    # Attempt 1: 白名单搜索
    tier_1_domains = rule.get("tier_1_domains", [])
    tier_2_domains = rule.get("tier_2_domains", [])
    combined_whitelist = tier_1_domains + tier_2_domains
    
    search_results_attempt1 = await self.search_service.search(search_query)
    filtered_results_attempt1 = self._filter_by_whitelist(
        search_results_attempt1, 
        combined_whitelist
    )
    
    if filtered_results_attempt1:
        result = await self._build_search_result(
            node_label, filtered_results_attempt1, 
            attempt_number=1, authority_check=False
        )
        if result.get("latest_value") != "unknown":
            return result  # 成功！
    
    # Attempt 2: 全网搜索 + 权威性判断
    search_results_attempt2 = await self.search_service.search(search_query)
    result = await self._build_search_result(
        node_label, search_results_attempt2[:10],
        attempt_number=2, authority_check=True
    )
    return result
```

### LLM 权威性判断 Prompt

```python
if authority_check:
    authority_guard = """
【重要：权威性判断】
⚠️ 这批数据来自无限制全网搜索，请严格判断来源权威性：
- 如果来源是博客、内容农场、自媒体、论坛帖子，必须返回 "unknown"
- 只接受：主流财经媒体、官方机构、知名金融网站
- 判断标准：域名是否为知名机构（如 .gov, .org, 主流媒体）
"""
```

---

## 📈 性能优化

### 并发处理
- Pass 2 使用 `asyncio.gather` 并发富化所有节点
- 单节点富化时间：1-3秒（取决于搜索 API 响应）

### 缓存策略（未来）
- 结构化 API 数据缓存（TTL: 1小时）
- 新闻搜索结果缓存（TTL: 15分钟）

---

## 🚀 未来扩展

### 1. 接入真实 API
- [ ] FRED API（需申请 API Key）
- [ ] Tushare Pro（需注册 Token）
- [ ] Tavily/Serper 搜索引擎（需付费）

### 2. 智能缓存
- [ ] Redis 缓存层
- [ ] 基于节点类型的差异化 TTL

### 3. 数据质量评分
- [ ] 来源权威性评分（0-100）
- [ ] 数据新鲜度评分
- [ ] 置信度加权

---

## 📝 配置文件位置

```
backend/
├── config/
│   └── financial_sources.json  # 核心配置
├── app/
│   └── services/
│       ├── multi_tool_router_service.py      # 多路由服务
│       ├── structured_api_service.py         # 结构化 API
│       └── two_pass_causal_service.py        # 双阶段分析
```

---

## 🎯 总结

通过引入**多路由工具调用**和**瀑布流降级搜索**，CausalFlow 成功解决了：
1. ✅ 付费墙导致的数据稀缺问题
2. ✅ 结构化数据与非结构化数据的统一处理
3. ✅ 数据来源的权威性保障
4. ✅ 高频 `unknown` 问题的显著改善

系统现在能够智能选择最优数据源，并在遇到障碍时自动降级，确保数据获取的鲁棒性。



















