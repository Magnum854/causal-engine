# CausalFlow v2 部署指南

主线采用前后端同源部署：仓库根 `Dockerfile` 构建 React 前端，再由 FastAPI 提供静态资源与 `/api/v2`。开发启动、持久化与检查命令见 [v2 runbook](docs/v2-runbook.md)。

## Docker Compose

需要 Docker 与 Docker Compose v2。在仓库根目录运行：

```bash
docker compose config
docker compose up -d --build
docker compose ps
```

打开 `http://localhost:8000`，健康检查为 `http://localhost:8000/health`，接口说明为 `http://localhost:8000/docs`。默认没有 LLM 密钥时可使用规则基础图谱。此流程不需要修改前端 API 域名，也不需要独立的前端或 Nginx 容器。

## 按需配置外部服务

将 `backend/.env.example` 复制为 `backend/.env`，在本机填写自己的密钥：

```bash
cp backend/.env.example backend/.env
docker compose --env-file backend/.env up -d --build
```

`OPENAI_API_KEY`/`OPENAI_BASE_URL`/`OPENAI_MODEL` 配置兼容模型服务；Tavily、Serper 和 QVeris 按需配置。密钥默认空，实际值不得进入 Git 或镜像。也可以从进程环境传入这些变量而不使用文件。

如需更换宿主机端口，设置 `CAUSAL_PORT`；容器内部始终使用 8000。Compose 的 `causalflow-data` 卷持久化 `/app/data/causal_v2.sqlite3`。普通 `docker compose down` 保留会话；`down -v` 会删除卷数据。

## 分离部署

开发模式在 `backend` 运行 Uvicorn、在 `frontend` 运行 Vite。生产单镜像以根 Dockerfile 为准。`render.yaml` 和 `backend/Dockerfile` 仍提供仅后端的部署入口；需要单独部署前端，并在构建时将 `VITE_API_BASE_URL` 设置为包含 `/api/v2` 的完整 URL，后端 `CORS_ORIGINS` 设置为该前端来源。

## 更新和检查

```bash
docker compose up -d --build
docker compose logs --tail=100 causalflow
```

使用私有 env 文件时给对应命令增加 `--env-file backend/.env`。不要公开粘贴带真实环境配置的 `docker compose config` 输出。项目离线测试和前端构建命令见 [CONTRIBUTING.md](CONTRIBUTING.md)；容器构建成功、接口健康、实时服务可用和公网交互完成应分别核实。
