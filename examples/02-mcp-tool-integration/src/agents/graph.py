"""LangGraph StateGraph wiring for the full Team 1 intelligence pipeline.

Architecture (fan-out / fan-in):

  research_planner ──┬── news_scanner ──────────┐
                     ├── project_profiler ───────┤── intelligence_compiler
                     └── community_analyst ──────┘

The three research nodes run in parallel after the planner finishes.
The compiler waits for all three branches to complete before synthesizing.

This graph is invoked from two entry points:
- POST /run (FastAPI, REST) in src/app.py
- research_crypto_project MCP tool in src/mcp_servers/crypto_intelligence.py
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agent_common.tracing import verbose_log
from langgraph.graph import END, START, StateGraph

from src.agents.community_analyst import community_analyst_node
from src.agents.intelligence_compiler import intelligence_compiler_node
from src.agents.news_scanner import news_scanner_node
from src.agents.project_profiler import project_profiler_node
from src.agents.research_planner import research_planner_node
from src.agents.state import AgentState

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph


def build_graph() -> CompiledStateGraph:  # type: ignore[type-arg]
    """Build and compile the crypto intelligence pipeline with parallel research."""
    verbose_log(
        "System",
        "Building graph: research_planner → [news_scanner | project_profiler | community_analyst] → compiler",
    )

    graph = StateGraph(AgentState)

    graph.add_node("research_planner", research_planner_node)
    graph.add_node("news_scanner", news_scanner_node)
    graph.add_node("project_profiler", project_profiler_node)
    graph.add_node("community_analyst", community_analyst_node)
    graph.add_node("intelligence_compiler", intelligence_compiler_node)

    graph.add_edge(START, "research_planner")

    # Fan-out: planner → three parallel research branches
    graph.add_edge("research_planner", "news_scanner")
    graph.add_edge("research_planner", "project_profiler")
    graph.add_edge("research_planner", "community_analyst")

    # Fan-in: all branches → compiler
    graph.add_edge("news_scanner", "intelligence_compiler")
    graph.add_edge("project_profiler", "intelligence_compiler")
    graph.add_edge("community_analyst", "intelligence_compiler")

    graph.add_edge("intelligence_compiler", END)

    return graph.compile()
