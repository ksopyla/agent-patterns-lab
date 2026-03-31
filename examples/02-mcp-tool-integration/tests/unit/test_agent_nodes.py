"""Unit tests for all 5 agent nodes in Pattern 02."""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import AsyncMock

import pytest
from src.agents import (
    community_analyst,
    intelligence_compiler,
    news_scanner,
    project_profiler,
    research_planner,
)


@dataclass
class _DummyResponse:
    content: str


class _DummyTextModel:
    def __init__(self, response_text: str) -> None:
        self._response_text = response_text
        self.calls: list[list[object]] = []

    async def ainvoke(self, messages: list[object]) -> _DummyResponse:
        self.calls.append(messages)
        return _DummyResponse(content=self._response_text)


class _DummyStructuredModel:
    def __init__(self, response: research_planner.ResearchPlan) -> None:
        self._response = response
        self.calls: list[list[object]] = []

    async def ainvoke(self, messages: list[object]) -> research_planner.ResearchPlan:
        self.calls.append(messages)
        return self._response


class _DummyPlannerModel:
    def __init__(self, response: research_planner.ResearchPlan) -> None:
        self.schemas: list[type[research_planner.ResearchPlan]] = []
        self.structured_model = _DummyStructuredModel(response)

    def with_structured_output(
        self,
        schema: type[research_planner.ResearchPlan],
    ) -> _DummyStructuredModel:
        self.schemas.append(schema)
        return self.structured_model


# --- Research Planner ---


@pytest.mark.asyncio
async def test_research_planner_returns_structured_output(monkeypatch: pytest.MonkeyPatch) -> None:
    planner_output = research_planner.ResearchPlan(
        project_name="Arbitrum",
        coin_ticker="arb",
        plan="1. Recent news\n2. Project fundamentals\n3. Community activity",
        news_queries=["Arbitrum latest news 2026", "Arbitrum partnership announcement"],
        community_queries=["Arbitrum site:reddit.com", "Arbitrum twitter sentiment"],
    )
    model = _DummyPlannerModel(planner_output)
    monkeypatch.setattr(research_planner, "get_chat_model", lambda: model)

    result = await research_planner.research_planner_node({"input": "Research Arbitrum"})

    assert result["plan"] == planner_output.plan
    assert result["project_name"] == "Arbitrum"
    assert result["coin_ticker"] == "ARB"
    assert result["news_queries"] == planner_output.news_queries
    assert result["community_queries"] == planner_output.community_queries
    assert model.schemas == [research_planner.ResearchPlan]
    assert len(model.structured_model.calls) == 1


@pytest.mark.asyncio
async def test_research_planner_falls_back_on_blank_project_name(monkeypatch: pytest.MonkeyPatch) -> None:
    planner_output = research_planner.ResearchPlan(
        project_name=" ",
        coin_ticker="",
        plan="1. News\n2. Profile\n3. Community",
        news_queries=["Arbitrum latest news"],
        community_queries=["Arbitrum reddit"],
    )
    model = _DummyPlannerModel(planner_output)
    monkeypatch.setattr(research_planner, "get_chat_model", lambda: model)

    result = await research_planner.research_planner_node({"input": "Research Arbitrum"})

    assert result["project_name"] == "Research Arbitrum"
    assert result["coin_ticker"] == ""


# --- News Scanner ---


@pytest.mark.asyncio
async def test_news_scanner_uses_planner_queries(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _DummyTextModel("Arbitrum announced Orbit chains. TVL exceeded $10B.")
    monkeypatch.setattr(news_scanner, "get_chat_model", lambda: model)
    run_search_queries = AsyncMock(
        return_value=[
            {"title": "Arbitrum news", "snippet": "Orbit chains launched", "link": "https://example.com/1"},
        ]
    )
    monkeypatch.setattr(news_scanner, "run_search_queries", run_search_queries)

    result = await news_scanner.news_scanner_node(
        {
            "input": "Research Arbitrum",
            "project_name": "Arbitrum",
            "coin_ticker": "ARB",
            "news_queries": ["Arbitrum latest news 2026"],
        }
    )

    assert "Orbit chains" in result["news"]
    run_search_queries.assert_awaited_once_with(["Arbitrum latest news 2026"], "NewsScanner")
    assert len(model.calls) == 1


@pytest.mark.asyncio
async def test_news_scanner_degrades_on_empty_search_results(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _DummyTextModel("Unable to find recent news due to search unavailability.")
    monkeypatch.setattr(news_scanner, "get_chat_model", lambda: model)
    run_search_queries = AsyncMock(return_value=[])
    monkeypatch.setattr(news_scanner, "run_search_queries", run_search_queries)

    result = await news_scanner.news_scanner_node(
        {
            "input": "Research Arbitrum",
            "project_name": "Arbitrum",
            "coin_ticker": "ARB",
            "news_queries": [],
        }
    )

    assert "news" in result
    assert len(model.calls) == 1


# --- Project Profiler ---


@pytest.mark.asyncio
async def test_project_profiler_uses_project_name(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _DummyTextModel("Arbitrum is an L2 optimistic rollup. Price: $1.23, Market cap: $4.5B")
    monkeypatch.setattr(project_profiler, "get_chat_model", lambda: model)

    monkeypatch.setattr(
        project_profiler,
        "search_coins",
        AsyncMock(return_value='[{"id": "arbitrum", "name": "Arbitrum", "symbol": "ARB"}]'),
    )
    monkeypatch.setattr(
        project_profiler,
        "get_coin_info",
        AsyncMock(return_value='{"name": "Arbitrum", "description": "L2 rollup", "developer_data": {"stars": 8000}}'),
    )
    monkeypatch.setattr(
        project_profiler,
        "get_coin_price",
        AsyncMock(return_value='{"price": 1.23, "market_cap": 4500000000}'),
    )

    result = await project_profiler.project_profiler_node(
        {
            "input": "Research Arbitrum",
            "project_name": "Arbitrum",
            "coin_ticker": "ARB",
        }
    )

    assert "L2 optimistic rollup" in result["profile"]
    project_profiler.search_coins.assert_called_once_with("Arbitrum")


@pytest.mark.asyncio
async def test_project_profiler_degrades_on_api_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _DummyTextModel("Limited profile available due to data source issues.")
    monkeypatch.setattr(project_profiler, "get_chat_model", lambda: model)

    monkeypatch.setattr(
        project_profiler,
        "search_coins",
        AsyncMock(side_effect=RuntimeError("CoinGecko down")),
    )
    monkeypatch.setattr(
        project_profiler,
        "get_coin_info",
        AsyncMock(side_effect=RuntimeError("CoinGecko down")),
    )
    monkeypatch.setattr(
        project_profiler,
        "get_coin_price",
        AsyncMock(side_effect=RuntimeError("CoinGecko down")),
    )

    result = await project_profiler.project_profiler_node(
        {
            "input": "Research Arbitrum",
            "project_name": "Arbitrum",
            "coin_ticker": "ARB",
        }
    )

    assert "profile" in result
    assert len(model.calls) == 1


# --- Community Analyst ---


@pytest.mark.asyncio
async def test_community_analyst_uses_social_search(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _DummyTextModel("Community Health: Strong. Active Reddit discussions and positive Twitter sentiment.")
    monkeypatch.setattr(community_analyst, "get_chat_model", lambda: model)
    run_search_queries = AsyncMock(
        return_value=[
            {"title": "Arbitrum Reddit", "snippet": "Great community", "link": "https://reddit.com/r/arbitrum/1"},
        ]
    )
    monkeypatch.setattr(community_analyst, "run_search_queries", run_search_queries)

    result = await community_analyst.community_analyst_node(
        {
            "input": "Research Arbitrum",
            "project_name": "Arbitrum",
            "coin_ticker": "ARB",
            "community_queries": ["Arbitrum site:reddit.com"],
        }
    )

    assert "Strong" in result["community"]
    run_search_queries.assert_awaited_once_with(["Arbitrum site:reddit.com"], "CommunityAnalyst")
    assert len(model.calls) == 1


@pytest.mark.asyncio
async def test_community_analyst_degrades_on_empty_search_results(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _DummyTextModel("Community analysis unavailable due to search issues.")
    monkeypatch.setattr(community_analyst, "get_chat_model", lambda: model)
    run_search_queries = AsyncMock(return_value=[])
    monkeypatch.setattr(community_analyst, "run_search_queries", run_search_queries)

    result = await community_analyst.community_analyst_node(
        {
            "input": "Research Arbitrum",
            "project_name": "Arbitrum",
            "coin_ticker": "ARB",
            "community_queries": [],
        }
    )

    assert "community" in result
    assert len(model.calls) == 1


# --- Intelligence Compiler ---


@pytest.mark.asyncio
async def test_intelligence_compiler_produces_report(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _DummyTextModel("## Executive Summary\nArbitrum is a leading L2 scaling solution.")
    monkeypatch.setattr(intelligence_compiler, "get_chat_model", lambda: model)

    state = {
        "input": "Research Arbitrum",
        "project_name": "Arbitrum",
        "coin_ticker": "ARB",
        "plan": "1. News\n2. Profile\n3. Community",
        "news": "Orbit chains launched",
        "profile": "L2 rollup, $1.23, $4.5B mcap",
        "community": "Strong community health",
    }
    result = await intelligence_compiler.intelligence_compiler_node(state)

    assert "Executive Summary" in result["report"]
    assert "L2 scaling solution" in result["report"]
