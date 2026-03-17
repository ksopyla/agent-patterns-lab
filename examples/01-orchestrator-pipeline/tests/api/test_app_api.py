"""API tests for FastAPI endpoints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest
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


def test_run_endpoint_executes_graph(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_graph = _FakeGraph(
        result={
            "report": "## Executive Summary\nArbitrum analysis.",
            "plan": "1. News\n2. Team",
            "news": "Partnership announced.",
        }
    )
    monkeypatch.setattr(app_module, "build_graph", lambda: fake_graph)

    with TestClient(app_module.app) as client:
        response = client.post("/run", json={"input": "Research Arbitrum"})

    assert response.status_code == 200
    data = response.json()
    assert data["report"] == "## Executive Summary\nArbitrum analysis."
    assert data["plan"] == "1. News\n2. Team"
    assert data["news"] == "Partnership announced."
    assert fake_graph.received_input == {"input": "Research Arbitrum"}


def test_run_endpoint_validates_request() -> None:
    with TestClient(app_module.app) as client:
        response = client.post("/run", json={})

    assert response.status_code == 422
