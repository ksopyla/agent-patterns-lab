"""LangGraph StateGraph wiring for the full Team 1 intelligence pipeline.

Pipeline: research_planner -> news_scanner -> project_profiler -> community_analyst -> intelligence_compiler

The news_scanner uses DuckDuckGo directly (not through MCP).
The project_profiler and community_analyst use the crypto-intelligence MCP server (SSE transport).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agent_common.tracing import verbose_log
from langgraph.graph import END, StateGraph

from src.agents.community_analyst import community_analyst_node
from src.agents.intelligence_compiler import intelligence_compiler_node
from src.agents.news_scanner import news_scanner_node
from src.agents.project_profiler import project_profiler_node
from src.agents.research_planner import research_planner_node
from src.agents.state import AgentState

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph


def build_graph() -> CompiledStateGraph:  # type: ignore[type-arg]
    """Build and compile the full crypto intelligence pipeline graph."""
    verbose_log(
        "System",
        "Building graph: research_planner -> news_scanner -> project_profiler -> community_analyst -> compiler",
    )

    graph = StateGraph(AgentState)

    graph.add_node("research_planner", research_planner_node)
    graph.add_node("news_scanner", news_scanner_node)
    graph.add_node("project_profiler", project_profiler_node)
    graph.add_node("community_analyst", community_analyst_node)
    graph.add_node("intelligence_compiler", intelligence_compiler_node)

    graph.set_entry_point("research_planner")
    graph.add_edge("research_planner", "news_scanner")
    graph.add_edge("news_scanner", "project_profiler")
    graph.add_edge("project_profiler", "community_analyst")
    graph.add_edge("community_analyst", "intelligence_compiler")
    graph.add_edge("intelligence_compiler", END)

    return graph.compile()
