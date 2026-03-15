"""Planner agent -- analyzes the request and creates a structured plan."""

from __future__ import annotations

from agent_common.llm import get_chat_model
from agent_common.tracing import verbose_log
from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.state import AgentState

SYSTEM_PROMPT = """You are a planning agent. Your job is to analyze the user's request and create
a clear, structured plan for researching and writing about the topic.

Output a numbered list of 2-4 sections that should be covered, with a brief description of what
each section should contain. Keep it concise and actionable."""


async def planner_node(state: AgentState) -> dict[str, str]:
    """Create a structured plan based on the user's input."""
    user_input = state["input"]
    verbose_log("Planner", f"Planning for: {user_input[:100]}")

    llm = get_chat_model()
    response = await llm.ainvoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_input),
        ]
    )

    plan = str(response.content)
    verbose_log("Planner", f"Plan created ({len(plan)} chars)")
    verbose_log("Planner", "Plan content", plan[:200])

    return {"plan": plan}
