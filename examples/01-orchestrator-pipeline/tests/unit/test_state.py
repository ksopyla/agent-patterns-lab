"""Unit tests for AgentState typed dict."""

from __future__ import annotations

from src.agents.state import AgentState


def test_state_requires_input() -> None:
    state: AgentState = {"input": "Research Arbitrum"}
    assert state["input"] == "Research Arbitrum"


def test_state_optional_fields() -> None:
    state: AgentState = {
        "input": "Research Arbitrum",
        "plan": "1. News\n2. Team",
        "news": "Partnership announced",
        "report": "## Executive Summary",
    }
    assert state["plan"] == "1. News\n2. Team"
    assert state["news"] == "Partnership announced"
    assert state["report"] == "## Executive Summary"
