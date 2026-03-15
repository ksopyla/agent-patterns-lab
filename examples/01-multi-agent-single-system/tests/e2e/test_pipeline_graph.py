"""End-to-end tests for graph orchestration flow."""

from __future__ import annotations

import pytest
from src.agents import graph as graph_module


@pytest.mark.asyncio
async def test_graph_executes_nodes_in_order(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_planner(state: dict[str, str]) -> dict[str, str]:
        assert state["input"] == "Design resilient multi-agent systems"
        return {"plan": "1. Requirements\n2. Pattern selection"}

    async def fake_researcher(state: dict[str, str]) -> dict[str, str]:
        assert state["plan"] == "1. Requirements\n2. Pattern selection"
        return {"research": "Orchestrator pattern improves coordination"}

    async def fake_writer(state: dict[str, str]) -> dict[str, str]:
        assert state["research"] == "Orchestrator pattern improves coordination"
        return {"output": "Final article"}

    monkeypatch.setattr(graph_module, "planner_node", fake_planner)
    monkeypatch.setattr(graph_module, "researcher_node", fake_researcher)
    monkeypatch.setattr(graph_module, "writer_node", fake_writer)

    graph = graph_module.build_graph()
    result = await graph.ainvoke({"input": "Design resilient multi-agent systems"})

    assert result["plan"] == "1. Requirements\n2. Pattern selection"
    assert result["research"] == "Orchestrator pattern improves coordination"
    assert result["output"] == "Final article"
