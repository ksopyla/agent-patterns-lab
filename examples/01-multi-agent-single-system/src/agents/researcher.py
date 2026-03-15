"""Researcher agent -- gathers information based on the plan."""

from __future__ import annotations

from agent_common.llm import get_chat_model
from agent_common.tracing import verbose_log
from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.state import AgentState

SYSTEM_PROMPT = """You are a research agent. You receive a plan with sections to cover.
For each section in the plan, provide 2-3 key facts, insights, or points that would be
useful for writing about that topic.

Be concise but informative. Focus on practical, actionable information."""


async def researcher_node(state: AgentState) -> dict[str, str]:
    """Research information for each section in the plan."""
    plan = state["plan"]
    verbose_log("Researcher", "Researching based on plan")

    llm = get_chat_model()
    response = await llm.ainvoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Original request: {state['input']}\n\nPlan:\n{plan}"),
        ]
    )

    research = str(response.content)
    verbose_log("Researcher", f"Research complete ({len(research)} chars)")

    return {"research": research}