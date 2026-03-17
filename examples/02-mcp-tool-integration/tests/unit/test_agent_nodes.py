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


@pytest.mark.asyncio
async def test_research_planner_returns_plan(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _DummyModel("1. Recent news\n2. Project fundamentals\n3. Community activity")
    monkeypatch.setattr(research_planner, "get_chat_model", lambda: model)

    result = await research_planner.research_planner_node({"input": "Research Arbitrum"})

    assert result == {"plan": "1. Recent news\n2. Project fundamentals\n3. Community activity"}
    assert len(model.calls) == 1


@pytest.mark.asyncio
async def test_news_scanner_returns_news(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _DummyModel("Arbitrum announced Orbit chains. TVL exceeded $10B.")
    monkeypatch.setattr(news_scanner, "get_chat_model", lambda: model)

    mock_search = AsyncMock()
    mock_search.ainvoke = AsyncMock(return_value=[{"title": "Arbitrum news", "snippet": "Orbit chains launched"}])
    with patch.object(news_scanner, "DuckDuckGoSearchResults", return_value=mock_search):
        result = await news_scanner.news_scanner_node({"input": "Research Arbitrum", "plan": "1. News\n2. Tech"})

    assert "Orbit chains" in result["news"]
    assert len(model.calls) == 1
    mock_search.ainvoke.assert_called_once()


@pytest.mark.asyncio
async def test_project_profiler_uses_mcp_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _DummyModel("Arbitrum is an L2 optimistic rollup. Price: $1.23, Market cap: $4.5B")
    monkeypatch.setattr(project_profiler, "get_chat_model", lambda: model)

    mock_search = AsyncMock()
    mock_search.ainvoke = AsyncMock(return_value='[{"id": "arbitrum", "name": "Arbitrum", "symbol": "ARB"}]')
    mock_info = AsyncMock()
    mock_info.ainvoke = AsyncMock(return_value='{"name": "Arbitrum", "description": "L2 rollup"}')
    mock_price = AsyncMock()
    mock_price.ainvoke = AsyncMock(return_value='{"price": 1.23, "market_cap": 4500000000}')

    monkeypatch.setattr(
        project_profiler,
        "get_mcp_tool",
        lambda name: {
            "search_coins": mock_search,
            "get_coin_info": mock_info,
            "get_coin_price": mock_price,
        }[name],
    )

    result = await project_profiler.project_profiler_node({"input": "Research Arbitrum"})

    assert "L2 optimistic rollup" in result["profile"]
    mock_search.ainvoke.assert_called_once()
    mock_info.ainvoke.assert_called_once()
    mock_price.ainvoke.assert_called_once()


@pytest.mark.asyncio
async def test_community_analyst_uses_mcp_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _DummyModel("Community Health: Strong. Active GitHub with 500+ contributors.")
    monkeypatch.setattr(community_analyst, "get_chat_model", lambda: model)

    mock_search = AsyncMock()
    mock_search.ainvoke = AsyncMock(return_value='[{"id": "arbitrum", "name": "Arbitrum", "symbol": "ARB"}]')
    mock_info = AsyncMock()
    mock_info.ainvoke = AsyncMock(
        return_value='{"community_data": {"twitter_followers": 500000}, "developer_data": {"commits": 1200}}'
    )

    monkeypatch.setattr(
        community_analyst,
        "get_mcp_tool",
        lambda name: {
            "search_coins": mock_search,
            "get_coin_info": mock_info,
        }[name],
    )

    result = await community_analyst.community_analyst_node({"input": "Research Arbitrum"})

    assert "Strong" in result["community"]


@pytest.mark.asyncio
async def test_intelligence_compiler_produces_report(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _DummyModel("## Executive Summary\nArbitrum is a leading L2 scaling solution.")
    monkeypatch.setattr(intelligence_compiler, "get_chat_model", lambda: model)

    state = {
        "input": "Research Arbitrum",
        "plan": "1. News\n2. Profile\n3. Community",
        "news": "Orbit chains launched",
        "profile": "L2 rollup, $1.23, $4.5B mcap",
        "community": "Strong community health",
    }
    result = await intelligence_compiler.intelligence_compiler_node(state)

    assert "Executive Summary" in result["report"]
    assert "L2 scaling solution" in result["report"]
