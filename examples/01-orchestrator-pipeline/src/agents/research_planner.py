"""Research Planner agent -- analyzes the crypto project request and creates a research plan."""

from __future__ import annotations

from agent_common.llm import get_chat_model
from agent_common.tracing import verbose_log
from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.state import AgentState

SYSTEM_PROMPT = """\
You are a crypto project research planner. Given a crypto project name or topic,
create a focused research plan.

Output a numbered list of 3-5 specific research areas to investigate. For each area,
write one sentence describing what to look for. Focus on:
- Recent news, announcements, and partnerships
- Project goals, technology, and roadmap milestones
- Team background and recent updates
- Community sentiment and adoption signals
- Notable events or controversies

Keep it concise and actionable."""


async def research_planner_node(state: AgentState) -> dict[str, str]:
    """Create a structured research plan for the crypto project."""
    user_input = state["input"]
    verbose_log("ResearchPlanner", f"Planning research for: {user_input[:100]}")

    llm = get_chat_model()
    response = await llm.ainvoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_input),
        ]
    )

    plan = str(response.content)
    verbose_log("ResearchPlanner", f"Plan created ({len(plan)} chars)")

    return {"plan": plan}
