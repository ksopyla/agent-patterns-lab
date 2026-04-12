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
        "project_name": "Arbitrum",
        "coin_ticker": "ARB",
        "news_queries": ["Arbitrum latest news 2026"],
        "community_queries": ["Arbitrum site:reddit.com"],
        "news": "Partnership announced",
        "profile": "L2 scaling solution",
        "community": "Strong community health",
        "report": "## Executive Summary",
    }
    assert state["project_name"] == "Arbitrum"
    assert state["coin_ticker"] == "ARB"
    assert state["news_queries"] == ["Arbitrum latest news 2026"]
    assert state["community_queries"] == ["Arbitrum site:reddit.com"]
    assert state["profile"] == "L2 scaling solution"
    assert state["community"] == "Strong community health"
