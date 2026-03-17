"""End-to-end tests for the crypto intelligence pipeline graph."""

from __future__ import annotations

import pytest
from src.agents import graph as graph_module


@pytest.mark.asyncio
async def test_graph_executes_nodes_in_order(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_research_planner(state: dict[str, str]) -> dict[str, str]:
        assert state["input"] == "Research Arbitrum"
        return {"plan": "1. Recent news\n2. Team background"}

    async def fake_news_scanner(state: dict[str, str]) -> dict[str, str]:
        assert state["plan"] == "1. Recent news\n2. Team background"
        return {"news": "Arbitrum announced L3 support. Community is bullish."}

    async def fake_intelligence_compiler(state: dict[str, str]) -> dict[str, str]:
        assert state["news"] == "Arbitrum announced L3 support. Community is bullish."
        return {"report": "## Executive Summary\nArbitrum is expanding its L2 ecosystem."}

    monkeypatch.setattr(graph_module, "research_planner_node", fake_research_planner)
    monkeypatch.setattr(graph_module, "news_scanner_node", fake_news_scanner)
    monkeypatch.setattr(graph_module, "intelligence_compiler_node", fake_intelligence_compiler)

    graph = graph_module.build_graph()
    result = await graph.ainvoke({"input": "Research Arbitrum"})

    assert result["plan"] == "1. Recent news\n2. Team background"
    assert result["news"] == "Arbitrum announced L3 support. Community is bullish."
    assert result["report"] == "## Executive Summary\nArbitrum is expanding its L2 ecosystem."
