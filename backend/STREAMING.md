# 流式输出 (Streaming) 功能文档

## 📋 概述

将因果推演过程升级为流式输出，前端实时展示"思考中"的进度反馈，提供更好的用户体验。

## 🔄 技术架构

### 后端：FastAPI + Server-Sent Events (SSE)
- 使用 `StreamingResponse` 返回流式数据
- 每个关键步骤推送进度事件
- 格式：`data: {"status": "...", "message": "...", "data": {...}}\n\n`

### 前端：ReadableStream + TextDecoder
- 使用 `response.body.getReader()` 读取流
- `TextDecoder` 解码数据块
- 按行分割解析 JSON 事件

## 🎯 API 接口

### POST /api/v1/research-target/stream

**流式版本**，实时推送分析进度。

**请求：**
```json
{
  "target": "中证1000指数"
}
```

**响应格式：** `text/event-stream`

**事件流示例：**
```
data: {"status": "start", "message": "开始分析标的: 中证1000指数", "timestamp": 1234567890.123}

data: {"status": "step1_start", "message": "正在提取核心影响因子...", "timestamp": 1234567890.456}

data: {"status": "step1_complete", "message": "因子提取完成 (耗时 3.5秒)", "data": {"factors": [...], "search_queries": [...], "elapsed": 3.5}, "timestamp": 1234567893.956}

data: {"status": "step2_start", "message": "正在搜索最新资讯 (5 个查询)...", "timestamp": 1234567894.001}

data: {"status": "step2_complete", "message": "搜索完成 (获取 8500 字符，耗时 12.3秒)", "data": {"context_length": 8500, "elapsed": 12.3}, "timestamp": 1234567906.301}

data: {"status": "step3_start", "message": "正在生成因果关系图谱...", "timestamp": 1234567906.350}

data: {"status": "step3_complete", "message": "图谱生成完成 (8 个节点，耗时 8.7秒)", "data": {"nodes_count": 8, "edges_count": 12, "elapsed": 8.7}, "timestamp": 1234567915.050}

data: {"status": "success", "message": "分析完成！总耗时 24.5秒", "data": {...完整的AnalysisResult...}, "timestamp": 1234567915.100}
```

## 📦 后端实现

### 1. 流式服务 (`streaming_research_service.py`)

```python
class StreamingTargetResearchService:
    async def stream_research_target(self, target: str) -> AsyncGenerator[str, None]:
        """流式执行标的研究 Pipeline"""
        
        # 步骤 1
        yield await self._send_progress("step1_start", "正在提取核心影响因子...")
        result = await self._step1_extract_factors(target)
        yield await self._send_progress("step1_complete", "因子提取完成", result)
        
        # 步骤 2
        yield await self._send_progress("step2_start", "正在搜索最新资讯...")
        context = await self._step2_perform_search(result["search_queries"])
        yield await self._send_progress("step2_complete", "搜索完成")
        
        # 步骤 3
        yield await self._send_progress("step3_start", "正在生成因果图谱...")
        analysis = await self._step3_generate_analysis(target, context, result["factors"])
        yield await self._send_progress("step3_complete", "图谱生成完成")
        
        # 完成
        yield await self._send_progress("success", "分析完成！", analysis)
```

### 2. API 路由 (`causal_router.py`)

```python
@router.post("/research-target/stream")
async def research_target_stream(request: TargetResearchRequest):
    """流式标的研究接口"""
    
    async def event_generator():
        try:
            async for event in streaming_research_service.stream_research_target(request.target):
                yield f"data: {event}\n\n"
        except Exception as e:
            error_event = json.dumps({"status": "error", "message": str(e)})
            yield f"data: {error_event}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
```

## 💻 前端实现

### 1. 流式客户端 (`streamClient.js`)

```javascript
export async function streamResearchTarget(target, config = {}) {
  const { onProgress, onComplete, onError, signal } = config

  const response = await fetch('/api/v1/research-target/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ target }),
    signal, // 支持取消
  })

  const reader = response.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const event = JSON.parse(line.slice(6))
        
        if (onProgress) onProgress(event)
        
        if (event.status === 'success') {
          if (onComplete) onComplete(event.data)
        }
        
        if (event.status === 'error') {
          throw new Error(event.message)
        }
      }
    }
  }
}
```

### 2. 加载动画组件 (`LoadingOverlay.jsx`)

**特性：**
- ✅ 心跳动画圆环
- ✅ 发光背景效果
- ✅ 实时进度文字
- ✅ 三步骤指示器
- ✅ 粒子装饰效果

```jsx
<LoadingOverlay
  isVisible={loading}
  message="正在提取核心影响因子..."
  progress={progressEvent}
/>
```

### 3. 流式研究页面 (`StreamingResearchPage.jsx`)

**完整的流式交互示例：**

```jsx
const handleStreamResearch = async () => {
  setLoading(true)
  const abortController = new AbortController()

  try {
    const response = await fetch('/api/v1/research-target/stream', {
      method: 'POST',
      body: JSON.stringify({ target }),
      signal: abortController.signal,
    })

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const event = JSON.parse(line.slice(6))
          setProgress(event) // 更新进度
          
          if (event.status === 'success') {
            setResult(event.data) // 设置结果
            setLoading(false)
          }
        }
      }
    }
  } catch (error) {
    setError(error)
    setLoading(false)
  }
}
```

## 🎨 UI 效果

### 加载动画

1. **心跳圆环**
   - 外圈：脉冲效果 (`animate-ping`)
   - 中圈：旋转效果 (`animate-spin`)
   - 内圈：发光核心 (`animate-pulse`)

2. **步骤指示器**
   - 未开始：灰色
   - 进行中：紫色渐变 + 脉冲
   - 已完成：绿色 + 对勾

3. **背景效果**
   - 发光渐变背景
   - 粒子浮动动画
   - 毛玻璃效果

### 进度消息映射

```javascript
const messages = {
  start: '开始分析...',
  step1_start: '正在提取核心影响因子...',
  step1_complete: '因子提取完成',
  step2_start: '正在搜索最新资讯...',
  step2_complete: '搜索完成',
  step3_start: '正在生成因果关系图谱...',
  step3_complete: '图谱生成完成',
  success: '分析完成！',
}
```

## 🔧 错误处理

### 后端容错

```python
try:
    # 执行步骤
    result = await self._step1_extract_factors(target)
    yield await self._send_progress("step1_complete", "完成", result)
except Exception as e:
    # 发送错误事件
    yield await self._send_progress("error", f"失败: {str(e)}")
    return  # 终止流
```

### 前端容错

```javascript
try {
  // 读取流
  while (true) {
    const { done, value } = await reader.read()
    // ...
  }
} catch (error) {
  if (error.name === 'AbortError') {
    console.log('请求已取消')
  } else {
    setError(error)
  }
} finally {
  setLoading(false)
}
```

### 请求取消

```javascript
// 创建 AbortController
const abortController = new AbortController()

// 传递 signal
fetch(url, { signal: abortController.signal })

// 取消请求
abortController.abort()

// 组件卸载时清理
useEffect(() => {
  return () => abortController.abort()
}, [])
```

## 📊 事件状态流转

```
start
  ↓
step1_start → step1_complete
  ↓
step2_start → step2_complete (或 step2_warning)
  ↓
step3_start → step3_complete
  ↓
success (或 error)
```

## 🚀 使用示例

### 基础使用

```jsx
import StreamingResearchPage from './StreamingResearchPage'

function App() {
  return <StreamingResearchPage />
}
```

### 自定义使用

```jsx
import { useState } from 'react'
import LoadingOverlay from './components/LoadingOverlay'

function CustomPage() {
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(null)

  const handleAnalyze = async () => {
    setLoading(true)
    
    const response = await fetch('/api/v1/research-target/stream', {
      method: 'POST',
      body: JSON.stringify({ target: '比特币' })
    })

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const event = JSON.parse(line.slice(6))
          setProgress(event)
          
          if (event.status === 'success') {
            console.log('完成:', event.data)
            setLoading(false)
          }
        }
      }
    }
  }

  return (
    <>
      <LoadingOverlay isVisible={loading} progress={progress} />
      <button onClick={handleAnalyze}>开始分析</button>
    </>
  )
}
```

## ⚡ 性能优化

### 后端优化

1. **异步生成器**：使用 `AsyncGenerator` 避免阻塞
2. **错误隔离**：每个步骤独立 try-catch
3. **超时控制**：设置合理的超时时间

### 前端优化

1. **增量解析**：按行解析，避免等待完整数据
2. **状态批量更新**：使用 `useState` 批量更新
3. **内存清理**：组件卸载时取消请求

## 🎯 最佳实践

1. **始终处理取消**：组件卸载时 abort 请求
2. **错误边界**：使用 try-catch 包裹流读取
3. **进度反馈**：每个关键步骤推送事件
4. **超时保护**：设置合理的超时时间
5. **日志记录**：记录每个事件用于调试

## 📚 相关文件

- `backend/app/services/streaming_research_service.py` - 流式服务
- `backend/app/api/causal_router.py` - API 路由
- `frontend/src/utils/streamClient.js` - 流式客户端
- `frontend/src/components/LoadingOverlay.jsx` - 加载动画
- `frontend/src/StreamingResearchPage.jsx` - 完整示例

---

现在你的因果推演引擎支持流式输出了！用户可以实时看到分析进度，体验更加流畅！🚀







