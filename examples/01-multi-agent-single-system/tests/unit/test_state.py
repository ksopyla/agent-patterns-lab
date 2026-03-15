"""Unit tests for the shared agent state."""

from __future__ import annotations

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
