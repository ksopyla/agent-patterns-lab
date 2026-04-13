"""API tests for Pattern 03 FastAPI endpoints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest
from fastapi.testclient import TestClient
from src import app as app_module
from src.service import CompletedRun, FailedRun, InterruptedRun


@dataclass
class _FakeGraph:
    pass


@dataclass
class _FakeCheckpointer:
    pass


@dataclass
class _FakeRuntime:
    graph: _FakeGraph
    checkpointer: _FakeCheckpointer
    pool: object | None = None


def _make_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    runtime = _FakeRuntime(graph=_FakeGraph(), checkpointer=_FakeCheckpointer())

    async def fake_create_runtime() -> _FakeRuntime:
        return runtime

    async def fake_close_runtime(runtime_to_close: _FakeRuntime) -> None:
        return None

    monkeypatch.setattr(app_module, "create_runtime", fake_create_runtime)
    monkeypatch.setattr(app_module, "close_runtime", fake_close_runtime)
    return TestClient(app_module.app)


def test_health_endpoint_returns_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    with _make_client(monkeypatch) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_run_endpoint_returns_completed_response(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_run_pipeline(runtime: object, *, input_text: str, thread_id: str | None = None) -> CompletedRun:
        return CompletedRun(
            thread_id=thread_id or "thread-1",
            result={
                "report": "## Executive Summary\nArbitrum report.",
                "plan": "1. News\n2. Profile",
                "news": "Orbit chains launched.",
                "profile": "L2 rollup, $1.23",
                "community": "Strong community health.",
                "project_name": "Arbitrum",
                "coin_ticker": "ARB",
                "coin_id": "arbitrum",
            },
        )

    monkeypatch.setattr(app_module, "run_pipeline", fake_run_pipeline)

    with _make_client(monkeypatch) as client:
        response = client.post("/run", json={"input": "Research Arbitrum", "thread_id": "thread-1"})

    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["thread_id"] == "thread-1"
    assert response.json()["coin_id"] == "arbitrum"


def test_run_endpoint_returns_interrupted_response(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_run_pipeline(runtime: object, *, input_text: str, thread_id: str | None = None) -> InterruptedRun:
        return InterruptedRun(
            thread_id=thread_id or "thread-2",
            payload={
                "interrupt_type": "ambiguous_project",
                "message": "Multiple matches found.",
                "project_name": "Mercury",
                "coin_ticker": "",
                "matches": [
                    {"coin_id": "mercury", "name": "Mercury", "symbol": "MER", "market_cap_rank": 999},
                ],
            },
        )

    monkeypatch.setattr(app_module, "run_pipeline", fake_run_pipeline)

    with _make_client(monkeypatch) as client:
        response = client.post("/run", json={"input": "Research Mercury"})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "interrupted"
    assert data["thread_id"] == "thread-2"
    assert data["matches"][0]["coin_id"] == "mercury"


def test_run_endpoint_returns_error_response(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_run_pipeline(runtime: object, *, input_text: str, thread_id: str | None = None) -> FailedRun:
        return FailedRun(
            thread_id="thread-3",
            error_code="pipeline_failed",
            detail="CoinGecko down",
            http_status=502,
        )

    monkeypatch.setattr(app_module, "run_pipeline", fake_run_pipeline)

    with _make_client(monkeypatch) as client:
        response = client.post("/run", json={"input": "Research Arbitrum"})

    assert response.status_code == 502
    assert response.json()["thread_id"] == "thread-3"
    assert response.json()["error"] == "pipeline_failed"


def test_run_endpoint_validates_input(monkeypatch: pytest.MonkeyPatch) -> None:
    with _make_client(monkeypatch) as client:
        response = client.post("/run", json={"input": "ab"})

    assert response.status_code == 422


def test_resume_endpoint_uses_selected_coin_id(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_resume_pipeline(runtime: object, *, thread_id: str, resume_payload: dict[str, Any]) -> CompletedRun:
        assert thread_id == "thread-4"
        assert resume_payload == {"selected_coin_id": "arbitrum"}
        return CompletedRun(
            thread_id=thread_id,
            result={
                "report": "## Executive Summary\nRecovered report.",
                "plan": "1. News",
                "news": "News",
                "profile": "Profile",
                "community": "Community",
                "project_name": "Arbitrum",
                "coin_ticker": "ARB",
                "coin_id": "arbitrum",
            },
        )

    monkeypatch.setattr(app_module, "resume_pipeline", fake_resume_pipeline)

    with _make_client(monkeypatch) as client:
        response = client.post("/run/resume", json={"thread_id": "thread-4", "selected_coin_id": "arbitrum"})

    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["thread_id"] == "thread-4"


def test_thread_endpoints_are_removed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Thread inspection is exposed via MCP tools, not REST endpoints."""
    with _make_client(monkeypatch) as client:
        assert client.get("/threads").status_code == 404
        assert client.get("/threads/some-id").status_code == 404
        assert client.delete("/threads/some-id").status_code == 404
