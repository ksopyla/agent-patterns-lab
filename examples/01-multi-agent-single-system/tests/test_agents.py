"""Tests for the multi-agent pipeline."""

from __future__ import annotations

import pytest

from src.agents.researcher import researcher_node
from src.agents.state import AgentState


def test_agent_state_accepts_required_fields() -> None:
    state: AgentState = {"input": "test request"}
    assert state["input"] == "test request"


def test_agent_state_accepts_all_fields() -> None:
    state: AgentState = {
        "input": "test",
        "plan": "plan text",
        "research": "research text",
        "output": "output text",
    }
    assert state["output"] == "output text"


async def test_researcher_node_handles_missing_plan(monkeypatch: pytest.MonkeyPatch) -> None:
    class _DummyModel:
        async def ainvoke(self, _messages: list[object]) -> object:
            return type("_Response", (), {"content": "research result"})()

    monkeypatch.setattr("src.agents.researcher.get_chat_model", lambda: _DummyModel())

    result = await researcher_node({"input": "test request"})

    assert result == {"research": "research result"}
