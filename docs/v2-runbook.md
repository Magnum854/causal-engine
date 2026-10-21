# CausalFlow v2 Runbook

Last updated: 2026-10-21

## Local startup

Run commands from the repository root unless noted otherwise. Install Python dependencies with `python -m pip install -r backend/requirements.txt` and frontend dependencies with `npm ci --prefix frontend`.

Backend (from `backend`):

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Frontend (in a second terminal, from `frontend`):

```powershell
npm.cmd run dev
```

Open `http://localhost:5173`. The Vite development proxy forwards `/api` to `http://localhost:8000`. The app defaults to the `/api/v2` API path.

## Same-origin Docker deployment

The root `Dockerfile` builds the frontend and serves it from FastAPI. Compose runs one `causalflow` service; no separate frontend container, Nginx container, domain edit, or `frontend/Dockerfile` is required.

```powershell
docker compose config
docker compose up -d --build
docker compose ps
docker compose logs --tail=100 causalflow
```

Open `http://localhost:8000`; API docs are at `/docs` and the health endpoint is `/health`. Without credentials, v2 can create rule-based fallback graphs. Live enrichment needs the matching provider configuration.

## Optional provider configuration

Copy `backend/.env.example` to `backend/.env`, fill only the providers you use, and then pass that file explicitly:

```powershell
Copy-Item backend/.env.example backend/.env
docker compose --env-file backend/.env up -d --build
```

For local non-Docker startup, the backend loads `backend/.env` directly. Leave keys blank for the no-LLM fallback. Never paste the resolved output of `docker compose --env-file backend/.env config` into public logs because it can contain secrets.

`VITE_API_BASE_URL`, when set for a separate frontend host, must be the full v2 API prefix, for example `https://api.example.com/api/v2`. It is a frontend build-time setting. The root Docker deployment normally uses `/api/v2` and needs no override.

## Runtime state and updates

- Local startup stores SQLite sessions under `backend/data/` by default.
- Compose sets `CAUSAL_V2_DB=/app/data/causal_v2.sqlite3` and persists `/app/data` in the `causalflow-data` named volume.
- `docker compose down` stops/removes containers while preserving the volume. The `-v` option deletes its stored session data and should only be used intentionally.
- To update, run `docker compose up -d --build` again, adding `--env-file backend/.env` when applicable.
- Runtime databases and private `.env` files are excluded from Git and Docker build contexts.

## Verification

From the repository root:

```powershell
python -m unittest discover -s backend/tests -p "test_v2_offline.py"
npm.cmd run build --prefix frontend
```

The regression checks use empty credentials, a temporary SQLite file, offline node enrichment, and no external provider calls. They cover session creation, synthesis SSE, node expansion, undo, persistence and missing-session responses. They do not verify paid provider credentials, real-time data or a public deployment.

UI checks: enter several clues, generate a graph, inspect backbone/focus edge modes, filter clusters, expand a node and undo. A successful image build or `/health` response alone does not prove all interactive UI flows.
