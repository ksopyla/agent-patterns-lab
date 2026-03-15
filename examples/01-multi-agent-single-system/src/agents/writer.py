"""Writer agent -- produces the final output using plan and research."""

from __future__ import annotations

from agent_common.llm import get_chat_model
from agent_common.tracing import verbose_log
from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.state import AgentState

SYSTEM_PROMPT = """You are a writing agent. You receive a plan and research findings.
Write a clear, well-structured piece that follows the plan and incorporates the research.

Keep the writing concise, professional, and informative. Use headers for each section.
Target 300-500 words."""


async def writer_node(state: AgentState) -> dict[str, str]:
    """Write the final output based on plan and research."""
    plan = state.get("plan", "")
    research = state.get("research", "")
    verbose_log("Writer", "Writing final output")

    llm = get_chat_model()
    response = await llm.ainvoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=f"Original request: {state['input']}\n\nPlan:\n{plan}\n\nResearch:\n{research}"
            ),
        ]
    )

    output = str(response.content)
    verbose_log("Writer", f"Output generated ({len(output)} chars)")

    return {"output": output}
