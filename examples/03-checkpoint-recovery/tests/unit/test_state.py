"""Unit tests for Pattern 03 AgentState."""

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
        "coin_id": "arbitrum",
        "news_queries": ["Arbitrum latest news 2026"],
        "community_queries": ["Arbitrum site:reddit.com"],
        "ambiguous_matches": [
            {
                "coin_id": "arbitrum",
                "name": "Arbitrum",
                "symbol": "ARB",
                "market_cap_rank": 40,
            }
        ],
        "news": "Partnership announced",
        "profile": "L2 scaling solution",
        "community": "Strong community health",
        "report": "## Executive Summary",
    }
    assert state["project_name"] == "Arbitrum"
    assert state["coin_ticker"] == "ARB"
    assert state["coin_id"] == "arbitrum"
    assert state["news_queries"] == ["Arbitrum latest news 2026"]
    assert state["community_queries"] == ["Arbitrum site:reddit.com"]
    assert state["ambiguous_matches"][0]["coin_id"] == "arbitrum"
    assert state["profile"] == "L2 scaling solution"
    assert state["community"] == "Strong community health"
