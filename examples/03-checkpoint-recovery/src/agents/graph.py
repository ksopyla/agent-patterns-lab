"""LangGraph StateGraph wiring for the Pattern 03 intelligence pipeline.

Architecture (fan-out / fan-in):

  research_planner -> project_verifier -> project_selector
                                               |
                                               +-> news_scanner ---------\
                                               +-> project_profiler ------> intelligence_compiler
                                               +-> community_analyst ----/

The three research nodes run in parallel after the project has either been
verified automatically or selected by the human.

Pattern 03 adds a durable checkpointer at compile time so runs can resume after
failure or interrupt.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from agent_common.tracing import verbose_log
from langgraph.graph import END, START, StateGraph

from src.agents.community_analyst import community_analyst_node
from src.agents.intelligence_compiler import intelligence_compiler_node
from src.agents.news_scanner import news_scanner_node
from src.agents.project_profiler import project_profiler_node
from src.agents.research_planner import project_selector_node, project_verifier_node, research_planner_node
from src.agents.state import AgentState

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph


def build_graph(*, checkpointer: Any | None = None) -> CompiledStateGraph:  # type: ignore[type-arg]
    """Build and compile the checkpoint-capable crypto intelligence pipeline."""
    verbose_log(
        "System",
        (
            "Building graph: research_planner → project_verifier → project_selector "
            "→ [news_scanner | project_profiler | community_analyst] → compiler"
        ),
    )

    graph = StateGraph(AgentState)

    graph.add_node("research_planner", research_planner_node)
    graph.add_node("project_verifier", project_verifier_node)
    graph.add_node("project_selector", project_selector_node)
    graph.add_node("news_scanner", news_scanner_node)
    graph.add_node("project_profiler", project_profiler_node)
    graph.add_node("community_analyst", community_analyst_node)
    graph.add_node("intelligence_compiler", intelligence_compiler_node)

    graph.add_edge(START, "research_planner")
    graph.add_edge("research_planner", "project_verifier")
    graph.add_edge("project_verifier", "project_selector")

    # Fan-out: project selection → three parallel research branches
    graph.add_edge("project_selector", "news_scanner")
    graph.add_edge("project_selector", "project_profiler")
    graph.add_edge("project_selector", "community_analyst")

    # Fan-in: all branches → compiler
    graph.add_edge("news_scanner", "intelligence_compiler")
    graph.add_edge("project_profiler", "intelligence_compiler")
    graph.add_edge("community_analyst", "intelligence_compiler")

    graph.add_edge("intelligence_compiler", END)

    if checkpointer is None:
        return graph.compile()

    return graph.compile(checkpointer=checkpointer)
