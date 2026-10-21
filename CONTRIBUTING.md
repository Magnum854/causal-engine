# 参与 CausalFlow 开发

当前主要维护分支是 CausalFlow v2；新功能优先使用 `/api/v2`，v1 保留兼容用途。项目结构和约定见 [AGENTS.md](AGENTS.md)。

## 本地开发

1. 安装 `backend/requirements.txt` 和前端依赖。
2. 将 `backend/.env.example` 复制为 `backend/.env`；密钥按需填写，仅保留在本机。
3. 后端在 `backend` 目录运行 `python -m uvicorn main:app --host 127.0.0.1 --port 8000`。
4. 前端在 `frontend` 目录运行 `npm run dev`。

## 提交前验证

从仓库根目录运行不联网的 v2 回归检查：

```bash
python -m unittest discover -s backend/tests -p "test_v2_offline.py"
```

前端构建：

```bash
cd frontend
npm ci
npm run build
```

PR 应描述具体行为、验证结果和仍未覆盖的外部服务。不要提交 `.env`、本地 SQLite 状态或真实 API 响应中的私人信息。实时服务的验证与离线回归应分别说明。

提交贡献表示你有权提供相应代码，并同意按仓库的 MIT License 发布你的贡献；第三方代码应保留原有来源和许可。
