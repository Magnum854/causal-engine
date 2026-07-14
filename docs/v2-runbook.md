# CausalFlow v2 Runbook

Last updated: 2026-05-05

## Local Startup

Backend:

```powershell
cd "X:\vibe coding\6 因果引擎\backend"
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd "X:\vibe coding\6 因果引擎\frontend"
npm.cmd run dev -- --host 0.0.0.0 --port 5173
```

Open `http://localhost:5173`.

## Environment Variables

Set these in `backend/.env` when real LLM/search enrichment is needed. See `backend/.env.example` for a template.

```env
OPENAI_API_KEY=your_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
TAVILY_API_KEY=optional
SERPER_API_KEY=optional
CAUSAL_V2_DB=optional/path/to/causal_v2.sqlite3
```

The v2 service can still create deterministic fallback graphs without `OPENAI_API_KEY`.

## Verification

Backend import check:

```powershell
cd "X:\vibe coding\6 因果引擎"
python -m py_compile backend\main.py backend\app\api\v2_router.py backend\app\services\v2_analysis_service.py
```

Frontend build:

```powershell
cd "X:\vibe coding\6 因果引擎\frontend"
npm.cmd run build
```

In the Codex sandbox, `npm.cmd run build` may fail with `spawn EPERM` unless escalation is allowed, because Vite/esbuild starts a child process.

## Runtime State

- SQLite sessions are stored under `backend/data/` by default.
- Treat `backend/data/` as local runtime state.
- Do not commit generated SQLite files.

## Common UI Checks

- Add many input clues in the left sidebar and verify the input panel scrolls.
- Generate a multi-input graph and verify default graph mode shows a readable backbone rather than every edge.
- Click a node and verify focused one-hop edges appear.
- Use cluster filter buttons to isolate one macro domain.

