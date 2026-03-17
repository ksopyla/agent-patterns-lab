"""Unit tests for research_planner, news_scanner, and intelligence_compiler nodes."""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import AsyncMock, patch

import pytest
from src.agents import intelligence_compiler, news_scanner, research_planner


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
    model = _DummyModel("1. Recent news\n2. Team background\n3. Technology")
    monkeypatch.setattr(research_planner, "get_chat_model", lambda: model)

    result = await research_planner.research_planner_node({"input": "Research Arbitrum"})

    assert result == {"plan": "1. Recent news\n2. Team background\n3. Technology"}
    assert len(model.calls) == 1

    sent_messages = model.calls[0]
    assert "research planner" in str(sent_messages[0].content)
    assert sent_messages[1].content == "Research Arbitrum"


@pytest.mark.asyncio
async def test_news_scanner_returns_analyzed_news(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _DummyModel("Arbitrum announced partnership with X. Community sentiment is bullish.")
    monkeypatch.setattr(news_scanner, "get_chat_model", lambda: model)

    mock_search = AsyncMock()
    mock_search.ainvoke = AsyncMock(return_value=[{"title": "Arbitrum news", "snippet": "Big partnership"}])
    with patch.object(news_scanner, "DuckDuckGoSearchResults", return_value=mock_search):
        state = {"input": "Research Arbitrum", "plan": "1. Recent news\n2. Partnerships"}
        result = await news_scanner.news_scanner_node(state)

    assert result == {"news": "Arbitrum announced partnership with X. Community sentiment is bullish."}
    assert len(model.calls) == 1

    sent_messages = model.calls[0]
    assert "news analyst" in str(sent_messages[0].content).lower()
    assert "Research Arbitrum" in str(sent_messages[1].content)
    assert "1. Recent news" in str(sent_messages[1].content)


@pytest.mark.asyncio
async def test_intelligence_compiler_returns_report(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _DummyModel("## Executive Summary\nArbitrum is an L2 scaling solution.")
    monkeypatch.setattr(intelligence_compiler, "get_chat_model", lambda: model)

    state = {
        "input": "Research Arbitrum",
        "plan": "1. News\n2. Team",
        "news": "Partnership with Coinbase announced. Community bullish.",
    }
    result = await intelligence_compiler.intelligence_compiler_node(state)

    assert result == {"report": "## Executive Summary\nArbitrum is an L2 scaling solution."}
    assert len(model.calls) == 1

    sent_messages = model.calls[0]
    assert "intelligence analyst" in str(sent_messages[0].content).lower()
    assert "1. News\n2. Team" in str(sent_messages[1].content)
    assert "Partnership with Coinbase" in str(sent_messages[1].content)
