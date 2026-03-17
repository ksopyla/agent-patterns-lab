"""LangGraph StateGraph wiring: research_planner -> news_scanner -> intelligence_compiler."""

from __future__ import annotations

from typing import TYPE_CHECKING

from agent_common.tracing import verbose_log
from langgraph.graph import END, StateGraph

from src.agents.intelligence_compiler import intelligence_compiler_node
from src.agents.news_scanner import news_scanner_node
from src.agents.research_planner import research_planner_node
from src.agents.state import AgentState

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph


def build_graph() -> CompiledStateGraph:
    """Build and compile the crypto intelligence pipeline graph."""
    verbose_log("System", "Building agent graph: research_planner -> news_scanner -> intelligence_compiler")

    graph = StateGraph(AgentState)

    graph.add_node("research_planner", research_planner_node)
    graph.add_node("news_scanner", news_scanner_node)
    graph.add_node("intelligence_compiler", intelligence_compiler_node)

    graph.set_entry_point("research_planner")
    graph.add_edge("research_planner", "news_scanner")
    graph.add_edge("news_scanner", "intelligence_compiler")
    graph.add_edge("intelligence_compiler", END)

    return graph.compile()
