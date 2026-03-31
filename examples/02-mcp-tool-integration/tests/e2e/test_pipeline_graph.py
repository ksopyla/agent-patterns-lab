"""End-to-end tests for the full Team 1 intelligence pipeline graph.

The graph architecture is fan-out/fan-in:
  research_planner → [news_scanner | project_profiler | community_analyst] → intelligence_compiler

The three middle nodes run in parallel, so we cannot assert a fixed order for
them -- only that all five execute and the compiler runs last.
"""

from __future__ import annotations

import pytest
from src.agents import graph as graph_module


@pytest.mark.asyncio
async def test_graph_executes_all_five_nodes(monkeypatch: pytest.MonkeyPatch) -> None:
    call_order: list[str] = []

    async def fake_research_planner(state: dict[str, str]) -> dict[str, str | list[str]]:
        call_order.append("research_planner")
        assert state["input"] == "Research Arbitrum"
        return {
            "plan": "1. News\n2. Profile\n3. Community",
            "project_name": "Arbitrum",
            "coin_ticker": "ARB",
            "news_queries": ["Arbitrum news"],
            "community_queries": ["Arbitrum reddit"],
        }

    async def fake_news_scanner(state: dict[str, str]) -> dict[str, str]:
        call_order.append("news_scanner")
        assert state["project_name"] == "Arbitrum"
        assert state["coin_ticker"] == "ARB"
        return {"news": "Orbit chains launched. TVL over $10B."}

    async def fake_project_profiler(state: dict[str, str]) -> dict[str, str]:
        call_order.append("project_profiler")
        assert state["project_name"] == "Arbitrum"
        return {"profile": "L2 optimistic rollup. Price $1.23, Market cap $4.5B."}

    async def fake_community_analyst(state: dict[str, str]) -> dict[str, str]:
        call_order.append("community_analyst")
        assert state["project_name"] == "Arbitrum"
        return {"community": "Strong: active Reddit, positive Twitter sentiment."}

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

    assert call_order[0] == "research_planner"
    assert call_order[-1] == "intelligence_compiler"

    parallel_nodes = set(call_order[1:-1])
    assert parallel_nodes == {"news_scanner", "project_profiler", "community_analyst"}

    assert "Executive Summary" in result["report"]
    assert result["profile"] == "L2 optimistic rollup. Price $1.23, Market cap $4.5B."
    assert result["project_name"] == "Arbitrum"
    assert result["coin_ticker"] == "ARB"
