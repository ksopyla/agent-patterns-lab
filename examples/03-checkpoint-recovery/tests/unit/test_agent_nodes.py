"""Unit tests for Pattern 03 agent nodes."""

from __future__ import annotations

import json
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


@pytest.mark.asyncio
async def test_research_planner_returns_structured_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    planner_output = research_planner.ResearchPlan(
        project_name="Arbitrum",
        coin_ticker="arb",
        plan="1. Recent news\n2. Project fundamentals\n3. Community activity",
        news_queries=["Arbitrum latest news 2026", "Arbitrum partnership announcement"],
        community_queries=["Arbitrum site:reddit.com", "Arbitrum twitter sentiment"],
    )
    model = _DummyPlannerModel(planner_output)
    monkeypatch.setattr(research_planner, "get_chat_model", lambda: model)
    search_coins = AsyncMock()
    monkeypatch.setattr(research_planner, "search_coins", search_coins)

    result = await research_planner.research_planner_node({"input": "Research Arbitrum"})

    assert result["plan"] == planner_output.plan
    assert result["project_name"] == "Arbitrum"
    assert result["coin_ticker"] == "ARB"
    assert result["news_queries"] == planner_output.news_queries
    assert result["community_queries"] == planner_output.community_queries
    search_coins.assert_not_awaited()
    assert model.schemas == [research_planner.ResearchPlan]
    assert len(model.structured_model.calls) == 1


@pytest.mark.asyncio
async def test_project_verifier_returns_verified_coin_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        research_planner,
        "search_coins",
        AsyncMock(
            return_value=json.dumps([{"id": "arbitrum", "name": "Arbitrum", "symbol": "ARB", "market_cap_rank": 40}])
        ),
    )

    result = await research_planner.project_verifier_node(
        {
            "input": "Research Arbitrum",
            "project_name": "Arbitrum",
            "coin_ticker": "ARB",
        }
    )

    assert result["coin_id"] == "arbitrum"
    assert result["ambiguous_matches"] == []


@pytest.mark.asyncio
async def test_project_verifier_returns_ambiguous_matches_without_interrupting(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        research_planner,
        "search_coins",
        AsyncMock(
            return_value=json.dumps(
                [
                    {"id": "mercury", "name": "Mercury", "symbol": "MER", "market_cap_rank": 999},
                    {"id": "mercury-wrapped", "name": "Mercury", "symbol": "WRAP", "market_cap_rank": 650},
                ]
            )
        ),
    )

    result = await research_planner.project_verifier_node(
        {
            "input": "Research Mercury",
            "project_name": "Mercury",
            "coin_ticker": "",
        }
    )

    assert result["coin_id"] == ""
    assert len(result["ambiguous_matches"]) == 2


@pytest.mark.asyncio
async def test_project_selector_interrupts_until_valid_coin_is_selected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    interrupt_payloads: list[dict[str, object]] = []
    responses = iter(
        [
            {"selected_coin_id": "not-a-real-coin"},
            {"selected_coin_id": "mercury"},
        ]
    )

    def fake_interrupt(payload: dict[str, object]) -> dict[str, str]:
        interrupt_payloads.append(payload)
        return next(responses)

    monkeypatch.setattr(research_planner, "interrupt", fake_interrupt)

    result = await research_planner.project_selector_node(
        {
            "input": "Research Mercury",
            "project_name": "Mercury",
            "coin_ticker": "",
            "ambiguous_matches": [
                {"coin_id": "mercury", "name": "Mercury", "symbol": "MER", "market_cap_rank": 999},
                {"coin_id": "mercury-wrapped", "name": "Mercury", "symbol": "WRAP", "market_cap_rank": 650},
            ],
        }
    )

    assert result["coin_id"] == "mercury"
    assert result["ambiguous_matches"] == []
    assert len(interrupt_payloads) == 2
    assert interrupt_payloads[0]["interrupt_type"] == "ambiguous_project"
    assert "not valid" in str(interrupt_payloads[1]["message"])


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
async def test_project_profiler_prefers_verified_coin_id(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _DummyTextModel("Arbitrum is an L2 optimistic rollup. Price: $1.23, Market cap: $4.5B")
    monkeypatch.setattr(project_profiler, "get_chat_model", lambda: model)
    monkeypatch.setattr(project_profiler, "search_coins", AsyncMock())
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
            "coin_id": "arbitrum",
        }
    )

    assert "L2 optimistic rollup" in result["profile"]
    project_profiler.search_coins.assert_not_called()


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
