"""Unit tests for Pattern 02 AgentState."""

from __future__ import annotations

from src.agents.state import AgentState


def test_state_requires_input() -> None:
    state: AgentState = {"input": "Research Arbitrum"}
    assert state["input"] == "Research Arbitrum"


def test_state_all_fields() -> None:
    state: AgentState = {
        "input": "Research Arbitrum",
        "plan": "1. News\n2. Team",
        "news": "Partnership announced",
        "profile": "L2 scaling solution",
        "community": "Strong community health",
        "report": "## Executive Summary",
    }
    assert state["profile"] == "L2 scaling solution"
    assert state["community"] == "Strong community health"
