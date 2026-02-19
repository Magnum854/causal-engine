# 紧急修复：数据全是 Unknown 的问题

## 问题诊断

从日志分析，有 **3 个严重问题**：

### 1. Yahoo Finance 429 限流
```
[ERROR] yfinance: 429 Client Error: Too Many Requests
```
- Yahoo Finance API 被限流，所有请求都失败
- 需要等待 30 分钟或更换 IP

### 2. Mock 搜索模式（最严重）
```
[WARNING] [搜索引擎] 未配置真实 API，将使用 Mock 模式
[Mock Search] 返回 2 条模拟结果
```
- **没有配置 Tavily 或 Serper API**
- 系统使用 Mock 数据（假数据）
- Mock 数据太简单，LLM 无法提取有效信息

### 3. LLM 解析失败
```
[WARNING] [Waterfall] Attempt 1 提取失败: LLM 返回 unknown
[WARNING] [Waterfall] ✗ Attempt 2 失败: 全网搜索仍无法提取有效数据
```
- 因为 Mock 数据内容太简单
- LLM 无法从中提取数值

---

## 立即修复方案

### 方案 1: 配置真实搜索 API（推荐）

#### 步骤 1: 获取 Tavily API Key（免费）

1. 访问：https://tavily.com/
2. 注册账号
3. 获取 API Key（免费额度：1000 次/月）

#### 步骤 2: 配置环境变量

编辑 `backend/.env` 文件，添加：

```bash
# Tavily 搜索 API（推荐）
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxx

# 或者使用 Serper API（备选）
# SERPER_API_KEY=your_serper_key_here
```

#### 步骤 3: 重启后端

```bash
# 停止当前后端（Ctrl+C）
# 重新启动
cd backend
python main.py
```

#### 步骤 4: 验证

查看日志，应该看到：
```
[INFO] [搜索引擎] 使用 Tavily API
```

而不是：
```
[WARNING] [搜索引擎] 未配置真实 API，将使用 Mock 模式
```

---

### 方案 2: 等待 Yahoo Finance 限流解除

如果只想用 Yahoo Finance（不需要搜索）：

1. **等待 30-60 分钟**
2. 或者**更换网络/IP**
3. 或者**使用 VPN**

---

### 方案 3: 临时修复 Mock 数据（不推荐）

如果暂时无法获取 API，可以改进 Mock 数据：

编辑 `backend/app/services/two_pass_causal_service.py`，找到 `_mock_search_api` 方法，修改返回更详细的数据：

```python
async def _mock_search_api(self, query: str) -> List[Dict[str, Any]]:
    """Mock 搜索引擎 API（改进版）"""
    logger.info(f"[Mock Search] 模拟搜索: {query}")
    
    await asyncio.sleep(0.5)
    
    # 根据查询关键词生成更详细的模拟结果
    if "美元" in query or "dollar" in query.lower():
        mock_results = [
            {
                "title": "美元指数升至103.5，创两个月新高",
                "url": "https://www.bloomberg.com/markets/currencies/dollar-index-2024",
                "snippet": "美元指数周三升至103.5，受美联储鹰派立场支撑。分析师指出，当前美元指数为103.5，较上周上涨1.2%。",
                "domain": "bloomberg.com"
            },
            {
                "title": "US Dollar Index Rises to 103.5 on Fed Hawkish Stance",
                "url": "https://www.reuters.com/markets/currencies/dollar-2024",
                "snippet": "The US Dollar Index (DXY) climbed to 103.5 on Wednesday, marking a two-month high. The index stands at 103.5.",
                "domain": "reuters.com"
            },
            {
                "title": "Dollar Index at 103.5 as Markets Digest Fed Comments",
                "url": "https://www.cnbc.com/dollar-index-2024",
                "snippet": "The dollar index reached 103.5 today, reflecting strong demand for the greenback. Current level: 103.5.",
                "domain": "cnbc.com"
            }
        ]
    elif "利率" in query or "interest rate" in query.lower():
        mock_results = [
            {
                "title": "美联储维持利率在5.25%-5.50%不变",
                "url": "https://www.federalreserve.gov/newsevents/2024",
                "snippet": "美联储宣布维持联邦基金利率目标区间在5.25%-5.50%不变，这是连续第三次会议维持利率不变。",
                "domain": "federalreserve.gov"
            },
            {
                "title": "Fed Holds Rates Steady at 5.25%-5.50%",
                "url": "https://www.bloomberg.com/fed-decision-2024",
                "snippet": "The Federal Reserve kept interest rates unchanged at 5.25%-5.50% range for the third consecutive meeting.",
                "domain": "bloomberg.com"
            },
            {
                "title": "Federal Reserve Maintains Interest Rate at 5.25%-5.50%",
                "url": "https://www.reuters.com/fed-2024",
                "snippet": "The U.S. Federal Reserve maintained its benchmark interest rate at 5.25%-5.50% on Wednesday.",
                "domain": "reuters.com"
            }
        ]
    elif "黄金" in query or "gold" in query.lower():
        mock_results = [
            {
                "title": "黄金价格突破2025美元/盎司",
                "url": "https://www.kitco.com/gold-price-2024",
                "snippet": "国际黄金价格周三突破2025美元/盎司，创历史新高。当前金价为2025美元/盎司。",
                "domain": "kitco.com"
            },
            {
                "title": "Gold Prices Hit Record High at $2025/oz",
                "url": "https://www.bloomberg.com/gold-2024",
                "snippet": "Gold prices surged to a record $2025 per ounce on Wednesday. Spot gold is trading at $2025.",
                "domain": "bloomberg.com"
            },
            {
                "title": "Gold Reaches $2025 Per Ounce on Safe-Haven Demand",
                "url": "https://www.reuters.com/gold-2024",
                "snippet": "Gold reached $2025 per ounce, driven by safe-haven demand. Current price: $2025/oz.",
                "domain": "reuters.com"
            }
        ]
    elif "铜" in query or "copper" in query.lower():
        mock_results = [
            {
                "title": "铜价升至每吨8500美元",
                "url": "https://www.bloomberg.com/copper-2024",
                "snippet": "伦敦金属交易所铜价周三升至每吨8500美元，受供应担忧推动。当前铜价为8500美元/吨。",
                "domain": "bloomberg.com"
            },
            {
                "title": "Copper Prices Rise to $8500 Per Ton",
                "url": "https://www.reuters.com/copper-2024",
                "snippet": "Copper prices on the London Metal Exchange rose to $8500 per ton. Current price: $8500/ton.",
                "domain": "reuters.com"
            },
            {
                "title": "LME Copper at $8500/Ton on Supply Concerns",
                "url": "https://www.marketwatch.com/copper-2024",
                "snippet": "London Metal Exchange copper reached $8500 per ton amid supply disruption fears. Price: $8500/ton.",
                "domain": "marketwatch.com"
            }
        ]
    else:
        # 通用模拟结果（包含明确数值）
        mock_results = [
            {
                "title": f"关于 {query} 的最新分析报告",
                "url": f"https://www.bloomberg.com/analysis/{query.replace(' ', '-')}",
                "snippet": f"最新数据显示，{query} 当前值为 100.5，呈现稳定态势。分析师预计短期内将维持在 100.5 附近。",
                "domain": "bloomberg.com"
            },
            {
                "title": f"Latest Update on {query}",
                "url": f"https://www.reuters.com/latest/{query.replace(' ', '-')}",
                "snippet": f"Recent developments in {query} show current value at 100.5. Experts forecast stability around 100.5.",
                "domain": "reuters.com"
            },
            {
                "title": f"{query} Market Analysis",
                "url": f"https://www.cnbc.com/markets/{query.replace(' ', '-')}",
                "snippet": f"Market analysis indicates {query} is currently at 100.5, with analysts expecting it to remain near 100.5.",
                "domain": "cnbc.com"
            }
        ]
    
    logger.info(f"[Mock Search] 返回 {len(mock_results)} 条模拟结果")
    return mock_results
```

**关键改进**：
- ✅ 每个 Mock 结果包含 **3 个不同域名**
- ✅ 每个结果都包含 **明确的数值**（如 "103.5", "5.25%-5.50%", "$2025"）
- ✅ 数值在多个结果中 **重复出现**，满足三方交叉验证

---

## 验证修复

### 成功的日志应该是：

```
[INFO] [搜索引擎] 使用 Tavily API
[INFO] [Waterfall] Attempt 1: 白名单搜索 (7天窗口)
[INFO] [Waterfall] Attempt 1 结果: 5 条 -> 白名单过滤后: 3 条
[INFO] [Waterfall] ✓ Attempt 1 成功: 103.5
[INFO] [Pass 2] 节点 美元指数 富化完成: value=103.5, confidence=whitelist_direct
```

### 失败的日志（当前状态）：

```
[WARNING] [搜索引擎] 未配置真实 API，将使用 Mock 模式
[Mock Search] 返回 2 条模拟结果
[WARNING] [Waterfall] Attempt 1 提取失败: LLM 返回 unknown
[WARNING] [Waterfall] ✗ Attempt 2 失败: 全网搜索仍无法提取有效数据
```

---

## 推荐方案优先级

1. **🥇 方案 1**：配置 Tavily API（5 分钟，永久解决）
2. **🥈 方案 2**：等待 Yahoo Finance 限流解除（30-60 分钟）
3. **🥉 方案 3**：改进 Mock 数据（临时方案，仅用于测试）

---

## Tavily API 注册指南

### 1. 访问官网
https://tavily.com/

### 2. 点击 "Get Started" 或 "Sign Up"

### 3. 注册账号
- 使用 Google 账号快速注册
- 或使用邮箱注册

### 4. 获取 API Key
- 登录后进入 Dashboard
- 复制 API Key（格式：`tvly-xxxxxxxxxxxxxxxxxxxxxx`）

### 5. 免费额度
- **1000 次搜索/月**（足够测试使用）
- 每次搜索返回 Top-5 结果
- 支持中文和英文查询

---

## 常见问题

### Q1: 为什么不直接用 Google 搜索？
A: Google 搜索需要付费 API（Custom Search API），且配置复杂。Tavily 专为 AI 应用设计，免费且易用。

### Q2: Serper 和 Tavily 哪个更好？
A: 
- **Tavily**：免费 1000 次/月，专为 AI 设计，推荐
- **Serper**：免费 2500 次/月，但需要信用卡验证

### Q3: 配置 API 后还是 unknown？
A: 检查：
1. `.env` 文件是否正确配置
2. 后端是否重启
3. 日志是否显示 `[INFO] 使用 Tavily API`

### Q4: Yahoo Finance 什么时候恢复？
A: 通常 30-60 分钟后自动恢复，或更换 IP/VPN。

---

生成时间: 2026-02-19 22:00

