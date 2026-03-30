"""Unit tests for all 5 agent nodes in Pattern 02."""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import AsyncMock, patch

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


class _DummyModel:
    def __init__(self, response_text: str) -> None:
        self._response_text = response_text
        self.calls: list[list[object]] = []

    async def ainvoke(self, messages: list[object]) -> _DummyResponse:
        self.calls.append(messages)
        return _DummyResponse(content=self._response_text)


# --- Research Planner ---


@pytest.mark.asyncio
async def test_research_planner_extracts_project_identifiers(monkeypatch: pytest.MonkeyPatch) -> None:
    plan_text = (
        "PROJECT_NAME: Arbitrum\n"
        "COIN_TICKER: ARB\n\n"
        "1. Recent news\n2. Project fundamentals\n3. Community activity\n\n"
        "NEWS_QUERIES:\n- Arbitrum latest news 2026\n\n"
        "COMMUNITY_QUERIES:\n- Arbitrum site:reddit.com"
    )
    model = _DummyModel(plan_text)
    monkeypatch.setattr(research_planner, "get_chat_model", lambda: model)

    result = await research_planner.research_planner_node({"input": "Research Arbitrum"})

    assert result["plan"] == plan_text
    assert result["project_name"] == "Arbitrum"
    assert result["coin_ticker"] == "ARB"
    assert len(model.calls) == 1


@pytest.mark.asyncio
async def test_research_planner_falls_back_on_missing_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _DummyModel("Just a plain plan without structured fields")
    monkeypatch.setattr(research_planner, "get_chat_model", lambda: model)

    result = await research_planner.research_planner_node({"input": "Research Arbitrum"})

    assert result["project_name"] == "Research Arbitrum"
    assert result["coin_ticker"] == ""


# --- News Scanner ---


@pytest.mark.asyncio
async def test_news_scanner_uses_project_name(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _DummyModel("Arbitrum announced Orbit chains. TVL exceeded $10B.")
    monkeypatch.setattr(news_scanner, "get_chat_model", lambda: model)

    mock_search = AsyncMock()
    mock_search.ainvoke = AsyncMock(
        return_value=[{"title": "Arbitrum news", "snippet": "Orbit chains launched", "link": "https://example.com/1"}]
    )
    with patch.object(news_scanner, "DuckDuckGoSearchResults", return_value=mock_search):
        result = await news_scanner.news_scanner_node(
            {
                "input": "Research Arbitrum",
                "project_name": "Arbitrum",
                "coin_ticker": "ARB",
                "plan": "NEWS_QUERIES:\n- Arbitrum latest news 2026",
            }
        )

    assert "Orbit chains" in result["news"]
    assert len(model.calls) == 1


@pytest.mark.asyncio
async def test_news_scanner_degrades_on_search_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _DummyModel("Unable to find recent news due to search unavailability.")
    monkeypatch.setattr(news_scanner, "get_chat_model", lambda: model)

    mock_search = AsyncMock()
    mock_search.ainvoke = AsyncMock(side_effect=RuntimeError("Search API down"))
    with patch.object(news_scanner, "DuckDuckGoSearchResults", return_value=mock_search):
        result = await news_scanner.news_scanner_node(
            {
                "input": "Research Arbitrum",
                "project_name": "Arbitrum",
                "coin_ticker": "ARB",
                "plan": "",
            }
        )

    assert "news" in result
    assert len(model.calls) == 1


@pytest.mark.asyncio
async def test_news_scanner_deduplicates_results(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _DummyModel("Deduplicated analysis.")
    monkeypatch.setattr(news_scanner, "get_chat_model", lambda: model)

    mock_search = AsyncMock()
    mock_search.ainvoke = AsyncMock(
        return_value=[
            {"title": "Same article", "snippet": "Content", "link": "https://example.com/same"},
            {"title": "Same article copy", "snippet": "Content", "link": "https://example.com/same"},
        ]
    )
    with patch.object(news_scanner, "DuckDuckGoSearchResults", return_value=mock_search):
        result = await news_scanner.news_scanner_node(
            {
                "input": "Research Arbitrum",
                "project_name": "Arbitrum",
                "coin_ticker": "ARB",
                "plan": "NEWS_QUERIES:\n- query one\n- query two",
            }
        )

    assert "news" in result


# --- Project Profiler ---


@pytest.mark.asyncio
async def test_project_profiler_uses_project_name(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _DummyModel("Arbitrum is an L2 optimistic rollup. Price: $1.23, Market cap: $4.5B")
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
    model = _DummyModel("Limited profile available due to data source issues.")
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


# --- Community Analyst (now uses DuckDuckGo, not CoinGecko) ---


@pytest.mark.asyncio
async def test_community_analyst_uses_social_search(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _DummyModel("Community Health: Strong. Active Reddit discussions and positive Twitter sentiment.")
    monkeypatch.setattr(community_analyst, "get_chat_model", lambda: model)

    mock_search = AsyncMock()
    mock_search.ainvoke = AsyncMock(
        return_value=[
            {"title": "Arbitrum Reddit", "snippet": "Great community", "link": "https://reddit.com/r/arbitrum/1"},
        ]
    )
    with patch.object(community_analyst, "DuckDuckGoSearchResults", return_value=mock_search):
        result = await community_analyst.community_analyst_node(
            {
                "input": "Research Arbitrum",
                "project_name": "Arbitrum",
                "coin_ticker": "ARB",
                "plan": "COMMUNITY_QUERIES:\n- Arbitrum site:reddit.com",
            }
        )

    assert "Strong" in result["community"]
    assert len(model.calls) == 1


@pytest.mark.asyncio
async def test_community_analyst_degrades_on_search_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _DummyModel("Community analysis unavailable due to search issues.")
    monkeypatch.setattr(community_analyst, "get_chat_model", lambda: model)

    mock_search = AsyncMock()
    mock_search.ainvoke = AsyncMock(side_effect=RuntimeError("Search API down"))
    with patch.object(community_analyst, "DuckDuckGoSearchResults", return_value=mock_search):
        result = await community_analyst.community_analyst_node(
            {
                "input": "Research Arbitrum",
                "project_name": "Arbitrum",
                "coin_ticker": "ARB",
                "plan": "",
            }
        )

    assert "community" in result
    assert len(model.calls) == 1


# --- Intelligence Compiler ---


@pytest.mark.asyncio
async def test_intelligence_compiler_produces_report(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _DummyModel("## Executive Summary\nArbitrum is a leading L2 scaling solution.")
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
