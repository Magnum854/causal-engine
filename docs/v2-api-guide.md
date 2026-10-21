# CausalFlow v2 API Guide

Last updated: 2026-05-05

Base URL: `http://localhost:8000/api/v2`

## Create Session

```bash
curl -X POST http://localhost:8000/api/v2/sessions \
  -H "Content-Type: application/json" \
  -d '{"title":"黄金宏观因果分析"}'
```

## Multi-Input Synthesis

Streams Server-Sent Events over a POST request.

```bash
curl -N -X POST http://localhost:8000/api/v2/sessions/{session_id}/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {"type":"event","content":"美联储暂停加息"},
      {"type":"event","content":"日元套息交易平仓"},
      {"type":"event","content":"中国房地产危机加深"},
      {"type":"data","content":"全球黄金 ETF 持仓创新高"}
    ],
    "find_connections": true,
    "discover_targets": true,
    "max_depth": 5
  }'
```

Important event statuses:

- `start`
- `subgraph`
- `connections`
- `data`
- `complete`
- `error`

## Deep Iterative Analysis

```bash
curl -N -X POST http://localhost:8000/api/v2/sessions/{session_id}/analyze-deep \
  -H "Content-Type: application/json" \
  -d '{
    "seed_query": "黄金价格",
    "max_depth": 5,
    "max_nodes": 50
  }'
```

## Expand A Node

```bash
curl -X POST http://localhost:8000/api/v2/sessions/{session_id}/expand \
  -H "Content-Type: application/json" \
  -d '{"node_id":"target-gold","direction":"both"}'
```

`direction` can be `causes`, `effects`, `both`, or `related`.

## Session Utilities

```bash
curl http://localhost:8000/api/v2/sessions/{session_id}
curl http://localhost:8000/api/v2/sessions/{session_id}/graph
curl -X POST http://localhost:8000/api/v2/sessions/{session_id}/undo
```

## Suggestions

```bash
curl -X POST http://localhost:8000/api/v2/suggestions \
  -H "Content-Type: application/json" \
  -d '{"text":"美联储"}'
```

