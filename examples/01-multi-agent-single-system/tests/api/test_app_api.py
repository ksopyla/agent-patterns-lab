"""API tests for FastAPI endpoints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fastapi.testclient import TestClient
from src import app as app_module


@dataclass
class _FakeGraph:
    result: dict[str, Any]
    received_input: dict[str, str] | None = None

    async def ainvoke(self, payload: dict[str, str]) -> dict[str, Any]:
        self.received_input = payload
        return self.result


def test_health_endpoint_returns_ok() -> None:
    with TestClient(app_module.app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_run_endpoint_executes_graph(monkeypatch) -> None:
    fake_graph = _FakeGraph(
        result={
            "output": "Final text",
            "plan": "Plan text",
            "research": "Research text",
        }
    )
    monkeypatch.setattr(app_module, "build_graph", lambda: fake_graph)

    with TestClient(app_module.app) as client:
        response = client.post("/run", json={"input": "Tell me about A2A"})

    assert response.status_code == 200
    assert response.json() == {
        "output": "Final text",
        "plan": "Plan text",
        "research": "Research text",
    }
    assert fake_graph.received_input == {"input": "Tell me about A2A"}


def test_run_endpoint_validates_request() -> None:
    with TestClient(app_module.app) as client:
        response = client.post("/run", json={})

    assert response.status_code == 422
