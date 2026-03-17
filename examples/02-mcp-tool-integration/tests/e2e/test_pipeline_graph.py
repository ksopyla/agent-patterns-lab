"""End-to-end tests for the full Team 1 intelligence pipeline graph."""

from __future__ import annotations

import pytest
from src.agents import graph as graph_module


@pytest.mark.asyncio
async def test_graph_executes_all_five_nodes(monkeypatch: pytest.MonkeyPatch) -> None:
    call_order: list[str] = []

    async def fake_research_planner(state: dict[str, str]) -> dict[str, str]:
        call_order.append("research_planner")
        assert state["input"] == "Research Arbitrum"
        return {"plan": "1. News\n2. Profile\n3. Community"}

    async def fake_news_scanner(state: dict[str, str]) -> dict[str, str]:
        call_order.append("news_scanner")
        assert state["plan"] == "1. News\n2. Profile\n3. Community"
        return {"news": "Orbit chains launched. TVL over $10B."}

    async def fake_project_profiler(state: dict[str, str]) -> dict[str, str]:
        call_order.append("project_profiler")
        assert "Orbit chains" in state["news"]
        return {"profile": "L2 optimistic rollup. Price $1.23, Market cap $4.5B."}

    async def fake_community_analyst(state: dict[str, str]) -> dict[str, str]:
        call_order.append("community_analyst")
        assert "L2 optimistic rollup" in state["profile"]
        return {"community": "Strong: 500k Twitter, 1200 commits/month."}

    async def fake_intelligence_compiler(state: dict[str, str]) -> dict[str, str]:
        call_order.append("intelligence_compiler")
        assert state["news"] is not None
        assert state["profile"] is not None
        assert state["community"] is not None
        return {"report": "## Executive Summary\nArbitrum comprehensive intelligence report."}

    monkeypatch.setattr(graph_module, "research_planner_node", fake_research_planner)
    monkeypatch.setattr(graph_module, "news_scanner_node", fake_news_scanner)
    monkeypatch.setattr(graph_module, "project_profiler_node", fake_project_profiler)
    monkeypatch.setattr(graph_module, "community_analyst_node", fake_community_analyst)
    monkeypatch.setattr(graph_module, "intelligence_compiler_node", fake_intelligence_compiler)

    graph = graph_module.build_graph()
    result = await graph.ainvoke({"input": "Research Arbitrum"})

    assert call_order == [
        "research_planner",
        "news_scanner",
        "project_profiler",
        "community_analyst",
        "intelligence_compiler",
    ]
    assert "Executive Summary" in result["report"]
    assert result["profile"] == "L2 optimistic rollup. Price $1.23, Market cap $4.5B."
