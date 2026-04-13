"""Typed state shared across all Pattern 03 agent nodes.

Data flow:
  research_planner -> project_verifier -> project_selector
                   -> [news_scanner, project_profiler, community_analyst] (parallel)
                   -> intelligence_compiler

research_planner populates: plan, project_name, coin_ticker,
                            news_queries, community_queries
project_verifier populates: coin_id, ambiguous_matches
project_selector populates: coin_id (after resume), clears ambiguous_matches
news_scanner populates:     news
project_profiler populates: profile
community_analyst populates: community
intelligence_compiler populates: report
"""

from __future__ import annotations

from typing import Required, TypedDict


class CoinMatch(TypedDict):
    coin_id: str
    name: str
    symbol: str
    market_cap_rank: int | None


class AgentState(TypedDict, total=False):
    input: Required[str]

    # Research planner outputs
    plan: str
    project_name: str
    coin_ticker: str
    coin_id: str
    news_queries: list[str]
    community_queries: list[str]
    ambiguous_matches: list[CoinMatch]

    # Parallel research branch outputs
    news: str
    profile: str
    community: str

    # Final synthesis
    report: str
