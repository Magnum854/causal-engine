"""Regression checks for v2 session workflows without credentials or network calls."""

import importlib
import ipaddress
from contextlib import ExitStack
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import unittest
from unittest.mock import patch

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))


class V2OfflineWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="causalflow-offline-")
        self.addCleanup(self.temp.cleanup)
        self.patches = ExitStack()
        self.addCleanup(self.patches.close)
        self.db_path = str(Path(self.temp.name) / "sessions.sqlite3")
        self.patches.enter_context(patch.dict(os.environ, {
            "OPENAI_API_KEY": "",
            "OPENAI_BASE_URL": "https://example.invalid/v1",
            "TAVILY_API_KEY": "",
            "SERPER_API_KEY": "",
            "QVERIS_API_KEY": "",
            "CAUSAL_V2_DB": self.db_path,
        }))
        self.patches.enter_context(patch("dotenv.load_dotenv", return_value=False))
        self.network_attempts = []

        original_connect = socket.socket.connect
        original_connect_ex = socket.socket.connect_ex

        def is_loopback(address):
            try:
                return ipaddress.ip_address(address[0]).is_loopback
            except (ValueError, TypeError, IndexError):
                return False

        def reject_network(sock, address):
            # Windows implements asyncio's internal socketpair using localhost.
            if is_loopback(address):
                return original_connect(sock, address)
            self.network_attempts.append(True)
            raise AssertionError("Offline test attempted a network connection")

        def reject_network_ex(sock, address):
            if is_loopback(address):
                return original_connect_ex(sock, address)
            self.network_attempts.append(True)
            raise AssertionError("Offline test attempted a network connection")

        self.patches.enter_context(patch.object(socket.socket, "connect", reject_network))
        self.patches.enter_context(patch.object(socket.socket, "connect_ex", reject_network_ex))

        main = importlib.import_module("main")
        self.router = importlib.import_module("app.api.v2_router")
        module = importlib.import_module("app.services.v2_analysis_service")
        self.store_class = module.V2SessionStore
        self.service = module.V2AnalysisService()
        self.assertFalse(self.service.use_llm)

        async def offline_enrichment(nodes):
            return nodes

        self.service.node_sensing.enrich_nodes_batch = offline_enrichment
        self.router._v2_service = self.service
        from fastapi.testclient import TestClient
        self.client = TestClient(main.app)
        self.addCleanup(self.client.close)
        self.addCleanup(setattr, self.router, "_v2_service", None)

    def tearDown(self):
        self.assertEqual(self.network_attempts, [], "The offline workflow must not contact providers")

    def test_session_synthesis_expansion_undo_and_persistence(self):
        self.assertEqual(self.client.get("/health").json(), {"status": "healthy"})
        response = self.client.post("/api/v2/sessions", json={"title": "Offline regression"})
        self.assertEqual(response.status_code, 200)
        session_id = response.json()["id"]

        response = self.client.post(f"/api/v2/sessions/{session_id}/add-input", json={
            "input": {"type": "event", "content": "美联储暂停加息"},
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["inputs"]), 1)

        response = self.client.post(f"/api/v2/sessions/{session_id}/synthesize", json={
            "inputs": [
                {"type": "event", "content": "美联储暂停加息"},
                {"type": "query", "content": "黄金价格的影响因素"},
            ],
            "max_depth": 2,
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/event-stream", response.headers["content-type"])
        events = [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith("data: ")]
        self.assertEqual(events[-1]["status"], "complete")
        graph = events[-1]["data"]["graph"]
        self.assertGreater(len(graph["nodes"]), 0)
        self.assertGreater(len(graph["edges"]), 0)
        known_ids = {node["id"] for node in graph["nodes"]}
        self.assertTrue(all(edge["source"] in known_ids and edge["target"] in known_ids for edge in graph["edges"]))

        response = self.client.post(f"/api/v2/sessions/{session_id}/expand", json={
            "node_id": graph["nodes"][0]["id"], "direction": "both",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("delta", response.json())
        response = self.client.post(f"/api/v2/sessions/{session_id}/undo")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["graph"], graph)
        restored = self.store_class(self.db_path).require(session_id)
        self.assertEqual(restored["graph"], graph)
        self.assertEqual(restored["status"], "completed")

    def test_missing_session_is_404(self):
        response = self.client.get("/api/v2/sessions/does-not-exist")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
