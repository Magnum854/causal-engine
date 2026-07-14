# Claude Handoff Notes

This file mirrors the project-level instructions in `AGENTS.md` for Claude Code. Keep these two files synchronized when project facts, routes, environment variables, or run commands change.

## Current Project

This is a React 18 + FastAPI macroeconomic causal analysis app. The current active product surface is CausalFlow v2.

## Project Structure

Backend:

- v2 router: `backend/app/api/v2_router.py` mounted at `/api/v2`.
- v1 router: `backend/app/api/causal_router.py` mounted at `/api/v1`, legacy.
- v2 service: `backend/app/services/v2_analysis_service.py`.
- API version guide: `backend/API_VERSIONS.md`.

Frontend:

- Main app: `frontend/src/App.jsx`.
- Multi-input panel: `frontend/src/components/QueryPanel.jsx`.
- Graph view: `frontend/src/components/CausalGraph.jsx`.
- Node card: `frontend/src/components/CustomNode.jsx`.
- Demo files, when present, belong under `frontend/src/demo/`.

Documentation:

- v2 docs: `docs/v2-architecture.md`, `docs/v2-api-guide.md`, `docs/v2-runbook.md`.
- Roadmaps: `CAUSAL_FLOW_ROADMAP.md` and `PROJECT_ROADMAP.md`.

## Run Commands

Backend:

```powershell
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd frontend
npm.cmd run dev -- --host 0.0.0.0 --port 5173
```

Frontend build:

```powershell
cd frontend
npm.cmd run build
```

## Important Constraints

- Do not commit API keys. Use `backend/.env` with `OPENAI_API_KEY`.
- v2 can run without an LLM key by using deterministic macro fallback graphs. LLM/search keys improve quality when present.
- Generated runtime DB files under `backend/data/` are local state and should not be committed.
- Keep edits scoped; the repository has historical docs and pre-existing dirty files.

## Cross-Platform Shared Knowledge

<!-- super-neat-freak-sync: last=2026-05-07T00:00 direction=codex->claude -->

### Project Facts

- Product priority is CausalFlow v2: a session-based macroeconomic causal analysis workspace for multi-input synthesis, iterative deep expansion, node expansion, and real-time node enrichment.
- Recommended API surface is `/api/v2`; `/api/v1` remains legacy and stateless.
- v2 session state is persisted through SQLite by `backend/app/services/v2_analysis_service.py`; generated files under `backend/data/` are runtime state and should not be committed.
- The graph presentation was redesigned on 2026-05-07 to use layered lanes, cluster filters, and edge modes (`main`, `focus`, `all`) so dense macro graphs remain readable.
- The left input sidebar was fixed on 2026-05-07 with `min-h-0` and internal scrolling so many clues can be entered.

### Conventions

- Keep real API keys out of repository docs and code. Use `backend/.env` and placeholders in committed files.
- Prefer v2 docs for new work: `docs/v2-architecture.md`, `docs/v2-api-guide.md`, and `docs/v2-runbook.md`.
- Keep temporary smoke-test SQLite data out of git.

### References

- Claude memory path inspected for this project: `C:\Users\28203\.claude\projects\X--vibe-coding-6-----\memory`.
- Existing Claude project memories cover product vision, search pipeline fixes, and the 2026-05-06 cleanup.
