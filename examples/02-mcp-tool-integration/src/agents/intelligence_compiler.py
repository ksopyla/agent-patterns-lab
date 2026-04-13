"""Intelligence Compiler agent -- synthesizes all research into a structured report.

Reads:  state["input"], state["project_name"], state["coin_ticker"],
        state["news"], state["profile"], state["community"]
Writes: state["report"]

This is the fan-in node that waits for all parallel research branches to
complete, then produces the final intelligence report.
"""

from __future__ import annotations

from agent_common.llm import get_chat_model
from agent_common.tracing import verbose_log
from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.state import AgentState

SYSTEM_PROMPT = """\
You are a senior crypto intelligence analyst producing a client-facing report.
You receive three independent research outputs: news analysis, project profile \
(with market and developer data), and community sentiment assessment.

Produce a comprehensive intelligence report with these sections:

1. **Executive Summary** — 2-3 sentence overview: what the project is, its current \
market position, and the overall signal (bullish/bearish/neutral).

2. **Market Snapshot** — Current price, market cap, 24h volume, 24h change. \
Use exact numbers from the profile data. If unavailable, state "Data not available".

3. **Key Findings** — Top 5 most important discoveries across all research. \
Prioritize facts that would affect an investment decision.

4. **Recent Developments** — Notable news, partnerships, milestones from the \
news analysis. Include dates and sources where available.

5. **Developer & Community Health** — GitHub activity metrics, community size, \
social sentiment. Cite specific numbers (stars, forks, commits, followers).

6. **Risk Factors** — Concrete concerns: declining metrics, regulatory threats, \
team issues, competitive pressure. No generic boilerplate.

7. **Outlook** — Forward-looking assessment with a confidence level \
(High / Medium / Low) and 1-2 specific catalysts or risks to watch.

Rules:
- Under 600 words total.
- Clearly distinguish verified facts from speculation.
- If an entire section has no data, write "Insufficient data for this section."
- Do NOT fabricate numbers, team members, or partnerships."""


async def intelligence_compiler_node(state: AgentState) -> dict[str, str]:
    """Compile all research findings into a structured intelligence report."""
    project_name = state.get("project_name", state["input"])
    ticker = state.get("coin_ticker", "")
    verbose_log("IntelligenceCompiler", f"Compiling report for {project_name} ({ticker})")

    news = state.get("news", "N/A")
    profile = state.get("profile", "N/A")
    community = state.get("community", "N/A")

    llm = get_chat_model()
    response = await llm.ainvoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"Project: {project_name} ({ticker})\n\n"
                    f"--- NEWS ANALYSIS ---\n{news}\n\n"
                    f"--- PROJECT PROFILE (market data + developer stats) ---\n{profile}\n\n"
                    f"--- COMMUNITY SENTIMENT ---\n{community}"
                )
            ),
        ]
    )

    report = str(response.content)
    verbose_log("IntelligenceCompiler", f"Report generated ({len(report)} chars)")

    return {"report": report}
