"""Unit tests for the Pattern 03 MCP tools (thread inspection via checkpoints)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from unittest.mock import AsyncMock

import pytest
from src.mcp_servers import crypto_intelligence as mcp_module


@dataclass
class _FakeInterrupt:
    value: dict[str, Any]


@dataclass
class _FakeTask:
    id: str = "task-1"
    name: str = "project_selector"
    interrupts: list[_FakeInterrupt] = field(default_factory=list)


@dataclass
class _FakeStateSnapshot:
    values: dict[str, Any]
    next: tuple[str, ...]
    config: dict[str, Any] = field(default_factory=lambda: {"configurable": {"checkpoint_id": "cp-1"}})
    tasks: tuple[_FakeTask, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


class _FakeGraph:
    def __init__(self, snapshots: dict[str, _FakeStateSnapshot | None] | None = None) -> None:
        self._snapshots = snapshots or {}

    async def aget_state(self, config: dict[str, Any]) -> _FakeStateSnapshot | None:
        tid = config.get("configurable", {}).get("thread_id", "")
        return self._snapshots.get(tid)


class _FakeCheckpointer:
    def __init__(self) -> None:
        self.deleted: list[str] = []

    async def adelete_thread(self, thread_id: str) -> None:
        self.deleted.append(thread_id)


@dataclass
class _FakeRuntime:
    graph: _FakeGraph
    checkpointer: _FakeCheckpointer
    pool: Any = None


def _install_runtime(monkeypatch: pytest.MonkeyPatch, runtime: _FakeRuntime) -> None:
    monkeypatch.setattr(mcp_module, "_runtime", runtime)


# ---------------------------------------------------------------------------
# get_research_status
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_status_completed(monkeypatch: pytest.MonkeyPatch) -> None:
    snapshot = _FakeStateSnapshot(
        values={
            "input": "Research Arbitrum",
            "project_name": "Arbitrum",
            "coin_ticker": "ARB",
            "coin_id": "arbitrum",
            "report": "## Executive Summary\nArbitrum is a leading L2.",
        },
        next=(),
    )
    runtime = _FakeRuntime(
        graph=_FakeGraph({"arb-thread": snapshot}),
        checkpointer=_FakeCheckpointer(),
    )
    _install_runtime(monkeypatch, runtime)

    result = await mcp_module.get_research_status("arb-thread")

    assert "COMPLETED" in result
    assert "Arbitrum" in result
    assert "ARB" in result
    assert "Executive Summary" in result


@pytest.mark.asyncio
async def test_get_status_interrupted(monkeypatch: pytest.MonkeyPatch) -> None:
    interrupt_payload = {
        "interrupt_type": "ambiguous_project",
        "message": "Multiple CoinGecko matches found for Mercury.",
        "project_name": "Mercury",
        "coin_ticker": "",
        "matches": [
            {"coin_id": "mercury", "name": "Mercury", "symbol": "MER", "market_cap_rank": 999},
            {"coin_id": "mercury-protocol", "name": "Mercury Protocol", "symbol": "GMT", "market_cap_rank": 650},
        ],
    }
    snapshot = _FakeStateSnapshot(
        values={"input": "Research Mercury", "project_name": "Mercury"},
        next=("project_selector",),
        tasks=(_FakeTask(interrupts=[_FakeInterrupt(value=interrupt_payload)]),),
    )
    runtime = _FakeRuntime(
        graph=_FakeGraph({"merc-thread": snapshot}),
        checkpointer=_FakeCheckpointer(),
    )
    _install_runtime(monkeypatch, runtime)

    result = await mcp_module.get_research_status("merc-thread")

    assert "INTERRUPTED" in result
    assert "Mercury" in result
    assert "mercury-protocol" in result
    assert "selected_coin_id" in result


@pytest.mark.asyncio
async def test_get_status_resumable(monkeypatch: pytest.MonkeyPatch) -> None:
    snapshot = _FakeStateSnapshot(
        values={"input": "Research Solana", "project_name": "Solana"},
        next=("project_profiler",),
    )
    runtime = _FakeRuntime(
        graph=_FakeGraph({"sol-thread": snapshot}),
        checkpointer=_FakeCheckpointer(),
    )
    _install_runtime(monkeypatch, runtime)

    result = await mcp_module.get_research_status("sol-thread")

    assert "RESUMABLE" in result
    assert "project_profiler" in result
    assert "sol-thread" in result


@pytest.mark.asyncio
async def test_get_status_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    runtime = _FakeRuntime(
        graph=_FakeGraph({}),
        checkpointer=_FakeCheckpointer(),
    )
    _install_runtime(monkeypatch, runtime)

    result = await mcp_module.get_research_status("no-such-thread")

    assert "No research found" in result


# ---------------------------------------------------------------------------
# list_research_threads
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_threads_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    pool = AsyncMock()
    pool.connection.return_value.__aenter__ = AsyncMock(side_effect=Exception("no table"))
    runtime = _FakeRuntime(
        graph=_FakeGraph({}),
        checkpointer=_FakeCheckpointer(),
        pool=pool,
    )
    _install_runtime(monkeypatch, runtime)

    result = await mcp_module.list_research_threads()

    assert "No research threads found" in result


@pytest.mark.asyncio
async def test_list_threads_with_data(monkeypatch: pytest.MonkeyPatch) -> None:
    completed = _FakeStateSnapshot(
        values={"input": "Research Arbitrum", "project_name": "Arbitrum"},
        next=(),
    )
    interrupted = _FakeStateSnapshot(
        values={"input": "Research Mercury", "project_name": "Mercury"},
        next=("project_selector",),
        tasks=(_FakeTask(interrupts=[_FakeInterrupt(value={"message": "pick"})]),),
    )
    graph = _FakeGraph({"arb-thread": completed, "merc-thread": interrupted})

    monkeypatch.setattr(
        mcp_module,
        "_list_thread_ids",
        AsyncMock(return_value=["arb-thread", "merc-thread"]),
    )
    runtime = _FakeRuntime(
        graph=graph,
        checkpointer=_FakeCheckpointer(),
    )
    _install_runtime(monkeypatch, runtime)

    result = await mcp_module.list_research_threads()

    assert "2 research thread" in result
    assert "arb-thread" in result
    assert "COMPLETED" in result
    assert "merc-thread" in result
    assert "INTERRUPTED" in result


# ---------------------------------------------------------------------------
# delete_research_thread
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_thread_success(monkeypatch: pytest.MonkeyPatch) -> None:
    snapshot = _FakeStateSnapshot(
        values={"input": "Research Arbitrum"},
        next=(),
    )
    checkpointer = _FakeCheckpointer()
    runtime = _FakeRuntime(
        graph=_FakeGraph({"arb-thread": snapshot}),
        checkpointer=checkpointer,
    )
    _install_runtime(monkeypatch, runtime)

    result = await mcp_module.delete_research_thread("arb-thread")

    assert "deleted" in result.lower()
    assert checkpointer.deleted == ["arb-thread"]


@pytest.mark.asyncio
async def test_delete_thread_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    runtime = _FakeRuntime(
        graph=_FakeGraph({}),
        checkpointer=_FakeCheckpointer(),
    )
    _install_runtime(monkeypatch, runtime)

    result = await mcp_module.delete_research_thread("no-such-thread")

    assert "No research found" in result
