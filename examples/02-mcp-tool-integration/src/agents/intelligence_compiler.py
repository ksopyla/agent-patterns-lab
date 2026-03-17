"""Intelligence Compiler agent -- synthesizes all research into a structured report."""

from __future__ import annotations

from agent_common.llm import get_chat_model
from agent_common.tracing import verbose_log
from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.state import AgentState

SYSTEM_PROMPT = """\
You are a senior crypto intelligence analyst. You receive a research plan, news analysis,
a project profile (with market data), and community health assessment.

Produce a comprehensive intelligence report with these sections:
1. **Executive Summary** -- 2-3 sentence overview of the project
2. **Market Snapshot** -- Current price, market cap, 24h change, volume
3. **Key Findings** -- Top 5 most important discoveries across all research
4. **Recent Developments** -- Notable news, partnerships, milestones
5. **Community & Development Health** -- Developer activity, community engagement
6. **Risk Factors** -- Potential concerns, red flags, or uncertainties
7. **Outlook** -- Forward-looking assessment with confidence level

Keep the report factual, professional, and under 600 words.
Clearly distinguish between verified facts and speculation."""


async def intelligence_compiler_node(state: AgentState) -> dict[str, str]:
    """Compile all research findings into a structured intelligence report."""
    verbose_log("IntelligenceCompiler", "Compiling intelligence report from all sources")

    llm = get_chat_model()
    response = await llm.ainvoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"Crypto project: {state['input']}\n\n"
                    f"Research plan:\n{state.get('plan', 'N/A')}\n\n"
                    f"News analysis:\n{state.get('news', 'N/A')}\n\n"
                    f"Project profile:\n{state.get('profile', 'N/A')}\n\n"
                    f"Community assessment:\n{state.get('community', 'N/A')}"
                )
            ),
        ]
    )

    report = str(response.content)
    verbose_log("IntelligenceCompiler", f"Report generated ({len(report)} chars)")

    return {"report": report}
