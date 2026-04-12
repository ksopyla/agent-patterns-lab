"""API tests for Pattern 02 FastAPI endpoints."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

import pytest
from fastapi.testclient import TestClient
from src import app as app_module


@dataclass
class _FakeGraph:
    result: dict[str, Any]
    received_input: dict[str, str] | None = None
    received_config: dict[str, Any] | None = None

    async def ainvoke(
        self,
        payload: dict[str, str],
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.received_input = payload
        self.received_config = config
        return self.result


class _ExplodingGraph:
    async def ainvoke(
        self,
        payload: dict[str, str],
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        raise RuntimeError("LLM provider unreachable")


class _SlowGraph:
    async def ainvoke(
        self,
        payload: dict[str, str],
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        await asyncio.sleep(0.05)
        return {"report": "late"}


def _make_client(monkeypatch: pytest.MonkeyPatch, graph: object) -> TestClient:
    """Create a TestClient with a pre-injected graph on app.state."""
    monkeypatch.setattr(app_module, "build_graph", lambda: graph)
    return TestClient(app_module.app)


def test_health_endpoint_returns_ok() -> None:
    with TestClient(app_module.app) as client:
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
    monkeypatch.setattr(
        app_module,
        "build_pipeline_run_config",
        lambda: {"run_name": "test-run", "tags": ["example:02-mcp-tool-integration"]},
    )

    with _make_client(monkeypatch, fake_graph) as client:
        response = client.post("/run", json={"input": "Research Arbitrum"})

    assert response.status_code == 200
    data = response.json()
    assert data["report"] == "## Executive Summary\nArbitrum report."
    assert data["profile"] == "L2 rollup, $1.23"
    assert data["community"] == "Strong community health."
    assert fake_graph.received_input == {"input": "Research Arbitrum"}
    assert fake_graph.received_config == {
        "run_name": "test-run",
        "tags": ["example:02-mcp-tool-integration"],
    }


def test_run_endpoint_validates_missing_input() -> None:
    with TestClient(app_module.app) as client:
        response = client.post("/run", json={})

    assert response.status_code == 422


def test_run_endpoint_rejects_empty_input() -> None:
    with TestClient(app_module.app) as client:
        response = client.post("/run", json={"input": ""})

    assert response.status_code == 422


def test_run_endpoint_rejects_too_short_input() -> None:
    with TestClient(app_module.app) as client:
        response = client.post("/run", json={"input": "ab"})

    assert response.status_code == 422


def test_run_endpoint_rejects_too_long_input() -> None:
    with TestClient(app_module.app) as client:
        response = client.post("/run", json={"input": "x" * 501})

    assert response.status_code == 422


def test_run_endpoint_returns_502_on_pipeline_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    with _make_client(monkeypatch, _ExplodingGraph()) as client:
        response = client.post("/run", json={"input": "Research Arbitrum"})

    assert response.status_code == 502
    data = response.json()
    assert data["error"] == "pipeline_failed"
    assert "LLM provider unreachable" in data["detail"]


def test_run_endpoint_returns_504_on_pipeline_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(app_module, "PIPELINE_TIMEOUT_SECONDS", 0.01)

    with _make_client(monkeypatch, _SlowGraph()) as client:
        response = client.post("/run", json={"input": "Research Arbitrum"})

    assert response.status_code == 504
    data = response.json()
    assert data["error"] == "pipeline_timeout"
    assert "timed out" in data["detail"]
