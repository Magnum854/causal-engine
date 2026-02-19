# API 配置说明

## 🔑 DeepSeek API 配置

你的 API 密钥已准备好，请按以下步骤配置：

### 步骤 1: 创建 .env 文件

在 `backend` 目录下创建 `.env` 文件（如果不存在）：

```bash
cd backend
touch .env  # Linux/Mac
# 或在 Windows 中直接创建文件
```

### 步骤 2: 填入配置

将以下内容复制到 `backend/.env` 文件中：

```env
# OpenAI API 配置（使用 DeepSeek）
OPENAI_API_KEY=sk-808aa93c9409413bbfcf66505a96de94
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat

# 摘要生成使用的快速模型（可选）
OPENAI_SUMMARY_MODEL=deepseek-chat

# 服务器配置
HOST=0.0.0.0
PORT=8000

# 搜索引擎配置（至少配置一个）
# 选项 1: Tavily (推荐，专为 AI 优化)
# 注册地址: https://tavily.com/
# TAVILY_API_KEY=your_tavily_key

# 选项 2: Serper.dev (基于 Google)
# 注册地址: https://serper.dev/
# SERPER_API_KEY=your_serper_key

# 选项 3: DuckDuckGo (免费，无需 key)
# 需要安装: pip install duckduckgo-search
SEARCH_ENGINE=duckduckgo
```

### 步骤 3: 验证配置

启动后端服务测试配置是否正确：

```bash
cd backend
python main.py
```

如果看到以下输出，说明配置成功：

```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 🔍 搜索引擎配置（可选）

标的研究功能需要搜索引擎支持，有三个选项：

### 选项 1: DuckDuckGo（推荐，免费）

**优点**: 完全免费，无需 API Key

**安装**:
```bash
pip install duckduckgo-search
```

**配置**:
```env
SEARCH_ENGINE=duckduckgo
```

### 选项 2: Tavily（推荐，质量高）

**优点**: 专为 AI 优化，结果质量高

**注册**: https://tavily.com/ （免费额度 1000 次/月）

**配置**:
```env
TAVILY_API_KEY=your_tavily_key
SEARCH_ENGINE=tavily
```

### 选项 3: Serper.dev（基于 Google）

**优点**: 基于 Google，结果准确

**注册**: https://serper.dev/ （免费额度 2500 次）

**配置**:
```env
SERPER_API_KEY=your_serper_key
SEARCH_ENGINE=serper
```

## ✅ 配置检查清单

- [ ] 创建 `backend/.env` 文件
- [ ] 填入 DeepSeek API Key: `sk-808aa93c9409413bbfcf66505a96de94`
- [ ] 设置 Base URL: `https://api.deepseek.com/v1`
- [ ] 设置模型: `deepseek-chat`
- [ ] 配置搜索引擎（推荐 DuckDuckGo）
- [ ] 安装依赖: `pip install -r requirements.txt`
- [ ] 如果使用 DuckDuckGo: `pip install duckduckgo-search`
- [ ] 启动服务测试: `python main.py`

## 🧪 测试 API 连接

### 测试基础因果分析

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "query": "全球变暖会导致什么后果？",
    "max_depth": 3
  }'
```

### 测试新闻提取

```bash
curl -X POST http://localhost:8000/api/v1/extract-causality \
  -H "Content-Type: application/json" \
  -d '{
    "news_text": "美联储宣布加息50个基点，导致美股大幅下跌。",
    "generate_summary": true
  }'
```

### 测试流式标的研究

```bash
curl -N -X POST http://localhost:8000/api/v1/research-target/stream \
  -H "Content-Type: application/json" \
  -d '{
    "target": "中证1000指数"
  }'
```

## 🔒 安全提示

1. **不要提交 .env 文件到 Git**
   - `.env` 文件已在 `.gitignore` 中
   - 永远不要将 API Key 提交到代码仓库

2. **定期更换 API Key**
   - 如果 Key 泄露，立即在 DeepSeek 控制台重新生成

3. **监控 API 使用量**
   - 登录 DeepSeek 控制台查看使用情况
   - 设置使用量告警

## 📊 DeepSeek 模型说明

### deepseek-chat

- **类型**: 对话模型
- **上下文长度**: 32K tokens
- **适用场景**: 
  - 因果关系分析
  - 新闻文本提取
  - 标的研究
  - 摘要生成

### 定价（参考）

- 输入: ¥1/百万 tokens
- 输出: ¥2/百万 tokens

**预估成本**:
- 单次因果分析: ~0.01-0.05 元
- 标的研究（含搜索）: ~0.05-0.15 元

## 🆘 常见问题

### Q1: API Key 无效

**错误**: `401 Unauthorized`

**解决**: 
1. 检查 API Key 是否正确复制
2. 确认 Key 未过期
3. 登录 DeepSeek 控制台验证

### Q2: 连接超时

**错误**: `Connection timeout`

**解决**:
1. 检查网络连接
2. 确认 Base URL 正确
3. 尝试使用代理

### Q3: 模型不存在

**错误**: `Model not found`

**解决**:
1. 确认使用 `deepseek-chat`
2. 检查 DeepSeek 控制台可用模型

### Q4: 搜索功能不工作

**解决**:
1. 确认已安装 `duckduckgo-search`
2. 或配置 Tavily/Serper API Key
3. 检查 `SEARCH_ENGINE` 环境变量

## 📞 获取帮助

- DeepSeek 文档: https://platform.deepseek.com/docs
- 项目 README: ../README.md
- API 测试文档: ./API_TEST.md
- 流式功能文档: ./STREAMING.md

---

配置完成后，你就可以开始使用因果推演引擎了！🚀







