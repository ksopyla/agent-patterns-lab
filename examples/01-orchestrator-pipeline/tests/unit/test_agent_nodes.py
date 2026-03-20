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


class _FailingModel:
    async def ainvoke(self, messages: list[object]) -> _DummyResponse:
        raise ConnectionError("LLM service unavailable")


# --- Research Planner ---


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
async def test_research_planner_handles_llm_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(research_planner, "get_chat_model", lambda: _FailingModel())

    result = await research_planner.research_planner_node({"input": "Research Arbitrum"})

    assert "ConnectionError" in result["plan"]
    assert "Fallback" in result["plan"]


# --- News Scanner ---


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
async def test_news_scanner_handles_search_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _DummyModel("Analysis based on limited data.")
    monkeypatch.setattr(news_scanner, "get_chat_model", lambda: model)

    mock_search = AsyncMock()
    mock_search.ainvoke = AsyncMock(side_effect=TimeoutError("Search timed out"))
    with patch.object(news_scanner, "DuckDuckGoSearchResults", return_value=mock_search):
        state = {"input": "Research Arbitrum", "plan": "1. News"}
        result = await news_scanner.news_scanner_node(state)

    assert result == {"news": "Analysis based on limited data."}


@pytest.mark.asyncio
async def test_news_scanner_handles_llm_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(news_scanner, "get_chat_model", lambda: _FailingModel())

    mock_search = AsyncMock()
    mock_search.ainvoke = AsyncMock(return_value=[{"title": "data"}])
    with patch.object(news_scanner, "DuckDuckGoSearchResults", return_value=mock_search):
        state = {"input": "Research Arbitrum", "plan": "1. News"}
        result = await news_scanner.news_scanner_node(state)

    assert "ConnectionError" in result["news"]
    assert "Raw search data" in result["news"]


# --- Intelligence Compiler ---


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


@pytest.mark.asyncio
async def test_intelligence_compiler_handles_llm_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(intelligence_compiler, "get_chat_model", lambda: _FailingModel())

    state = {"input": "Research Arbitrum", "plan": "plan text", "news": "news text"}
    result = await intelligence_compiler.intelligence_compiler_node(state)

    assert "ConnectionError" in result["report"]
    assert "plan text" in result["report"]
    assert "news text" in result["report"]
