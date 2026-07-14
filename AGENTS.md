# Agent Handoff Notes

This project is a React 18 + FastAPI macroeconomic causal analysis app. The current active product surface is CausalFlow v2.

## Project Structure

Backend:

- v2 router: `backend/app/api/v2_router.py` mounted at `/api/v2`.
- v1 router: `backend/app/api/causal_router.py` mounted at `/api/v1`, legacy.
- v2 service: `backend/app/services/v2_analysis_service.py`.
- API version guide: `backend/API_VERSIONS.md` explains v1 vs v2.

Frontend:

- Main app: `frontend/src/App.jsx`.
- Production components: `frontend/src/components/`.
- Demo files, when present, belong under `frontend/src/demo/`.

Documentation:

- v2 docs: `docs/v2-architecture.md`, `docs/v2-api-guide.md`, `docs/v2-runbook.md`.
- Roadmaps: `CAUSAL_FLOW_ROADMAP.md` and `PROJECT_ROADMAP.md`.
- Cleanup report: `CLEANUP_REPORT.md` records the 2026-05-06 cleanup when present.

## Current v2 Entry Points

- Backend router: `backend/app/api/v2_router.py`, mounted at `/api/v2` from `backend/main.py`.
- v2 orchestration/session service: `backend/app/services/v2_analysis_service.py`.
- Frontend workspace: `frontend/src/App.jsx`.
- Multi-input form: `frontend/src/components/QueryPanel.jsx`.
- Graph presentation: `frontend/src/components/CausalGraph.jsx` and `frontend/src/components/CustomNode.jsx`.

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

Build verification:

```powershell
cd frontend
npm.cmd run build
```

In the Codex sandbox, Vite/esbuild may require elevated execution because it starts a child process.

## Important Constraints

- Do not reintroduce hard-coded API keys in docs or code. Use `backend/.env` with `OPENAI_API_KEY`.
- The repository was cleaned on 2026-05-06: temporary/debug files were removed, obsolete components were deleted, and demo files were organized to `frontend/src/demo/`. Keep edits scoped to production files.
- v2 is designed to run without an LLM key by using deterministic macro fallback graphs. Search and LLM enrichment improve quality when keys are present.
- Generated runtime DB files under `backend/data/` are local state and should not be committed.
- SearchService duplication in `two_pass_causal_service.py` was fixed; shared search behavior should live in `search_service.py`.
- v1 is legacy/stateless and v2 is recommended/session-based. See `backend/API_VERSIONS.md` when available.

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
