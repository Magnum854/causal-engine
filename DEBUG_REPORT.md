# 因果引擎 Debug 报告

## 问题诊断

用户反馈：前端一直显示"运行中"状态，转圈无结果。

## 根本原因

通过审查代码和日志，发现了以下关键问题：

### 1. **CORS 配置错误** ⚠️ 最严重
**位置**: `backend/main.py`

**问题**: 
```python
allow_origins=["http://localhost:5173"]  # 只允许 5173 端口
```

**实际情况**: 前端运行在 5174 端口（因为 5173 被占用）

**影响**: 浏览器阻止所有跨域请求，导致前端无法与后端通信

**修复**:
```python
allow_origins=["http://localhost:5173", "http://localhost:5174"]  # 支持两个端口
```

---

### 2. **域名白名单加载失败** 🔧
**位置**: `backend/app/services/multi_tool_router_service.py`

**问题**: 
```python
def _get_all_search_domains(self) -> List[str]:
    domains = []
    for category in self.config["search_domains"].values():
        if isinstance(category, list):  # ❌ 错误：配置是嵌套字典，不是列表
            domains.extend(category)
    return domains
```

**结果**: 白名单域名数量为 0，导致所有搜索都失败

**修复**:
```python
def _get_all_search_domains(self) -> List[str]:
    domains = []
    for category_name, category_data in self.config["search_domains"].items():
        if category_name == "description":
            continue
        if isinstance(category_data, dict) and "domains" in category_data:
            domains.extend(category_data["domains"])
    return domains
```

**验证**: 日志显示从 `0 个` 增加到 `22 个` ✅

---

### 3. **默认路由规则缺失字段** 🔧
**位置**: `backend/app/services/multi_tool_router_service.py`

**问题**: 当节点类型没有匹配规则时，默认规则缺少 `tier_1_domains` 和 `tier_2_domains` 字段

**影响**: 瀑布流搜索逻辑无法获取白名单，导致搜索失败

**修复**:
```python
# 默认规则：使用新闻搜索
all_domains = self._get_all_search_domains()

return {
    "primary_strategy": "news_search",
    "fallback_strategy": None,
    "preferred_apis": [],
    "tier_1_domains": all_domains[:10] if len(all_domains) > 10 else all_domains,
    "tier_2_domains": all_domains[10:] if len(all_domains) > 10 else []
}
```

---

## 修复验证

### 后端日志对比

**修复前**:
```
2026-02-19 19:32:38 [INFO] - 搜索域名白名单: 0 个
```

**修复后**:
```
2026-02-19 21:15:04 [INFO] - 搜索域名白名单: 22 个
```

### 系统状态

✅ 后端运行正常 (PID: 20840, 端口: 8000)  
✅ 前端运行正常 (端口: 5174)  
✅ CORS 配置已修复  
✅ 域名白名单加载成功  
✅ 健康检查通过: `{"status":"healthy"}`

---

## 下一步操作

### 1. 刷新浏览器页面
按 `Ctrl + Shift + R` 强制刷新，清除缓存

### 2. 测试分析功能
在前端输入查询（如"黄金价格"），点击"开始分析"

### 3. 检查浏览器控制台
按 `F12` 打开开发者工具，查看是否还有错误

### 4. 查看后端日志
观察终端输出，确认请求正常处理

---

## 预期行为

修复后，系统应该：

1. **Pass 1**: 生成因果图谱拓扑结构（15-20秒）
2. **Pass 2**: 动态富化节点状态（10-15秒）
   - 使用 Yahoo Finance 直连获取金融数据
   - 使用新闻搜索获取其他信息
   - 白名单过滤确保数据质量
3. **返回结果**: 显示因果关系图谱，包含实时数据

---

## 技术细节

### 系统架构
- **前端**: Vite + React + ReactFlow (端口 5174)
- **后端**: FastAPI + Python (端口 8000)
- **LLM**: DeepSeek API (deepseek-reasoner 模型)
- **数据源**: Mock 模式（未配置真实搜索 API）

### 双阶段分析流程
1. **Pass 1**: LLM 生成因果图谱结构
2. **Pass 2**: 多路由数据获取
   - 路由 1: Yahoo Finance 直连（资产价格）
   - 路由 2: 结构化 API（宏观指标，Mock 模式）
   - 路由 3: 新闻搜索（事件/情绪，Mock 模式）

---

## 已修复文件清单

1. `backend/main.py` - CORS 配置
2. `backend/app/services/multi_tool_router_service.py` - 域名白名单加载 + 默认路由规则

---

## 注意事项

⚠️ **Mock 模式**: 当前系统运行在 Mock 模式，搜索引擎返回模拟数据。如需真实数据，请配置：
- `TAVILY_API_KEY` 或 `SERPER_API_KEY` (搜索引擎)
- `FRED_API_KEY` (美联储经济数据)
- `TUSHARE_TOKEN` (中国金融数据)

⚠️ **端口冲突**: 如果 5173 端口被释放，前端可能切换回 5173，届时需要重启前端服务。

---

生成时间: 2026-02-19 21:15  
修复人员: Claude (Cursor AI)

