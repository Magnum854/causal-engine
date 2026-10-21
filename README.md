# CausalFlow — 因果推演引擎

由 [Magnum854](https://github.com/Magnum854) 维护的 React + FastAPI 宏观事件因果分析工作台。项目以 CausalFlow v2 会话工作流为主线，代码按 [MIT License](LICENSE) 开源；依赖项保留各自的许可证。

维护范围包括多输入分析、图谱交互、会话持久化、接口与部署配置。参与开发见 [CONTRIBUTING.md](CONTRIBUTING.md)，密钥处理见 [SECURITY.md](SECURITY.md)。

## CausalFlow v2 当前状态

当前主线为 CausalFlow v2 工作台：

- 多输入综合分析：左侧面板可输入多条事件/数据/新闻/问题，后端通过 `/api/v2/sessions/{session_id}/synthesize` 以 SSE 推送阶段进度。
- 深度迭代扩展：后端通过 `/api/v2/sessions/{session_id}/analyze-deep` 按层生成增量图谱。
- 会话管理：v2 会话使用 SQLite 持久化，默认运行态路径为 `backend/data/causal_v2.sqlite3`。
- 节点扩展：点击图谱节点后，可通过 `/api/v2/sessions/{session_id}/expand` 扩展原因、影响或相关因素。
- 图谱呈现：前端使用分层泳道布局、聚类筛选、主干/聚焦/全部边模式，避免大图节点重叠和连线过密。
- 数据管道：搜索感知支持 15 秒超时、3 次指数退避、15 分钟缓存和来源质量评分；结构化数据服务新增 yfinance 入口。

没有配置 LLM 密钥时，v2 可以使用确定性规则生成基础图谱。实时搜索、模型推理与外部数据增强需要各自的服务配置；规则图谱不代表已经核实的实时因果关系。

**API 版本说明:**
- **v2 API** (推荐): 会话式设计，支持多轮交互、撤销/重做、多输入综合分析。详见 `backend/API_VERSIONS.md`
- **v1 API** (维护模式): 无状态设计，适合简单的一次性分析。

详细说明见：

- `docs/v2-architecture.md`
- `docs/v2-api-guide.md`
- `docs/v2-runbook.md`
- `backend/API_VERSIONS.md` (v1 vs v2 对比和迁移指南)

一个基于大模型的因果推演引擎，用于分析和可视化事件之间的因果关系。

## ✨ 核心功能

- 🧠 **智能因果分析**: 基于 DeepSeek 大模型的因果关系推理
- 📊 **可视化图谱**: 使用 React Flow 展示因果关系网络
- 🔍 **标的研究**: 逆向推演 + 实时搜索 + 因果分析
- 📝 **新闻提取**: 从新闻文本中自动提取因果关系
- 💬 **智能摘要**: 根据图复杂度动态生成分析简报
- 🌊 **流式输出**: 实时展示分析进度，提供流畅体验

## 技术栈

### 前端
- **框架**: React 18 + Vite
- **样式**: Tailwind CSS
- **可视化**: @xyflow/react (React Flow v12) + Dagre 自动布局
- **HTTP 客户端**: Fetch API (原生)

### 后端
- **框架**: FastAPI
- **AI 模型**: DeepSeek API (兼容 OpenAI 格式)
- **搜索引擎**: DuckDuckGo / Tavily / Serper
- **异步支持**: Uvicorn + AsyncIO

## 项目结构

```
因果引擎/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API 路由
│   │   │   ├── __init__.py
│   │   │   └── causal_router.py
│   │   ├── services/       # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   └── causal_service.py
│   │   └── __init__.py
│   ├── main.py             # 应用入口
│   ├── requirements.txt    # Python 依赖
│   └── .env.example        # 环境变量示例
│
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── components/     # React 组件
│   │   │   ├── CausalGraph.jsx
│   │   │   └── QueryPanel.jsx
│   │   ├── App.jsx         # 主应用组件
│   │   ├── main.jsx        # 应用入口
│   │   └── index.css       # 全局样式
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
│
├── .gitignore
└── README.md
```

## 快速开始

Docker 同源部署使用仓库根目录的 `Dockerfile` 与 `docker-compose.yml`，运行 `docker compose up -d --build` 后打开 `http://localhost:8000`。无密钥时可先体验 v2 规则图谱；持久化、可选环境配置与启动检查见 [v2 runbook](docs/v2-runbook.md) 和 [部署指南](DEPLOYMENT.md)。

### 方法 1: 使用自动配置脚本（推荐）

**Windows 用户:**
```bash
cd backend
setup.bat
```

**Linux/Mac 用户:**
```bash
cd backend
bash setup.sh
```

脚本会自动：
- ✅ 创建 `.env` 配置文件
- ✅ 创建 DeepSeek/OpenAI 兼容 API 配置占位
- ✅ 安装 Python 依赖
- ✅ 安装搜索引擎支持

### 方法 2: 手动配置

#### 1. 环境准备

确保已安装：
- Node.js 18+ 和 npm/yarn
- Python 3.9+

#### 2. 后端设置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装搜索引擎支持（可选）
pip install duckduckgo-search

# 创建 .env 配置文件
# 复制模板，按需在本机填写密钥：
cp .env.example .env
```

**backend/.env 文件内容:**
```env
# DeepSeek/OpenAI 兼容 API 配置
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat

# 服务器配置
HOST=0.0.0.0
PORT=8000

# 搜索引擎配置（使用免费的 DuckDuckGo）
SEARCH_ENGINE=duckduckgo
```

`OPENAI_API_KEY` 留空可先体验 v2 规则图谱。真实密钥只放入被 Git 忽略的 `backend/.env`；不要提交到示例、文档、截图或 Issue。

```bash
# 启动后端服务
python main.py
```

后端服务将在 `http://localhost:8000` 启动

#### 3. 前端设置

```bash
# 打开新终端，进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用将在 `http://localhost:5173` 启动

#### 4. 访问应用

在浏览器中打开 `http://localhost:5173`，即可开始使用因果推演引擎。

### 🎯 快速测试

启动服务后，可以测试以下功能：

1. **基础因果分析**: 输入"全球变暖会导致什么后果？"
2. **新闻提取**: 粘贴一段新闻文本，自动提取因果关系
3. **标的研究**: 输入"中证1000指数"，查看实时分析
4. **流式体验**: 观察实时进度反馈和炫酷的加载动画

## 功能特性

### 🎯 核心功能

#### 1. 基础因果分析 (`/api/v1/analyze`)
- 自然语言因果关系推理
- 可调节分析深度（1-5层）
- 支持背景信息输入
- 生成结构化因果图谱

#### 2. 新闻因果提取 (`/api/v1/extract-causality`)
- 从新闻文本自动提取因果关系
- 智能识别原因、结果、中间节点
- 评估因果强度和置信度
- 可选生成智能摘要（简单/复杂两种模式）

#### 3. 标的研究 (`/api/v1/research-target`)
- **步骤 1**: 逆向因子提取 + 关键词生成
- **步骤 2**: 并发联网搜索最新资讯
- **步骤 3**: 综合分析生成因果图谱
- 支持流式输出 (`/stream`)，实时展示进度

#### 4. 可视化图谱
- 基于 React Flow + Dagre 自动布局
- 5 种节点类型（原因、结果、中间、假设、证据）
- 3 种边强度（弱、中、强），强关联带动画
- 交互式操作（点击、拖拽、缩放、小地图）
- 详情侧边栏展示节点完整信息

### ✨ 界面特点
- 🎨 现代化渐变背景设计（紫-粉-青）
- 🌓 深色主题界面，护眼舒适
- 📱 响应式布局，适配多种屏幕
- 💫 流畅的动画效果（心跳、脉冲、发光）
- 🎯 直观的用户体验
- 🌊 流式进度反馈，实时展示"思考中"

## API 文档

### 1. 基础因果分析

**POST** `/api/v1/analyze`

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "query": "全球变暖会导致什么后果？",
    "context": "可选的背景信息",
    "max_depth": 3
  }'
```

### 2. 新闻因果提取

**POST** `/api/v1/extract-causality`

```bash
curl -X POST http://localhost:8000/api/v1/extract-causality \
  -H "Content-Type: application/json" \
  -d '{
    "news_text": "美联储宣布加息50个基点，导致美股大幅下跌。",
    "generate_summary": true
  }'
```

### 3. 标的研究（流式）

**POST** `/api/v1/research-target/stream`

```bash
curl -N -X POST http://localhost:8000/api/v1/research-target/stream \
  -H "Content-Type: application/json" \
  -d '{
    "target": "中证1000指数"
  }'
```

### 4. 标的研究（非流式）

**POST** `/api/v1/research-target`

```bash
curl -X POST http://localhost:8000/api/v1/research-target \
  -H "Content-Type: application/json" \
  -d '{
    "target": "比特币"
  }'
```

### 响应格式

所有接口返回标准的 `AnalysisResult` 格式：

```json
{
  "nodes": [
    {
      "id": "n1",
      "label": "节点标签",
      "type": "cause|effect|intermediate|hypothesis|evidence",
      "description": "详细描述",
      "confidence": 0.9
    }
  ],
  "edges": [
    {
      "source": "n1",
      "target": "n2",
      "label": "因果关系",
      "description": "传导机制",
      "strength": 0.85
    }
  ],
  "explanation": "整体因果关系分析",
  "metadata": {
    "target": "标的名称",
    "factors": ["因子1", "因子2"],
    "total_time": 24.5
  }
}
```

### 完整 API 文档

启动后端后访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 开发说明

### 前端开发

```bash
cd frontend

# 开发模式
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

### 后端开发

```bash
cd backend

# 开发模式（自动重载）
python main.py

# 或使用 uvicorn 直接运行
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API 文档

后端启动后，访问以下地址查看自动生成的 API 文档：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 配置说明

### DeepSeek/OpenAI 兼容 API 配置

请在 `backend/.env` 中配置自己的 API Key：

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat
```

### 搜索引擎配置（可选）

标的研究功能需要搜索引擎支持，推荐使用免费的 DuckDuckGo：

```bash
# 安装 DuckDuckGo 搜索支持
pip install duckduckgo-search
```

```env
# 在 .env 中配置
SEARCH_ENGINE=duckduckgo
```

**其他选项：**
- **Tavily**: 专为 AI 优化，注册地址 https://tavily.com/
- **Serper**: 基于 Google，注册地址 https://serper.dev/

详细配置说明请查看：`backend/API_CONFIG.md`

### 前端代理配置

前端通过 Vite 代理转发 API 请求，配置在 `frontend/vite.config.js`：

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

## 部署建议

### 前端部署
1. 构建生产版本：`npm run build`
2. 将 `dist` 目录部署到静态服务器（Nginx、Vercel、Netlify 等）

### 后端部署
1. 使用 Gunicorn + Uvicorn workers
2. 配置反向代理（Nginx）
3. 设置环境变量
4. 使用进程管理器（systemd、supervisor）

## 常见问题

### Q: 如何开始使用？
**A**: 运行 `cd backend && setup.bat`（Windows）或 `bash setup.sh`（Linux/Mac），然后 `python main.py` 启动后端，`cd frontend && npm install && npm run dev` 启动前端。

### Q: API Key 已配置好了吗？
**A**: 没有。请在 `backend/.env` 中设置自己的 `OPENAI_API_KEY`，不要把真实密钥提交到仓库。

### Q: 后端启动失败？
**A**: 
1. 检查 Python 版本（需要 3.9+）
2. 确认已安装依赖：`pip install -r requirements.txt`
3. 检查 `.env` 文件是否存在
4. 查看错误日志定位问题

### Q: 前端无法连接后端？
**A**: 
1. 确保后端服务正在运行（http://localhost:8000）
2. 检查 Vite 代理配置
3. 查看浏览器控制台的网络请求

### Q: 标的研究功能不工作？
**A**: 
1. 确认已安装搜索引擎支持：`pip install duckduckgo-search`
2. 检查 `.env` 中的 `SEARCH_ENGINE=duckduckgo`
3. 或配置 Tavily/Serper API Key

### Q: 图谱显示异常？
**A**: 
1. 确保后端返回的数据格式正确
2. 检查节点和边的 ID 是否匹配
3. 查看浏览器控制台的错误信息

### Q: 如何更换 API Key？
**A**: 编辑 `backend/.env` 文件，修改 `OPENAI_API_KEY` 的值。

### Q: 支持哪些大模型？
**A**: 支持所有兼容 OpenAI API 格式的模型，包括：
- DeepSeek (已配置)
- OpenAI GPT-4/GPT-3.5
- Azure OpenAI
- 其他兼容服务

## 📚 详细文档

- **v2 架构文档**: `docs/v2-architecture.md`
- **v2 API 指南**: `docs/v2-api-guide.md`
- **v2 运维手册**: `docs/v2-runbook.md`
- **API 版本对比**: `backend/API_VERSIONS.md` (v1 vs v2 详细对比和迁移指南)
- **项目清理报告**: `CLEANUP_REPORT.md` (2026-05-06 项目结构优化记录)
- **API 配置指南**: `backend/API_CONFIG.md`
- **API 测试文档**: `backend/API_TEST.md`
- **标的研究文档**: `backend/RESEARCH_TARGET_API.md`
- **流式输出文档**: `backend/STREAMING.md`
- **可视化组件文档**: `frontend/VISUALIZATION.md`
- **TypeScript 类型文档**: `frontend/TYPES.md`

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请通过 GitHub Issues 联系。
