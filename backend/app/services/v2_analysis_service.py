import asyncio
import json
import logging
import os
import re
import sqlite3
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional
from uuid import uuid4

from openai import AsyncOpenAI

from app.services.node_sensing_service import NodeSensingService

logger = logging.getLogger(__name__)


def _utcnow() -> str:
    return datetime.utcnow().isoformat()


def _slug(value: str) -> str:
    text = re.sub(r"\s+", "-", value.strip().lower())
    text = re.sub(r"[^a-z0-9\u4e00-\u9fff-]+", "", text)
    return text[:48] or uuid4().hex[:8]


class V2SessionStore:
    """Small SQLite-backed session store for v2 graph state and undo history."""

    def __init__(self, db_path: Optional[str] = None):
        base_dir = Path(__file__).resolve().parents[2] / "data"
        base_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = Path(db_path or os.getenv("CAUSAL_V2_DB", base_dir / "causal_v2.sqlite3"))
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )

    def create(self, title: Optional[str] = None) -> Dict[str, Any]:
        session_id = uuid4().hex
        now = _utcnow()
        session = {
            "id": session_id,
            "title": title or "新的宏观因果分析",
            "created_at": now,
            "updated_at": now,
            "inputs": [],
            "graph": {"nodes": [], "edges": [], "explanation": "", "clusters": []},
            "history": [],
            "status": "idle",
        }
        self.save(session)
        return session

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute("SELECT payload FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not row:
            return None
        return json.loads(row["payload"])

    def save(self, session: Dict[str, Any]) -> Dict[str, Any]:
        session["updated_at"] = _utcnow()
        payload = json.dumps(session, ensure_ascii=False)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO sessions (id, title, created_at, updated_at, payload)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    updated_at = excluded.updated_at,
                    payload = excluded.payload
                """,
                (
                    session["id"],
                    session.get("title", "宏观因果分析"),
                    session.get("created_at", _utcnow()),
                    session["updated_at"],
                    payload,
                ),
            )
        return session

    def snapshot(self, session: Dict[str, Any]) -> None:
        history = session.setdefault("history", [])
        history.append(deepcopy(session.get("graph", {})))
        session["history"] = history[-25:]

    def undo(self, session_id: str) -> Dict[str, Any]:
        session = self.require(session_id)
        history = session.get("history", [])
        if not history:
            return session
        session["graph"] = history.pop()
        session["history"] = history
        return self.save(session)

    def require(self, session_id: str) -> Dict[str, Any]:
        session = self.get(session_id)
        if not session:
            raise ValueError(f"session not found: {session_id}")
        return session


class MacroKnowledgeBase:
    """Deterministic fallback graph generator used when LLM credentials are absent."""

    DOMAINS = {
        "monetary_policy": "货币政策",
        "currency": "汇率与美元",
        "liquidity": "全球流动性",
        "geopolitics": "地缘政治",
        "market": "市场与资产",
        "structure": "结构性因素",
    }

    SEEDS = {
        "黄金": [
            ("real_rates", "美国实际利率", "interest_rate", "monetary_policy", "实际利率越高，持有黄金的机会成本越高"),
            ("dxy", "美元指数 DXY", "forex_rate", "currency", "美元走强通常压制以美元计价的黄金"),
            ("central_bank_buying", "央行购金", "market", "liquidity", "官方储备配置为黄金提供中长期需求"),
            ("geopolitical_risk", "地缘风险", "geopolitical_risk", "geopolitics", "风险事件会抬升避险需求"),
            ("etf_flows", "黄金 ETF 持仓", "market", "market", "ETF 资金流反映投资者配置意愿"),
        ],
        "美联储": [
            ("fed_rate", "联邦基金利率", "interest_rate", "monetary_policy", "政策利率决定美元资产收益率锚"),
            ("inflation", "美国通胀", "inflation_rate", "monetary_policy", "通胀决定政策紧缩或宽松压力"),
            ("labor_market", "美国就业市场", "macro_indicator", "structure", "就业强弱影响美联储反应函数"),
        ],
        "日元": [
            ("jpy_carry", "日元套息交易", "market", "liquidity", "套息交易平仓会触发跨资产去杠杆"),
            ("boj_ycc", "日本央行 YCC 政策", "monetary_policy", "monetary_policy", "YCC 调整会改变日债收益率和日元融资成本"),
            ("us_jp_spread", "美日利差", "interest_rate", "currency", "利差驱动美元兑日元和套息收益"),
        ],
        "房地产": [
            ("china_property", "中国房地产信用压力", "macro_indicator", "structure", "地产信用收缩影响中国需求和风险偏好"),
            ("china_growth", "中国增长预期", "macro_indicator", "structure", "增长预期会影响商品和新兴市场资金流"),
            ("policy_support", "中国政策托底", "fiscal_policy", "monetary_policy", "逆周期政策改变增长和信用预期"),
        ],
        "美元": [
            ("dxy", "美元指数 DXY", "forex_rate", "currency", "美元是全球流动性和风险偏好的核心价格"),
            ("treasury_yields", "美国国债收益率", "interest_rate", "monetary_policy", "美债收益率影响全球贴现率"),
            ("dollar_liquidity", "美元流动性", "macro_indicator", "liquidity", "美元融资条件影响全球资产定价"),
        ],
    }

    COMMON_TARGETS = [
        ("gold_price", "黄金价格", "commodity_price", "market", "共同受实际利率、美元、避险需求和央行购金影响"),
        ("us_treasury", "美国国债", "bond", "market", "共同受政策利率、避险资金和全球流动性影响"),
        ("global_risk_assets", "全球风险资产", "stock_index", "market", "受美元流动性、套息交易和增长预期共同驱动"),
    ]

    COMPLEMENTS = [
        ("oil_price", "原油价格", "commodity_price", "market", "能源价格影响通胀和地缘风险定价"),
        ("real_yields", "美国 TIPS 实际收益率", "interest_rate", "monetary_policy", "实际收益率是黄金和成长资产的重要折现变量"),
        ("vix", "VIX 波动率", "market_sentiment", "market", "风险厌恶升温通常推高 VIX"),
        ("cross_border_flows", "跨境资金流", "macro_indicator", "liquidity", "资金流向连接汇率、债券和商品市场"),
    ]

    def initial_graph(self, query: str, max_nodes: int = 12) -> Dict[str, Any]:
        nodes = []
        edges = []
        root_id = f"target-{_slug(query)}"
        nodes.append(
            {
                "id": root_id,
                "label": query.strip(),
                "type": "target",
                "causal_role": "effect",
                "domain": "market",
                "cluster": self.DOMAINS["market"],
                "layer": 0,
                "confidence": 0.86,
                "description": "分析目标或用户输入的核心事件",
                "search_query": f"{query} latest macro impact 2026",
            }
        )
        candidates = self._candidates_for(query)
        for idx, (key, label, node_type, domain, description) in enumerate(candidates[: max_nodes - 1], 1):
            node_id = f"{key}-{idx}"
            nodes.append(
                {
                    "id": node_id,
                    "label": label,
                    "type": node_type,
                    "causal_role": "cause",
                    "domain": domain,
                    "cluster": self.DOMAINS.get(domain, domain),
                    "layer": 1,
                    "confidence": round(0.82 - idx * 0.025, 2),
                    "description": description,
                    "search_query": f"{label} latest current data 2026",
                }
            )
            edges.append(
                {
                    "id": f"{node_id}->{root_id}",
                    "source": node_id,
                    "target": root_id,
                    "label": "影响",
                    "strength": round(0.8 - idx * 0.03, 2),
                    "confidence": round(0.8 - idx * 0.03, 2),
                }
            )
        return {
            "nodes": nodes,
            "edges": edges,
            "explanation": f"围绕「{query}」建立初始宏观因果骨架，覆盖政策、汇率、流动性、地缘与市场资金五类驱动。",
            "clusters": self._clusters(nodes),
        }

    def synthesize_graph(self, inputs: List[Dict[str, str]], max_depth: int = 5) -> Dict[str, Any]:
        nodes = []
        edges = []
        seen_labels = set()
        input_node_ids = []
        for idx, item in enumerate(inputs):
            content = item.get("content", "").strip()
            if not content:
                continue
            node_id = f"input-{idx}-{_slug(content)}"
            input_node_ids.append(node_id)
            node = {
                "id": node_id,
                "label": content,
                "type": item.get("type", "event"),
                "causal_role": "cause",
                "domain": self._domain_for(content),
                "cluster": self.DOMAINS.get(self._domain_for(content), "事件"),
                "layer": 0,
                "confidence": 0.88,
                "description": "用户输入的信息源",
                "search_query": f"{content} latest macro market impact 2026",
            }
            nodes.append(node)
            seen_labels.add(content)

        bridge_candidates = []
        for item in inputs:
            bridge_candidates.extend(self._candidates_for(item.get("content", ""))[:4])

        for idx, (key, label, node_type, domain, description) in enumerate(bridge_candidates):
            if label in seen_labels:
                continue
            seen_labels.add(label)
            node_id = f"bridge-{key}-{idx}"
            nodes.append(
                {
                    "id": node_id,
                    "label": label,
                    "type": node_type,
                    "causal_role": "intermediate",
                    "domain": domain,
                    "cluster": self.DOMAINS.get(domain, domain),
                    "layer": 1 + (idx % max(1, min(max_depth, 3))),
                    "confidence": max(0.42, round(0.78 - idx * 0.025, 2)),
                    "description": description,
                    "search_query": f"{label} latest current data 2026",
                }
            )
            source = input_node_ids[idx % len(input_node_ids)] if input_node_ids else node_id
            edges.append(
                {
                    "id": f"{source}->{node_id}",
                    "source": source,
                    "target": node_id,
                    "label": "关联",
                    "strength": max(0.35, round(0.76 - idx * 0.02, 2)),
                    "confidence": max(0.35, round(0.76 - idx * 0.02, 2)),
                }
            )

        target_ids = []
        for idx, (key, label, node_type, domain, description) in enumerate(self.COMMON_TARGETS):
            node_id = f"target-{key}"
            target_ids.append(node_id)
            nodes.append(
                {
                    "id": node_id,
                    "label": label,
                    "type": node_type,
                    "causal_role": "effect",
                    "domain": domain,
                    "cluster": self.DOMAINS.get(domain, domain),
                    "layer": max(2, min(max_depth, 4)),
                    "confidence": 0.74,
                    "description": description,
                    "search_query": f"{label} latest price yield flows 2026",
                }
            )

        bridge_ids = [node["id"] for node in nodes if node["id"].startswith("bridge-")]
        for idx, target_id in enumerate(target_ids):
            for source_id in bridge_ids[idx:: max(1, len(target_ids))][:4]:
                edges.append(
                    {
                        "id": f"{source_id}->{target_id}",
                        "source": source_id,
                        "target": target_id,
                        "label": "共同驱动",
                        "strength": 0.68,
                        "confidence": 0.68,
                    }
                )

        graph = self.merge_graph({"nodes": [], "edges": []}, {"nodes": nodes, "edges": edges})
        graph["explanation"] = "多输入综合完成：系统先抽取每条输入的局部驱动，再寻找美元流动性、利差、风险偏好和增长预期等桥接节点，最后归纳共同影响的资产目标。"
        graph["clusters"] = self._clusters(graph["nodes"])
        return graph

    def expand(self, graph: Dict[str, Any], node_id: str, direction: str = "both") -> Dict[str, Any]:
        existing = {node["id"] for node in graph.get("nodes", [])}
        node = next((n for n in graph.get("nodes", []) if n.get("id") == node_id), None)
        if not node:
            raise ValueError(f"node not found: {node_id}")

        additions = []
        label = node.get("label", "")
        for idx, item in enumerate(self._candidates_for(label)[:2] + self.COMPLEMENTS[:2]):
            key, item_label, node_type, domain, description = item
            new_id = f"expand-{_slug(label)}-{key}-{idx}"
            if new_id in existing:
                continue
            additions.append(
                {
                    "id": new_id,
                    "label": item_label,
                    "type": node_type,
                    "causal_role": "cause" if direction in ("causes", "both") else "effect",
                    "domain": domain,
                    "cluster": self.DOMAINS.get(domain, domain),
                    "layer": int(node.get("layer", 0)) + 1,
                    "confidence": max(0.32, round(float(node.get("confidence", 0.7)) * 0.82, 2)),
                    "description": description,
                    "search_query": f"{item_label} latest current data 2026",
                }
            )

        edges = []
        for addition in additions:
            if direction == "effects":
                source, target = node_id, addition["id"]
            else:
                source, target = addition["id"], node_id
            edges.append(
                {
                    "id": f"{source}->{target}",
                    "source": source,
                    "target": target,
                    "label": "扩展",
                    "strength": addition["confidence"],
                    "confidence": addition["confidence"],
                }
            )
        return {"nodes": additions, "edges": edges}

    def merge_graph(self, base: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
        nodes_by_label = {self._norm(node.get("label", "")): deepcopy(node) for node in base.get("nodes", [])}
        id_map = {node.get("id"): node.get("id") for node in base.get("nodes", [])}
        for node in patch.get("nodes", []):
            label_key = self._norm(node.get("label", ""))
            if label_key in nodes_by_label:
                existing = nodes_by_label[label_key]
                id_map[node.get("id")] = existing.get("id")
                existing["confidence"] = max(float(existing.get("confidence", 0)), float(node.get("confidence", 0)))
                existing.setdefault("aliases", [])
                if node.get("label") not in existing["aliases"]:
                    existing["aliases"].append(node.get("label"))
            else:
                nodes_by_label[label_key] = deepcopy(node)
                id_map[node.get("id")] = node.get("id")

        edges_by_id = {edge.get("id"): deepcopy(edge) for edge in base.get("edges", [])}
        for edge in patch.get("edges", []):
            source = id_map.get(edge.get("source"), edge.get("source"))
            target = id_map.get(edge.get("target"), edge.get("target"))
            if source == target:
                continue
            edge_id = f"{source}->{target}"
            merged_edge = deepcopy(edge)
            merged_edge["id"] = edge_id
            merged_edge["source"] = source
            merged_edge["target"] = target
            if float(merged_edge.get("confidence", merged_edge.get("strength", 0.5))) < 0.3:
                continue
            edges_by_id[edge_id] = merged_edge

        nodes = list(nodes_by_label.values())
        return {"nodes": nodes, "edges": list(edges_by_id.values()), "clusters": self._clusters(nodes)}

    def _candidates_for(self, text: str) -> List[tuple]:
        text_lower = text.lower()
        results = []
        for keyword, candidates in self.SEEDS.items():
            if keyword in text or keyword.lower() in text_lower:
                results.extend(candidates)
        if not results:
            results = self.SEEDS["黄金"] + self.SEEDS["美元"]
        deduped = []
        seen = set()
        for item in results + self.COMPLEMENTS:
            if item[1] not in seen:
                seen.add(item[1])
                deduped.append(item)
        return deduped

    def _domain_for(self, text: str) -> str:
        if any(k in text for k in ["美联储", "央行", "利率", "YCC", "加息"]):
            return "monetary_policy"
        if any(k in text for k in ["美元", "日元", "DXY", "汇率"]):
            return "currency"
        if any(k in text for k in ["地缘", "战争", "政治"]):
            return "geopolitics"
        if any(k in text for k in ["房地产", "就业", "GDP", "通胀"]):
            return "structure"
        return "market"

    def _clusters(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        counts: Dict[str, int] = {}
        for node in nodes:
            cluster = node.get("cluster") or self.DOMAINS.get(node.get("domain"), "其他")
            counts[cluster] = counts.get(cluster, 0) + 1
        return [{"id": _slug(name), "label": name, "count": count} for name, count in counts.items()]

    def _norm(self, value: str) -> str:
        return re.sub(r"\s+", "", value.lower())


class V2AnalysisService:
    def __init__(self):
        self.store = V2SessionStore()
        self.knowledge = MacroKnowledgeBase()
        self.node_sensing = NodeSensingService()
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY") or "missing-key",
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            timeout=60.0,
        )
        self.use_llm = bool(os.getenv("OPENAI_API_KEY"))

    def create_session(self, title: Optional[str] = None) -> Dict[str, Any]:
        return self.store.create(title)

    def get_session(self, session_id: str) -> Dict[str, Any]:
        return self.store.require(session_id)

    def add_input(self, session_id: str, item: Dict[str, Any]) -> Dict[str, Any]:
        session = self.store.require(session_id)
        session.setdefault("inputs", []).append(item)
        return self.store.save(session)

    def undo(self, session_id: str) -> Dict[str, Any]:
        return self.store.undo(session_id)

    async def suggestions(self, text: str) -> Dict[str, Any]:
        base = [
            "美联储暂停加息",
            "日元套息交易平仓",
            "中国房地产信用压力",
            "全球黄金 ETF 持仓变化",
            "DXY 指数跌破关键点位",
        ]
        filtered = [item for item in base if not text or text in item]
        return {"suggestions": filtered[:5]}

    async def synthesize_stream(
        self,
        session_id: str,
        inputs: List[Dict[str, str]],
        max_depth: int = 5,
        find_connections: bool = True,
        discover_targets: bool = True,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        session = self.store.require(session_id)
        self.store.snapshot(session)
        session["status"] = "running"
        session["inputs"] = inputs
        self.store.save(session)

        yield self._event("start", "已创建多输入综合任务", {"session": self._public_session(session)})
        await asyncio.sleep(0)

        shallow_graphs = []
        for idx, item in enumerate(inputs):
            content = item.get("content", "").strip()
            if not content:
                continue
            graph = self.knowledge.initial_graph(content, max_nodes=7)
            shallow_graphs.append(graph)
            yield self._event(
                "subgraph",
                f"完成第 {idx + 1} 条输入的浅层子图",
                {"input_index": idx, "graph": graph},
            )

        combined = {"nodes": [], "edges": [], "clusters": []}
        for graph in shallow_graphs:
            combined = self.knowledge.merge_graph(combined, graph)

        if find_connections or discover_targets:
            synthesized = await self._synthesize_with_optional_llm(inputs, max_depth)
            combined = self.knowledge.merge_graph(combined, synthesized)
            combined["explanation"] = synthesized.get("explanation", combined.get("explanation", ""))
            combined["clusters"] = self.knowledge._clusters(combined["nodes"])
            yield self._event("connections", "已识别跨输入桥接节点和共同影响目标", {"graph": combined})

        enriched_nodes = await self._enrich_nodes_light(combined["nodes"][: min(len(combined["nodes"]), 18)])
        enriched_by_id = {node["id"]: node for node in enriched_nodes}
        combined["nodes"] = [enriched_by_id.get(node["id"], node) for node in combined["nodes"]]
        yield self._event("data", "已完成首批节点实时数据填充", {"nodes": enriched_nodes})

        session["graph"] = combined
        session["status"] = "completed"
        self.store.save(session)
        yield self._event("complete", "多输入综合分析完成", {"session": self._public_session(session), "graph": combined})

    async def analyze_deep_stream(
        self,
        session_id: str,
        seed_query: str,
        max_depth: int = 5,
        max_nodes: int = 50,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        session = self.store.require(session_id)
        self.store.snapshot(session)
        graph = self.knowledge.initial_graph(seed_query, max_nodes=7)
        yield self._event("layer", "Layer 0 核心节点已生成", {"layer": 0, "graph": graph})

        frontier = [node["id"] for node in graph.get("nodes", []) if node.get("layer") == 1]
        for layer in range(1, max_depth + 1):
            if len(graph["nodes"]) >= max_nodes or not frontier:
                break
            additions = {"nodes": [], "edges": []}
            for node_id in frontier[:4]:
                patch = self.knowledge.expand(graph, node_id, "both")
                additions = self.knowledge.merge_graph(additions, patch)
            graph = self.knowledge.merge_graph(graph, additions)
            graph["nodes"] = graph["nodes"][:max_nodes]
            graph["edges"] = [e for e in graph["edges"] if e.get("source") in {n["id"] for n in graph["nodes"]} and e.get("target") in {n["id"] for n in graph["nodes"]}]
            frontier = [node["id"] for node in additions.get("nodes", [])]
            yield self._event("layer", f"Layer {layer} 扩展完成", {"layer": layer, "delta": additions, "graph": graph})

        graph["explanation"] = f"围绕「{seed_query}」完成迭代式深度扩展，节点置信度随层级递减，低于 0.3 的关系已剪枝。"
        session["graph"] = graph
        session["status"] = "completed"
        self.store.save(session)
        yield self._event("complete", "深度分析完成", {"session": self._public_session(session), "graph": graph})

    async def expand_node(self, session_id: str, node_id: str, direction: str = "both") -> Dict[str, Any]:
        session = self.store.require(session_id)
        self.store.snapshot(session)
        graph = session.get("graph", {"nodes": [], "edges": []})
        patch = self.knowledge.expand(graph, node_id, direction)
        patch["nodes"] = await self._enrich_nodes_light(patch["nodes"])
        session["graph"] = self.knowledge.merge_graph(graph, patch)
        session["graph"]["explanation"] = graph.get("explanation", "")
        self.store.save(session)
        return {"delta": patch, "graph": session["graph"], "session": self._public_session(session)}

    async def refresh_node_data(self, session_id: str, node_id: str) -> Dict[str, Any]:
        session = self.store.require(session_id)
        graph = session.get("graph", {})
        node = next((n for n in graph.get("nodes", []) if n.get("id") == node_id), None)
        if not node:
            raise ValueError(f"node not found: {node_id}")
        enriched = (await self._enrich_nodes_light([node]))[0]
        for idx, current in enumerate(graph.get("nodes", [])):
            if current.get("id") == node_id:
                graph["nodes"][idx] = enriched
        session["graph"] = graph
        self.store.save(session)
        return {"node": enriched, "graph": graph}

    async def _synthesize_with_optional_llm(self, inputs: List[Dict[str, str]], max_depth: int) -> Dict[str, Any]:
        if not self.use_llm:
            return self.knowledge.synthesize_graph(inputs, max_depth=max_depth)

        prompt = {
            "task": "Build a macroeconomic causal graph from multiple inputs.",
            "inputs": inputs,
            "schema": {
                "nodes": "id,label,type,causal_role,domain,cluster,layer,confidence,description,search_query",
                "edges": "id,source,target,label,strength,confidence",
                "explanation": "Chinese summary",
            },
            "constraints": [
                "Return JSON only.",
                "Use Chinese labels.",
                "Find hidden bridges and common affected assets.",
                "Keep nodes <= 35.",
            ],
        }
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior macro strategist and causal graph designer."},
                    {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
                ],
                temperature=0.35,
                response_format={"type": "json_object"},
            )
            graph = json.loads(response.choices[0].message.content)
            if graph.get("nodes") and graph.get("edges"):
                return graph
        except Exception as exc:
            logger.warning("[v2] LLM synthesis failed, using fallback: %s", exc)
        return self.knowledge.synthesize_graph(inputs, max_depth=max_depth)

    async def _enrich_nodes_light(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not nodes:
            return []
        sensing_nodes = []
        for node in nodes:
            sensing_nodes.append(
                {
                    **node,
                    "sensing_config": {"auto_queries": [node.get("search_query") or f"{node.get('label')} latest 2026"]},
                }
            )
        try:
            enriched = await self.node_sensing.enrich_nodes_batch(sensing_nodes)
        except Exception as exc:
            logger.warning("[v2] node sensing failed: %s", exc)
            enriched = sensing_nodes

        result = []
        for node in enriched:
            current_state = node.pop("current_state", None)
            if current_state:
                node["realtime_state"] = {
                    "latest_value": current_state.get("value", "unknown"),
                    "trend": current_state.get("trend", "stable"),
                    "narrative_context": current_state.get("narrative_context", ""),
                    "sources": current_state.get("sources", []),
                    "updated_at": node.get("last_updated") or _utcnow(),
                    "confidence": current_state.get("confidence_score", current_state.get("confidence", "web_search")),
                    "quality_score": current_state.get("confidence_score"),
                }
            else:
                node.setdefault(
                    "realtime_state",
                    {
                        "latest_value": "pending",
                        "trend": "stable",
                        "sources": [],
                        "updated_at": _utcnow(),
                        "confidence": "pending",
                    },
                )
            result.append(node)
        return result

    def _event(self, status: str, message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"status": status, "message": message, "data": data or {}, "timestamp": _utcnow()}

    def _public_session(self, session: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in session.items() if k != "history"}
