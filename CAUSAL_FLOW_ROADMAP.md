# 因果推演引擎 - 系统架构文档 (SSOT)

## 核心愿景

构建一个全自动因果推断引擎，将碎片化的宏观经济、地缘政治新闻转化为由"节点"和"有向边"构成的知识图谱。通过 AI 驱动的因果关系抽取，实现从非结构化文本到结构化因果链的自动化转换，为金融市场宏观分析提供可视化、可追溯的推理依据。

---

## 技术架构

### 表现层 (Frontend)
- **技术栈**: React + Vite + ReactFlow
- **职责**: 因果图谱可视化渲染、交互式节点编辑、实时流式数据展示
- **核心组件**: `CausalGraphViewer`, `CustomNode`, `StreamingResearchPage`

### 逻辑层 (Backend API)
- **技术栈**: FastAPI + Pydantic
- **职责**: JSON 数据流转、路由分发、业务逻辑编排
- **标准数据结构**:
  ```json
  {
    "nodes": [{"id", "label", "type", "description", "confidence"}],
    "edges": [{"source", "target", "label", "strength"}],
    "explanation": "string",
    "metadata": {}
  }
  ```

### 抽取层 (AI Parsing)
- **技术栈**: OpenAI API (DeepSeek)
- **职责**: 文本 → 因果关系提取、关键词生成、联网搜索整合
- **核心服务**: `NewsExtractionService`, `TargetResearchService`, `StreamingResearchService`

---

## 开发路线图

### 阶段一：定义标准因果 JSON 结构 & 实现前端静态图谱渲染
**状态**: ✅ 已完成
- 定义 `AnalysisResult` 数据模型 (nodes/edges/explanation)
- 实现 ReactFlow 图谱渲染引擎
- 支持自定义节点样式与布局算法

### 阶段二：开发基础事件录入接口 (API)
**状态**: ✅ 已完成
- `/api/v1/analyze` - 通用因果分析
- `/api/v1/extract-causality` - 新闻文本因果提取
- `/api/v1/research-target` - 标的逆向推演

### 阶段三：集成 LLM 实现文本到图论结构的自动化解析
**状态**: ✅ 已完成
- 集成 DeepSeek API 进行因果关系抽取
- 实现 JSON 强制输出与结构化验证
- 支持流式响应 (SSE) 实时推送分析进度

### 阶段四：增强功能
**状态**: ✅ 已完成
- 智能摘要生成 (基于因果图复杂度动态调整)
- 联网搜索集成 (DuckDuckGo)
- 多轮对话上下文保持

### 阶段五：节点自主感知 (Autonomous Sensing)
**状态**: ✅ 已完成
- 实现异步智能体搜索管道 (Agentic Search Pipeline)
- 集成 Tavily/Serper 搜索引擎 API
- LLM 驱动的信息抽取与结构化输出
- 并发处理与降级策略
- 反幻觉机制（无数据 → unknown）

### 阶段六：双阶段架构 + 数据溯源 (Two-Pass with Provenance)
**状态**: ✅ 已完成
- Pass 1: 生成因果图谱拓扑结构（每个节点包含 search_query）
- Pass 2: 动态富化节点状态 + 严格数据溯源
- Mock 搜索引擎支持（无需真实 API 即可测试）
- 节点卡片显示实时状态栏和数据源角标
- 全局数据源面板（底部展示所有引用来源）
- 完整的数据可追溯性（title, url, domain）

---

## 更新日志 (Changelog)

| 日期 | 核心改动 | 涉及文件 | 对应的商业逻辑 |
|------|---------|---------|---------------|
| 2026-02-19 | UI 全面重构：转向现代极简白风格 (Notion/Linear Style) | `App.jsx`, `CustomNode.jsx`, `DataSourcesPanel.jsx`, `CausalGraph.jsx`, `QueryPanel.jsx` | 提高数据展示信噪比：纯白背景、左侧彩色边线区分节点类型、柔和石板灰连线、极简边框和阴影，摒弃高饱和度色块 |
| 2026-02-19 | 实现双阶段架构 + 数据溯源系统 (Two-Pass Pipeline with Provenance) | `two_pass_causal_service.py`, `CustomNode.jsx`, `DataSourcesPanel.jsx`, `App.jsx` | 架构升级：Pass 1 生成拓扑 → Pass 2 联网富化 + 溯源。节点显示实时状态，底部面板展示所有数据源，实现完整的数据可追溯性 |
| 2026-02-19 | 实现增强型标的研究 - 因果分析与实时状态的完整闭环 | `enhanced_research_service.py`, `causal_router.py`, `ENHANCED_RESEARCH_GUIDE.md` | 解决核心痛点：不仅分析"哪些因素影响标的"，还自动获取"这些因素的当前状态"，实现端到端的智能分析 |
| 2026-02-19 | 实现节点自主感知功能 (Autonomous Sensing) | `node_sensing_service.py`, `causal_router.py`, `NODE_SENSING_API.md` | 解决"引擎只知道因果关系，不知道实时状态"的痛点，实现图谱节点的自动状态更新 |
| 2026-02-19 | 创建生产环境部署配置，支持 Docker 和传统部署 | `DEPLOYMENT.md`, `Dockerfile`, `docker-compose.yml`, `nginx.conf` | 实现一键部署，降低运维成本，支持快速上线 |
| 2026-02-19 | 统一所有服务使用 DeepSeek Reasoner 深度思考模型 | `*_service.py`, `requirements.txt` | 确保因果推理质量，利用深度思考能力提升分析准确度 |
| 2026-02-19 | 修复环境变量加载顺序问题 | `main.py` | 解决启动报错，确保 API 密钥正确加载 |
| 2026-02-19 | 初始化系统架构文档，建立 SSOT | `CAUSAL_FLOW_ROADMAP.md` | 统一项目上下文，确保所有开发决策基于单一真相源 |

---

## 数据流转示意

```
用户输入 (文本/标的)
    ↓
FastAPI 路由层
    ↓
AI 服务层 (LLM 调用)
    ↓
JSON 结构化输出
    ↓
前端 ReactFlow 渲染
    ↓
可视化因果图谱
```

---

## 关键约束

1. **数据格式**: 所有 API 响应必须符合 `AnalysisResult` 标准结构
2. **节点类型**: 仅限 `cause` / `effect` / `intermediate` / `hypothesis` / `evidence`
3. **边的强度**: `strength` 字段范围 [0.0, 1.0]
4. **JSON 验证**: 必须验证节点引用完整性 (边的 source/target 必须存在于 nodes 中)

---

## 未来扩展方向

- [ ] 知识图谱持久化 (Neo4j / 向量数据库)
- [ ] 多模态输入 (图片、视频、音频)
- [ ] 因果链推理引擎 (基于概率图模型)
- [ ] 协作编辑与版本控制
- [ ] 节点状态时间序列追踪
- [ ] WebSocket 实时状态推送

