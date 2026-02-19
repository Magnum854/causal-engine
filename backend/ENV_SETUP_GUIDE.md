# 环境变量配置指南

## 问题诊断

你的系统显示：
```
[WARNING] [搜索引擎] 未配置真实 API，将使用 Mock 模式
```

**原因**：`backend/.env` 文件不存在或未配置 `TAVILY_API_KEY`

---

## 立即修复步骤

### 1. 创建 `.env` 文件

在 `backend` 目录下创建 `.env` 文件（注意文件名以点开头）：

**Windows 创建方法**：
```powershell
# 方法 1: 使用记事本
notepad X:\因果引擎\backend\.env

# 方法 2: 使用 PowerShell
New-Item -Path "X:\因果引擎\backend\.env" -ItemType File
```

### 2. 填写以下内容

```env
# OpenAI API 配置（DeepSeek）
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-reasoner

# Tavily 搜索 API（必须配置！）
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxx

# Serper 搜索 API（备选，可选）
# SERPER_API_KEY=your_serper_key_here
```

### 3. 获取 Tavily API Key

1. 访问：https://tavily.com/
2. 点击 "Sign Up" 注册
3. 登录后进入 Dashboard
4. 复制 API Key（格式：`tvly-xxxxxxxxxxxxxxxxxxxxxx`）
5. 粘贴到 `.env` 文件的 `TAVILY_API_KEY=` 后面

### 4. 重启后端

```powershell
# 停止当前后端（Ctrl+C）
# 重新启动
cd X:\因果引擎\backend
python main.py
```

### 5. 验证配置成功

启动后，日志应该显示：

✅ **成功**：
```
[INFO] [搜索引擎] 使用 Tavily API
```

❌ **失败**（当前状态）：
```
[WARNING] [搜索引擎] 未配置真实 API，将使用 Mock 模式
```

---

## 完整的 .env 文件示例

```env
# ============================================
# OpenAI API 配置
# ============================================
OPENAI_API_KEY=sk-1234567890abcdefghijklmnopqrstuvwxyz
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-reasoner

# ============================================
# 搜索引擎 API（必须配置其中一个）
# ============================================

# Tavily API（推荐）
TAVILY_API_KEY=tvly-abcdefghijklmnopqrstuvwxyz123456

# Serper API（备选）
# SERPER_API_KEY=your_serper_api_key_here

# ============================================
# Yahoo Finance（无需配置）
# ============================================
# Yahoo Finance 自动使用，无需 API Key
```

---

## 常见问题

### Q1: 如何确认 .env 文件创建成功？

```powershell
# 检查文件是否存在
Test-Path "X:\因果引擎\backend\.env"
# 应该返回 True

# 查看文件内容
Get-Content "X:\因果引擎\backend\.env"
```

### Q2: 为什么 Windows 无法创建 .env 文件？

Windows 资源管理器不允许创建以点开头的文件。解决方法：
- 使用记事本：`notepad .env`
- 使用 VS Code：直接在编辑器中创建
- 使用 PowerShell：`New-Item -Path .env -ItemType File`

### Q3: 配置后还是 Mock 模式？

检查：
1. `.env` 文件是否在 `backend` 目录（不是 `backend/app`）
2. `TAVILY_API_KEY=` 后面是否有实际的 API Key
3. 是否重启了后端服务

### Q4: Tavily API 免费吗？

是的！免费额度：
- 1000 次搜索/月
- 每次搜索返回 Top-5 结果
- 足够测试和小规模使用

---

## 下一步

配置完成后，刷新浏览器，重新测试"铜价"或"黄金价格"查询，应该能看到真实数据而不是 `unknown`！

---

生成时间: 2026-02-19 22:05

