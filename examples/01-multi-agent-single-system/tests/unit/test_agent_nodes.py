"""Unit tests for planner, researcher, and writer nodes."""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from src.agents import planner, researcher, writer


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
async def test_planner_node_returns_plan(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _DummyModel("1. Scope\n2. Research")
    monkeypatch.setattr(planner, "get_chat_model", lambda: model)

    result = await planner.planner_node({"input": "Explain agent patterns"})

    assert result == {"plan": "1. Scope\n2. Research"}
    assert len(model.calls) == 1

    sent_messages = model.calls[0]
    assert "planning agent" in str(sent_messages[0].content)
    assert sent_messages[1].content == "Explain agent patterns"


@pytest.mark.asyncio
async def test_researcher_node_returns_research(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _DummyModel("Fact A\nFact B")
    monkeypatch.setattr(researcher, "get_chat_model", lambda: model)

    state = {"input": "Explain MCP", "plan": "1. Overview\n2. Trade-offs"}
    result = await researcher.researcher_node(state)

    assert result == {"research": "Fact A\nFact B"}
    assert len(model.calls) == 1

    sent_messages = model.calls[0]
    assert "research agent" in str(sent_messages[0].content)
    assert "Original request: Explain MCP" in str(sent_messages[1].content)
    assert "Plan:\n1. Overview\n2. Trade-offs" in str(sent_messages[1].content)


@pytest.mark.asyncio
async def test_writer_node_returns_output(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _DummyModel("## Final answer")
    monkeypatch.setattr(writer, "get_chat_model", lambda: model)

    state = {
        "input": "Write about LangGraph",
        "plan": "1. Basics\n2. Example",
        "research": "LangGraph supports stateful workflows",
    }
    result = await writer.writer_node(state)

    assert result == {"output": "## Final answer"}
    assert len(model.calls) == 1

    sent_messages = model.calls[0]
    assert "writing agent" in str(sent_messages[0].content)
    assert "Plan:\n1. Basics\n2. Example" in str(sent_messages[1].content)
    assert "Research:\nLangGraph supports stateful workflows" in str(sent_messages[1].content)
