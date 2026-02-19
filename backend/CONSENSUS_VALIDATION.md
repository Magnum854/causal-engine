# 机构级数据防伪与共识验证机制 (Consensus Validation)

## 概述

本文档详细说明因果引擎感知层的**两阶段共识验证机制**，用于消除虚假信息、过时数据和营销内容，确保节点状态数据的真实性和可靠性。

---

## 架构设计

### 核心理念

**问题**：全网搜索结果包含大量噪音
- ❌ 虚假信息（假新闻、营销软文）
- ❌ 过时数据（历史数据被误认为最新）
- ❌ 单一来源（无法验证真实性）

**解决方案**：两阶段瀑布流 + 三方交叉验证
- ✅ Stage 1: 白名单优先（信任权威来源）
- ✅ Stage 2: 全网兜底 + 三方交叉验证（严格共识机制）

---

## Stage 1: 白名单优先搜索 (Whitelist Pass)

### 目标
从权威域名中快速获取可信数据，无需交叉验证。

### 流程

```
用户查询
   ↓
搜索引擎 API (Tavily/Serper)
   ↓
白名单过滤 (27 个权威域名)
   ↓
LLM 直接提取数值
   ↓
成功？
   ├─ YES → 返回数据 (confidence: "whitelist_direct")
   └─ NO  → 进入 Stage 2
```

### 白名单域名（27 个）

#### Tier 1: 顶级付费墙媒体
```
bloomberg.com
reuters.com
ft.com
wsj.com
nikkei.com
```

#### Tier 2: 财经聚合器
```
tradingeconomics.com
investing.com
finance.yahoo.com
cnbc.com
marketwatch.com
```

#### 中国财经媒体
```
caixin.com
yicai.com
21jingji.com
```

#### 官方机构网站
```
imf.org
bis.org
worldbank.org
federalreserve.gov
pbc.gov.cn
stats.gov.cn
sec.gov
sse.com.cn
szse.cn
```

#### 券商门户和财经聚合平台（新增）
```
eastmoney.com
10jqka.com.cn
finance.sina.com.cn
wallstreetcn.com
investing.com
```

### LLM Prompt 设计（Stage 1）

**系统提示词核心**：
```
你正在处理来自【权威白名单域名】的搜索结果。

【关键约束】
1. 这些是权威来源，可以直接采信
2. 如果有明确数值，必须提取
3. 如果无法确定，返回 unknown（不要编造）

【输出格式】
{
    "value": "5.25%",
    "trend": "rising|falling|stable",
    "narrative_context": "一句话背景",
    "confidence": "whitelist_direct",
    "sources": [
        {"title": "...", "url": "...", "domain": "..."}
    ]
}
```

**特点**：
- ✅ 信任白名单，无需交叉验证
- ✅ 温度 0.1（低幻觉）
- ✅ 强制 JSON 输出

---

## Stage 2: 全网兜底与三方交叉验证 (Cross-Validation Pass)

### 目标
当白名单无法提供数据时，从全网搜索中提取数据，但必须通过**三方交叉验证**才能采信。

### 流程

```
Stage 1 失败
   ↓
全网搜索 (Top-10 结果，不限域名)
   ↓
LLM 三方交叉验证
   ↓
检查规则：
   1. 数值在 ≥3 个不同域名中一致？
   2. sources 数组包含 ≥3 个独立域名？
   ↓
通过？
   ├─ YES → 返回数据 (confidence: "cross_validated")
   └─ NO  → 返回 unknown
```

### 三方交叉验证规则（严格执行）

#### 规则 1: 数值一致性
提取的数值必须在**至少 3 个不同域名**的网页中**完全一致**地出现。

**示例**：
```
✓ 正确：
  - bloomberg.com: "美联储利率维持在 5.25%"
  - reuters.com: "Fed rate remains at 5.25%"
  - cnbc.com: "联邦基金利率 5.25%"
  → 3 个不同域名，数值一致 (5.25%)，通过验证

✗ 错误：
  - bloomberg.com: "美联储利率维持在 5.25%"
  - bloomberg.com: "Fed rate 5.25%"（同域名，不计入）
  - reuters.com: "利率可能在 5.0%-5.5% 之间"（不明确，不计入）
  → 只有 1 个域名明确提到 5.25%，不通过验证
```

#### 规则 2: Sources 数组验证
LLM 必须在 `sources` 数组中列出这 3 个支持该数值的独立网页。

**格式要求**：
```json
{
    "sources": [
        {
            "title": "美联储维持利率在 5.25%",
            "url": "https://www.bloomberg.com/news/...",
            "domain": "bloomberg.com"
        },
        {
            "title": "Fed rate remains at 5.25%",
            "url": "https://www.reuters.com/markets/...",
            "domain": "reuters.com"
        },
        {
            "title": "联邦基金利率 5.25%",
            "url": "https://www.cnbc.com/2024/...",
            "domain": "cnbc.com"
        }
    ]
}
```

**验证逻辑**（后端代码）：
```python
# 检查是否有至少 3 个不同域名
unique_domains = set()
for source in state.get("sources", []):
    domain = source.get("domain", "")
    if domain:
        unique_domains.add(domain)

if len(unique_domains) < 3:
    logger.warning(f"三方验证失败: 只有 {len(unique_domains)} 个独立域名")
    return unknown_state
```

#### 规则 3: 强制返回 Unknown
如果满足该数值的独立域名少于 3 个，即使 LLM 看到了数据，也**必须返回 unknown**。

**示例**：
```
场景 1: 只有 2 个域名提到数值
  → 返回 unknown（不满足 ≥3 的要求）

场景 2: 10 个搜索结果都来自同一个域名
  → 返回 unknown（只有 1 个独立域名）

场景 3: 3 个域名提到不同数值
  - domain1.com: "5.25%"
  - domain2.com: "5.5%"
  - domain3.com: "5.0%"
  → 返回 unknown（数值不一致，无法达成共识）
```

---

## LLM Prompt 设计（Stage 2）- 核心难点

### 系统提示词（完整版）

```
你是一个严苛的金融审计员。面对这批全网搜索结果，你必须进行【三方交叉验证 (Cross-Validation)】以消除虚假信息。

【输出格式】
必须严格输出以下 JSON 格式：
{
    "value": "具体数值或状态描述",
    "trend": "rising|falling|stable",
    "narrative_context": "一句话总结当前状态的背景原因",
    "confidence": "cross_validated",
    "sources": [
        {"title": "新闻标题1", "url": "完整URL1", "domain": "域名1"},
        {"title": "新闻标题2", "url": "完整URL2", "domain": "域名2"},
        {"title": "新闻标题3", "url": "完整URL3", "domain": "域名3"}
    ]
}

【三方交叉验证规则（严格执行）】
规则 1：你提取的最新数值，必须在至少 3 个不同域名的网页摘要中完全一致地出现过。
   - 例如：如果你提取 "5.25%"，那么必须有 3 个不同域名的网页都明确提到 "5.25%"
   - 不同域名是指：bloomberg.com、reuters.com、cnbc.com 算 3 个不同域名
   - 同一域名的多个页面只算 1 个域名

规则 2：请在 JSON 输出的 sources 数组中，严格列出这 3 个支持该数值的独立网页。
   - sources 数组必须包含至少 3 条记录
   - 每条记录必须包含 title、url、domain 三个字段
   - 这 3 条记录的 domain 必须完全不同

规则 3：如果满足该数值的独立域名少于 3 个，即使你看到了数据，也必须返回 unknown。
   - 例如：只有 2 个域名提到 "5.25%"，其他域名没有提到或提到不同数值 → 返回 unknown
   - 例如：10 个搜索结果都来自同一个域名 → 返回 unknown

【反幻觉机制】
- 全网搜索结果可能包含虚假信息、过时数据、营销内容
- 只有通过三方交叉验证的数据才能采信
- 如果无法满足三方验证，必须返回：
{
    "value": "unknown",
    "trend": "stable",
    "narrative_context": "无法通过三方交叉验证，数据源不足或存在冲突",
    "confidence": "cross_validated",
    "sources": []
}
```

### 用户提示词

```
【节点名称】
美联储利率

【搜索结果（全网，需要三方交叉验证）】
[结果 1] 域名: bloomberg.com
标题: Fed Holds Rates at 5.25%
摘要: The Federal Reserve maintained its benchmark interest rate at 5.25%...
URL: https://www.bloomberg.com/news/...

[结果 2] 域名: reuters.com
标题: U.S. Fed keeps rates steady at 5.25%
摘要: The U.S. Federal Reserve kept interest rates unchanged at 5.25%...
URL: https://www.reuters.com/markets/...

[结果 3] 域名: cnbc.com
标题: Federal Reserve holds interest rate at 5.25%
摘要: The Federal Reserve decided to hold its key interest rate at 5.25%...
URL: https://www.cnbc.com/2024/...

[结果 4] 域名: randomsite.com
标题: 利率可能上调至 5.5%
摘要: 有分析师预测利率可能上调至 5.5%...
URL: https://randomsite.com/...

请严格执行三方交叉验证规则，提取该节点的实时状态。如果无法满足三方验证，必须返回 unknown。
```

### LLM 预期输出

```json
{
    "value": "5.25%",
    "trend": "stable",
    "narrative_context": "美联储维持基准利率在 5.25%，以应对通胀压力",
    "confidence": "cross_validated",
    "sources": [
        {
            "title": "Fed Holds Rates at 5.25%",
            "url": "https://www.bloomberg.com/news/...",
            "domain": "bloomberg.com"
        },
        {
            "title": "U.S. Fed keeps rates steady at 5.25%",
            "url": "https://www.reuters.com/markets/...",
            "domain": "reuters.com"
        },
        {
            "title": "Federal Reserve holds interest rate at 5.25%",
            "url": "https://www.cnbc.com/2024/...",
            "domain": "cnbc.com"
        }
    ]
}
```

**注意**：
- ✅ 前 3 个结果都提到 5.25%，且来自不同域名 → 通过验证
- ❌ 第 4 个结果提到 5.5%，但只有 1 个域名 → 忽略（冲突数据）

---

## 后端验证逻辑（Python）

### 核心代码片段

```python
async def _extract_state_stage2(
    self, 
    node_label: str, 
    search_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Stage 2: 全网搜索 + 三方交叉验证"""
    
    # 1. 调用 LLM（温度 0.0，最大化确定性）
    response = await self.client.chat.completions.create(
        model=self.model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0,  # 零温度
        response_format={"type": "json_object"}
    )
    
    state = json.loads(response.choices[0].message.content)
    
    # 2. 验证三方交叉验证规则
    if state["value"] != "unknown":
        sources = state.get("sources", [])
        
        # 提取所有独立域名
        unique_domains = set()
        for source in sources:
            domain = source.get("domain", "")
            if domain:
                unique_domains.add(domain)
        
        # 检查是否满足 ≥3 个独立域名
        if len(unique_domains) < 3:
            logger.warning(
                f"三方验证失败: 只有 {len(unique_domains)} 个独立域名，"
                f"不满足 ≥3 的要求，强制返回 unknown"
            )
            return self._create_unknown_state(
                confidence="cross_validated",
                narrative="无法通过三方交叉验证，数据源不足或存在冲突"
            )
    
    return state
```

### 关键点

1. **温度设置**：`temperature=0.0`（零温度，最大化确定性）
2. **强制 JSON**：`response_format={"type": "json_object"}`
3. **后端二次验证**：即使 LLM 返回数据，后端也会检查 `unique_domains` 数量
4. **强制降级**：不满足规则时，强制返回 `unknown`

---

## 数据流示意图

```
┌─────────────────────────────────────────────────────────────┐
│                     用户查询节点                              │
│                  "美联储利率" 的实时状态                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Stage 1: 白名单优先搜索                     │
├─────────────────────────────────────────────────────────────┤
│ 1. 搜索引擎 API (Tavily/Serper)                              │
│ 2. 白名单过滤 (27 个权威域名)                                 │
│ 3. LLM 直接提取 (temperature=0.1)                            │
│ 4. 成功？                                                    │
│    ├─ YES → 返回 (confidence: "whitelist_direct")           │
│    └─ NO  → 进入 Stage 2                                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Stage 2: 全网兜底 + 三方交叉验证                 │
├─────────────────────────────────────────────────────────────┤
│ 1. 全网搜索 (Top-10，不限域名)                               │
│ 2. LLM 三方交叉验证 (temperature=0.0)                        │
│    - 规则 1: 数值在 ≥3 个不同域名中一致                       │
│    - 规则 2: sources 数组包含 ≥3 个独立域名                   │
│    - 规则 3: 不满足则返回 unknown                             │
│ 3. 后端二次验证 (检查 unique_domains 数量)                   │
│ 4. 通过？                                                    │
│    ├─ YES → 返回 (confidence: "cross_validated")            │
│    └─ NO  → 返回 unknown                                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      前端 UI 展示                             │
├─────────────────────────────────────────────────────────────┤
│ • value: "5.25%"                                             │
│ • trend: "stable"                                            │
│ • confidence: "cross_validated" (显示徽章)                   │
│ • sources: [3 个独立来源链接]                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 前端 UI 建议

### Confidence 徽章

```jsx
{node.current_state.confidence === "whitelist_direct" && (
  <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
    ✓ 白名单直接采信
  </span>
)}

{node.current_state.confidence === "cross_validated" && (
  <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
    ✓ 三方交叉验证
  </span>
)}

{node.current_state.value === "unknown" && (
  <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
    ⚠ 数据不足
  </span>
)}
```

### Sources 展示

```jsx
{node.current_state.sources.length > 0 && (
  <div className="mt-2">
    <p className="text-xs text-gray-600 mb-1">
      数据来源 ({node.current_state.sources.length} 个独立域名):
    </p>
    <ul className="space-y-1">
      {node.current_state.sources.map((source, idx) => (
        <li key={idx} className="text-xs">
          <a 
            href={source.url} 
            target="_blank"
            className="text-blue-600 hover:underline"
          >
            {source.domain}
          </a>
        </li>
      ))}
    </ul>
  </div>
)}
```

---

## 性能优化

### 1. 并发控制
```python
semaphore = asyncio.Semaphore(5)  # 最多 5 个并发搜索
```

### 2. 缓存机制（可选）
```python
# 缓存搜索结果 5 分钟
cache_key = f"search:{query}:{timestamp // 300}"
```

### 3. 超时控制
```python
async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)):
    # 搜索请求
```

---

## 测试用例

### 测试 1: Stage 1 成功（白名单直接采信）

**输入**：
- 节点: "美联储利率"
- 搜索结果: 3 条来自 bloomberg.com、reuters.com、cnbc.com

**预期输出**：
```json
{
    "value": "5.25%",
    "confidence": "whitelist_direct",
    "sources": [...]
}
```

### 测试 2: Stage 2 成功（三方交叉验证通过）

**输入**：
- 节点: "比特币价格"
- Stage 1 失败（白名单无结果）
- Stage 2 全网搜索: 10 条结果，其中 3 个不同域名都提到 "$45,000"

**预期输出**：
```json
{
    "value": "$45,000",
    "confidence": "cross_validated",
    "sources": [3 个独立域名]
}
```

### 测试 3: Stage 2 失败（数据源不足）

**输入**：
- 节点: "某小众指标"
- Stage 1 失败
- Stage 2 全网搜索: 10 条结果，但只有 2 个域名提到数值

**预期输出**：
```json
{
    "value": "unknown",
    "confidence": "cross_validated",
    "narrative_context": "无法通过三方交叉验证，数据源不足或存在冲突"
}
```

### 测试 4: Stage 2 失败（数值冲突）

**输入**：
- 节点: "某争议性指标"
- Stage 2 全网搜索: 3 个域名分别提到 "5.0%"、"5.5%"、"6.0%"（不一致）

**预期输出**：
```json
{
    "value": "unknown",
    "confidence": "cross_validated",
    "narrative_context": "无法通过三方交叉验证，数据源不足或存在冲突"
}
```

---

## 配置文件更新

### `financial_sources.json`

```json
{
  "search_domains": {
    "broker_and_portals": {
      "description": "券商门户和财经聚合平台（中国市场）",
      "domains": [
        "eastmoney.com",
        "10jqka.com.cn",
        "finance.sina.com.cn",
        "wallstreetcn.com",
        "investing.com"
      ]
    }
  }
}
```

---

## 总结

### 核心优势

1. **数据真实性**：三方交叉验证消除虚假信息
2. **可追溯性**：每个数据都有 ≥3 个独立来源
3. **降级机制**：白名单失败时自动兜底
4. **透明度**：前端显示 confidence 徽章和 sources

### 关键指标

- **白名单域名数量**：27 个
- **三方验证阈值**：≥3 个独立域名
- **LLM 温度**：Stage 1 = 0.1，Stage 2 = 0.0
- **搜索结果数量**：Stage 1 = 3-5 条，Stage 2 = 10 条

### 未来优化方向

1. **动态白名单**：根据历史准确率动态调整白名单
2. **时间衰减**：优先采信最新数据
3. **权威性评分**：不同域名赋予不同权重
4. **用户反馈**：允许用户标记错误数据

---

**版本**: 2.0  
**更新时间**: 2026-02-19  
**作者**: CausalFlow Team

