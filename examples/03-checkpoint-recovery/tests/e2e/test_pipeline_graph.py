"""End-to-end tests for the Pattern 03 checkpointed graph."""

from __future__ import annotations

import pytest
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt
from src.agents import graph as graph_module


@pytest.mark.asyncio
async def test_graph_resumes_only_failed_branch_after_checkpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    call_counts = {
        "research_planner": 0,
        "project_verifier": 0,
        "project_selector": 0,
        "news_scanner": 0,
        "project_profiler": 0,
        "community_analyst": 0,
        "intelligence_compiler": 0,
    }

    async def fake_research_planner(state: dict[str, str]) -> dict[str, str | list[str]]:
        call_counts["research_planner"] += 1
        return {
            "plan": "1. News\n2. Profile\n3. Community",
            "project_name": "Arbitrum",
            "coin_ticker": "ARB",
            "news_queries": ["Arbitrum news"],
            "community_queries": ["Arbitrum reddit"],
        }

    async def fake_project_verifier(state: dict[str, str]) -> dict[str, str | list[str]]:
        call_counts["project_verifier"] += 1
        return {
            "coin_id": "arbitrum",
            "ambiguous_matches": [],
        }

    async def fake_project_selector(state: dict[str, str]) -> dict[str, str | list[str]]:
        call_counts["project_selector"] += 1
        return {}

    async def fake_news_scanner(state: dict[str, str]) -> dict[str, str]:
        call_counts["news_scanner"] += 1
        return {"news": "Orbit chains launched. TVL over $10B."}

    async def fake_project_profiler(state: dict[str, str]) -> dict[str, str]:
        call_counts["project_profiler"] += 1
        if call_counts["project_profiler"] == 1:
            raise RuntimeError("CoinGecko temporarily unavailable")
        return {"profile": "L2 optimistic rollup. Price $1.23, Market cap $4.5B."}

    async def fake_community_analyst(state: dict[str, str]) -> dict[str, str]:
        call_counts["community_analyst"] += 1
        return {"community": "Strong: active Reddit, positive Twitter sentiment."}

    async def fake_intelligence_compiler(state: dict[str, str]) -> dict[str, str]:
        call_counts["intelligence_compiler"] += 1
        assert state["news"] is not None
        assert state["profile"] is not None
        assert state["community"] is not None
        return {"report": "## Executive Summary\nArbitrum comprehensive intelligence report."}

    monkeypatch.setattr(graph_module, "research_planner_node", fake_research_planner)
    monkeypatch.setattr(graph_module, "project_verifier_node", fake_project_verifier)
    monkeypatch.setattr(graph_module, "project_selector_node", fake_project_selector)
    monkeypatch.setattr(graph_module, "news_scanner_node", fake_news_scanner)
    monkeypatch.setattr(graph_module, "project_profiler_node", fake_project_profiler)
    monkeypatch.setattr(graph_module, "community_analyst_node", fake_community_analyst)
    monkeypatch.setattr(graph_module, "intelligence_compiler_node", fake_intelligence_compiler)

    graph = graph_module.build_graph(checkpointer=MemorySaver())
    config = {"configurable": {"thread_id": "recovery-thread"}}

    with pytest.raises(RuntimeError, match="CoinGecko temporarily unavailable"):
        await graph.ainvoke({"input": "Research Arbitrum"}, config=config)

    result = await graph.ainvoke(None, config=config)

    assert call_counts == {
        "research_planner": 1,
        "project_verifier": 1,
        "project_selector": 1,
        "news_scanner": 1,
        "project_profiler": 2,
        "community_analyst": 1,
        "intelligence_compiler": 1,
    }
    assert "Executive Summary" in result["report"]
    assert result["coin_id"] == "arbitrum"


@pytest.mark.asyncio
async def test_graph_interrupts_and_resumes_with_same_thread(monkeypatch: pytest.MonkeyPatch) -> None:
    call_counts = {
        "research_planner": 0,
        "project_verifier": 0,
        "project_selector": 0,
    }

    async def planning_node(state: dict[str, str]) -> dict[str, str | list[str]]:
        call_counts["research_planner"] += 1
        return {
            "plan": "1. News\n2. Profile\n3. Community",
            "project_name": "Mercury",
            "coin_ticker": "",
            "news_queries": ["Mercury crypto news"],
            "community_queries": ["Mercury crypto reddit"],
        }

    async def verifying_node(state: dict[str, str]) -> dict[str, str | list[str]]:
        call_counts["project_verifier"] += 1
        return {
            "coin_id": "",
            "ambiguous_matches": [
                {"coin_id": "mercury", "name": "Mercury", "symbol": "MER", "market_cap_rank": 999},
                {
                    "coin_id": "mercury-protocol",
                    "name": "Mercury Protocol",
                    "symbol": "GMT",
                    "market_cap_rank": 650,
                },
            ],
        }

    async def selecting_node(state: dict[str, str]) -> dict[str, str | list[str]]:
        call_counts["project_selector"] += 1
        selected = interrupt(
            {
                "interrupt_type": "ambiguous_project",
                "message": "Multiple CoinGecko matches found.",
                "project_name": state["project_name"],
                "coin_ticker": state["coin_ticker"],
                "matches": state["ambiguous_matches"],
            }
        )
        selected_coin_id = str(selected["selected_coin_id"])
        return {
            "coin_id": selected_coin_id,
            "ambiguous_matches": [],
        }

    async def fake_news_scanner(state: dict[str, str]) -> dict[str, str]:
        return {"news": "Mercury news"}

    async def fake_project_profiler(state: dict[str, str]) -> dict[str, str]:
        return {"profile": f"Profile for {state['coin_id']}"}

    async def fake_community_analyst(state: dict[str, str]) -> dict[str, str]:
        return {"community": "Community sentiment"}

    async def fake_intelligence_compiler(state: dict[str, str]) -> dict[str, str]:
        return {"report": f"Report for {state['coin_id']}"}

    monkeypatch.setattr(graph_module, "research_planner_node", planning_node)
    monkeypatch.setattr(graph_module, "project_verifier_node", verifying_node)
    monkeypatch.setattr(graph_module, "project_selector_node", selecting_node)
    monkeypatch.setattr(graph_module, "news_scanner_node", fake_news_scanner)
    monkeypatch.setattr(graph_module, "project_profiler_node", fake_project_profiler)
    monkeypatch.setattr(graph_module, "community_analyst_node", fake_community_analyst)
    monkeypatch.setattr(graph_module, "intelligence_compiler_node", fake_intelligence_compiler)

    graph = graph_module.build_graph(checkpointer=MemorySaver())
    config = {"configurable": {"thread_id": "interrupt-thread"}}

    first = await graph.ainvoke({"input": "Research Mercury"}, config=config)
    assert "__interrupt__" in first

    resumed = await graph.ainvoke(Command(resume={"selected_coin_id": "mercury-protocol"}), config=config)
    assert call_counts == {
        "research_planner": 1,
        "project_verifier": 1,
        "project_selector": 2,
    }
    assert resumed["coin_id"] == "mercury-protocol"
    assert resumed["report"] == "Report for mercury-protocol"
