"""API tests for Pattern 02 FastAPI endpoints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from unittest.mock import AsyncMock, patch

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
    with (
        patch.object(app_module, "init_mcp", new_callable=AsyncMock),
        patch.object(app_module, "close_mcp", new_callable=AsyncMock),
        TestClient(app_module.app) as client,
    ):
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_run_endpoint_executes_graph(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_graph = _FakeGraph(
        result={
            "report": "## Executive Summary\nArbitrum report.",
            "plan": "1. News\n2. Profile",
            "news": "Orbit chains launched.",
            "profile": "L2 rollup, $1.23",
            "community": "Strong community health.",
        }
    )
    monkeypatch.setattr(app_module, "build_graph", lambda: fake_graph)

    with (
        patch.object(app_module, "init_mcp", new_callable=AsyncMock),
        patch.object(app_module, "close_mcp", new_callable=AsyncMock),
        TestClient(app_module.app) as client,
    ):
        response = client.post("/run", json={"input": "Research Arbitrum"})

    assert response.status_code == 200
    data = response.json()
    assert data["report"] == "## Executive Summary\nArbitrum report."
    assert data["profile"] == "L2 rollup, $1.23"
    assert data["community"] == "Strong community health."
    assert fake_graph.received_input == {"input": "Research Arbitrum"}


def test_run_endpoint_validates_request() -> None:
    with (
        patch.object(app_module, "init_mcp", new_callable=AsyncMock),
        patch.object(app_module, "close_mcp", new_callable=AsyncMock),
        TestClient(app_module.app) as client,
    ):
        response = client.post("/run", json={})

    assert response.status_code == 422
