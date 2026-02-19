# 快速测试指南

## 立即测试修复结果

### 方法 1: 浏览器测试（推荐）

1. **打开浏览器**
   访问: http://localhost:5174

2. **强制刷新页面**
   按 `Ctrl + Shift + R` (Windows) 或 `Cmd + Shift + R` (Mac)

3. **输入测试查询**
   在"分析问题"框中输入: `黄金价格`

4. **点击"开始分析"**
   等待 20-30 秒，应该看到因果关系图谱

5. **检查结果**
   - 应该显示多个节点（美元指数、美联储利率、通货膨胀等）
   - 每个节点应该有实时数据（如果有的话）
   - 底部应该显示数据源面板

---

### 方法 2: API 直接测试

打开新的 PowerShell 窗口，运行：

```powershell
# 测试健康检查
Invoke-RestMethod -Uri "http://localhost:8000/health"

# 测试因果分析（需要等待 30-60 秒）
$body = @{
    query = "黄金价格"
    context = $null
    max_depth = 3
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/analyze-v2" `
    -Method POST `
    -Body $body `
    -ContentType "application/json" `
    -TimeoutSec 60
```

---

## 预期结果

### 成功的标志

✅ 前端不再一直转圈  
✅ 20-30秒后显示因果图谱  
✅ 节点包含实时数据（部分节点可能显示 "unknown"，这是正常的 Mock 模式行为）  
✅ 浏览器控制台没有 CORS 错误  

### 正常的 Mock 模式行为

由于系统运行在 Mock 模式（未配置真实 API），部分节点可能显示：
- `latest_value: "unknown"` - 这是正常的
- `latest_value: "稳定趋势"` - 这是 LLM 从模拟数据中提取的
- `latest_value: "103.5"` - 这是从模拟新闻中提取的数值

---

## 如果还有问题

### 1. 检查浏览器控制台
按 `F12` 打开开发者工具，查看 Console 标签页：
- ❌ 如果看到 CORS 错误 → 后端可能没有重启，等待几秒
- ❌ 如果看到 Network Error → 检查后端是否运行在 8000 端口

### 2. 检查后端日志
查看运行后端的终端窗口：
- ✅ 应该看到: `搜索域名白名单: 22 个`
- ✅ 应该看到: `Application startup complete`
- ❌ 如果看到错误 → 查看 DEBUG_REPORT.md

### 3. 重启服务（如果需要）

**重启后端**:
```powershell
# 在后端终端按 Ctrl+C 停止
# 然后重新运行
cd X:\因果引擎\backend
python main.py
```

**重启前端**:
```powershell
# 在前端终端按 Ctrl+C 停止
# 然后重新运行
cd X:\因果引擎\frontend
npm run dev
```

---

## 查看详细日志

### 后端日志位置
终端 6: `c:\Users\28203\.cursor\projects\x\terminals\6.txt`

### 前端日志位置
终端 1: `c:\Users\28203\.cursor\projects\x\terminals\1.txt`

---

## 示例查询

试试这些查询来测试系统：

1. **金融类**
   - 黄金价格
   - 美元指数
   - 比特币价格

2. **宏观经济**
   - 通货膨胀的原因
   - 经济衰退的影响

3. **社会问题**
   - 全球变暖会导致什么后果
   - 人工智能发展对就业市场的影响

---

## 技术支持

如果问题仍然存在，请提供：
1. 浏览器控制台截图（F12 → Console）
2. 后端日志最后 50 行
3. 具体的错误信息

---

最后更新: 2026-02-19 21:15

