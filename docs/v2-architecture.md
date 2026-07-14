# CausalFlow v2 Architecture

Last updated: 2026-05-05

## Purpose

CausalFlow v2 upgrades the app from a single-query shallow causal graph into a session-based macroeconomic causal analysis workspace. It supports multi-input synthesis, iterative deep expansion, node-level expansion, streaming progress, and a clearer large-graph presentation.

## Backend Flow

Main v2 modules:

- `backend/app/api/v2_router.py`: REST and SSE API surface under `/api/v2`.
- `backend/app/services/v2_analysis_service.py`: session store, deterministic macro fallback graph builder, multi-input synthesis, deep expansion, node expansion, and node data enrichment.
- `backend/app/services/node_sensing_service.py`: search-based node enrichment with timeout, retry, cache, and source quality scoring.
- `backend/app/services/structured_api_service.py`: structured data access, including a yfinance path for liquid market tickers.

Session state is stored in SQLite through `V2SessionStore`. The default database path is `backend/data/causal_v2.sqlite3`, or `CAUSAL_V2_DB` when set.

## v2 Data Model

Graph nodes use these important fields:

- `id`: stable node id.
- `label`: display label.
- `type`: macro/market node type.
- `causal_role`: `cause`, `intermediate`, `effect`, or `target`.
- `domain`: broad domain such as `monetary_policy`, `currency`, `liquidity`, `geopolitics`, `market`, or `structure`.
- `cluster`: user-facing group label.
- `layer`: causal layer used by the frontend layout.
- `confidence`: 0 to 1 score.
- `search_query`: query used for real-time enrichment.
- `realtime_state`: optional latest value, trend, sources, and update time.

Graph edges use:

- `id`, `source`, `target`
- `label`
- `strength`
- `confidence`

## Frontend Presentation

The v2 graph no longer renders every node and every edge as one dense free-form graph. `CausalGraph.jsx` uses a layered lane layout:

- each causal layer becomes a fixed column;
- nodes are grouped by cluster inside each layer;
- node cards have fixed dimensions to prevent overlap;
- default edge mode shows only the main backbone;
- selecting a node switches to focused one-hop edges;
- an "all edges" mode remains available for debugging dense graphs.

This is intentionally optimized for 50+ node macro graphs where readability matters more than showing every relation at once.

