"""Typed state shared across all agent nodes in the full intelligence pipeline.

Data flow:
  research_planner → [news_scanner, project_profiler, community_analyst] (parallel)
                   → intelligence_compiler

research_planner populates: plan, project_name, coin_ticker, news_queries,
                            community_queries
news_scanner populates:     news
project_profiler populates: profile
community_analyst populates: community
intelligence_compiler populates: report
"""

from __future__ import annotations

from typing import Required, TypedDict


class AgentState(TypedDict, total=False):
    input: Required[str]

    # Research planner outputs
    plan: str
    project_name: str
    coin_ticker: str
    news_queries: list[str]
    community_queries: list[str]

    # Parallel research branch outputs
    news: str
    profile: str
    community: str

    # Final synthesis
    report: str
