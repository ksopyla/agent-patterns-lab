"""Intelligence Compiler agent -- synthesizes research into a structured report."""

from __future__ import annotations

from agent_common.llm import get_chat_model
from agent_common.tracing import verbose_log
from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.state import AgentState

SYSTEM_PROMPT = """\
You are a crypto intelligence analyst. You receive a research plan and analyzed news
findings about a crypto project.

Produce a structured intelligence report with the following sections:
1. **Executive Summary** -- 2-3 sentence overview of the project's current state
2. **Key Findings** -- Bullet points of the most important discoveries
3. **Recent Developments** -- Notable news, partnerships, or milestones
4. **Risk Factors** -- Potential concerns or red flags
5. **Outlook** -- Brief forward-looking assessment

Keep the report factual, professional, and concise (300-500 words).
Clearly distinguish between verified facts and speculation."""


async def intelligence_compiler_node(state: AgentState) -> dict[str, str]:
    """Compile research findings into a structured intelligence report."""
    plan = state.get("plan", "")
    news = state.get("news", "")
    verbose_log("IntelligenceCompiler", "Compiling intelligence report")

    try:
        llm = get_chat_model()
        response = await llm.ainvoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(
                    content=(
                        f"Crypto project: {state['input']}\n\nResearch plan:\n{plan}\n\nAnalyzed findings:\n{news}"
                    )
                ),
            ]
        )
        report = str(response.content)
    except Exception as exc:
        verbose_log("IntelligenceCompiler", f"LLM call failed: {exc}")
        report = f"[Report generation failed: {type(exc).__name__}]\n\nRaw plan:\n{plan}\n\nRaw findings:\n{news}"

    verbose_log("IntelligenceCompiler", f"Report generated ({len(report)} chars)")
    return {"report": report}
