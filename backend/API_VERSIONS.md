# API 版本说明

本项目提供两个版本的 API，分别适用于不同的使用场景。

## v1 API (Legacy - 无状态)

**路径前缀:** `/api/v1/`

**特点:**
- 无状态设计，每次请求独立处理
- 多种服务实现可选
- 适合简单的一次性分析

**主要端点:**
- `POST /api/v1/analyze` - 基础因果分析
- `POST /api/v1/analyze-v2` - 增强因果分析
- `POST /api/v1/extract-causality` - 新闻因果关系提取
- `POST /api/v1/research-target` - 目标研究分析
- `POST /api/v1/research-target/stream` - 流式目标研究
- `POST /api/v1/research-target-enhanced` - 增强目标研究
- `POST /api/v1/enrich-nodes` - 节点富化

**服务实现:**
- `causal_service.py` - 基础因果分析
- `target_research_service.py` - 目标研究（三步流程）
- `streaming_research_service.py` - 流式研究
- `enhanced_research_service.py` - 增强研究（集成节点感知）
- `two_pass_causal_service.py` - 双阶段分析
- `news_extraction_service.py` - 新闻提取

**适用场景:**
- 快速原型开发
- 简单的一次性分析
- 不需要保存历史状态的场景

---

## v2 API (Recommended - 会话式)

**路径前缀:** `/api/v2/`

**特点:**
- 会话式设计，支持多轮交互
- SQLite 持久化存储
- 支持撤销/重做操作
- 多输入综合分析
- 更强大的状态管理

**主要端点:**
- `POST /api/v2/sessions` - 创建会话
- `GET /api/v2/sessions/{id}` - 获取会话
- `POST /api/v2/sessions/{id}/analyze-deep` - 深度分析（流式）
- `POST /api/v2/sessions/{id}/synthesize` - 综合多输入（流式）
- `POST /api/v2/sessions/{id}/expand` - 扩展节点
- `POST /api/v2/sessions/{id}/add-input` - 添加输入
- `POST /api/v2/sessions/{id}/undo` - 撤销操作
- `GET /api/v2/sessions/{id}/graph` - 获取图谱
- `POST /api/v2/sessions/{id}/data/refresh/{node_id}` - 刷新节点数据
- `POST /api/v2/data/refresh/{node_id}` - 全局节点刷新
- `POST /api/v2/suggestions` - 获取建议

**服务实现:**
- `v2_analysis_service.py` - 会话式分析服务

**适用场景:**
- 需要多轮交互的复杂分析
- 需要保存分析历史
- 需要撤销/重做功能
- 多输入综合分析
- 生产环境推荐使用

---

## 迁移指南

### 从 v1 迁移到 v2

**1. 创建会话**
```python
# v1: 直接调用分析
response = requests.post("/api/v1/analyze", json={"query": "..."})

# v2: 先创建会话
session = requests.post("/api/v2/sessions", json={
    "title": "我的分析",
    "description": "..."
}).json()
session_id = session["id"]
```

**2. 执行分析**
```python
# v1: 一次性分析
response = requests.post("/api/v1/analyze", json={"query": "..."})

# v2: 会话式分析（支持流式）
response = requests.post(
    f"/api/v2/sessions/{session_id}/analyze-deep",
    json={"query": "..."},
    stream=True
)
```

**3. 多轮交互**
```python
# v2 独有功能：添加新输入
requests.post(
    f"/api/v2/sessions/{session_id}/add-input",
    json={"input_text": "新的分析维度"}
)

# v2 独有功能：综合分析
requests.post(
    f"/api/v2/sessions/{session_id}/synthesize",
    stream=True
)
```

**4. 撤销操作**
```python
# v2 独有功能：撤销上一步操作
requests.post(f"/api/v2/sessions/{session_id}/undo")
```

---

## 性能对比

| 特性 | v1 API | v2 API |
|------|--------|--------|
| 响应速度 | 快（无状态） | 中等（需要加载会话） |
| 内存占用 | 低 | 中等（会话缓存） |
| 持久化 | 无 | SQLite |
| 并发支持 | 高 | 中等 |
| 功能丰富度 | 基础 | 高级 |

---

## 推荐使用

- **新项目:** 使用 v2 API
- **简单场景:** 可以使用 v1 API
- **生产环境:** 推荐 v2 API
- **原型开发:** v1 或 v2 都可以

---

## 维护状态

- **v1 API:** 维护模式，不再添加新功能，但会修复关键 bug
- **v2 API:** 活跃开发，持续添加新功能

---

## 相关文档

- v1 API 详细文档: `backend/API_TEST.md`
- v2 API 详细文档: `docs/v2-api-guide.md`
- v2 架构说明: `docs/v2-architecture.md`
- v2 运维手册: `docs/v2-runbook.md`
