"""LangGraph StateGraph wiring: planner -> researcher -> writer."""

from __future__ import annotations

from typing import TYPE_CHECKING

from agent_common.tracing import verbose_log
from langgraph.graph import END, StateGraph

from src.agents.planner import planner_node
from src.agents.researcher import researcher_node
from src.agents.state import AgentState
from src.agents.writer import writer_node

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph


def build_graph() -> CompiledStateGraph:
    """Build and compile the multi-agent pipeline graph."""
    verbose_log("System", "Building agent graph: planner -> researcher -> writer")

    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("writer", writer_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", END)

    return graph.compile()
