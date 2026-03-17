"""Research Planner agent -- creates a structured research plan for a crypto project."""

from __future__ import annotations

from agent_common.llm import get_chat_model
from agent_common.tracing import verbose_log
from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.state import AgentState

SYSTEM_PROMPT = """\
You are a crypto project research planner. Given a crypto project name or topic,
create a focused research plan covering these areas:

1. Recent news, announcements, and partnerships
2. Project fundamentals: goals, technology, roadmap, team
3. Community and developer activity: GitHub commits, social media sentiment
4. Market positioning: categories, competitors, unique value proposition

Output a numbered list with one sentence per area describing what to investigate.
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
