# 本地环境变量配置

在仓库的 `backend` 目录创建私有配置：

```powershell
Copy-Item .env.example .env
```

Linux/macOS 可使用 `cp .env.example .env`。模板中的密钥默认留空。

## 按需启用服务

- `OPENAI_API_KEY`：填写你自己的 DeepSeek/OpenAI 兼容服务密钥；对应设置 `OPENAI_BASE_URL` 和 `OPENAI_MODEL`。
- `TAVILY_API_KEY` 或 `SERPER_API_KEY`：启用对应实时搜索服务。
- `QVERIS_API_KEY`：启用可选外部数据服务。

v2 在 LLM 密钥留空时仍可生成确定性基础图谱。实时数据与模型增强取决于所配置服务，不保证在无配置时可用。

示例（密钥保持为空，真实值只在本机填写）：

```env
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat
TAVILY_API_KEY=
SERPER_API_KEY=
QVERIS_API_KEY=
```

修改后重启后端：

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

运行 `python test_env.py` 可检查配置是否存在，脚本不输出密钥内容。不要把 `.env` 内容复制进日志、Issue 或截图。若此前已公开密钥，按 [SECURITY.md](../SECURITY.md) 处理；删除文档示例不等于撤销凭据。
