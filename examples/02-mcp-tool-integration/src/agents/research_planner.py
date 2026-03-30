"""Research Planner agent -- orchestrates the research pipeline.

Reads:  state["input"]
Writes: state["plan"], state["project_name"], state["coin_ticker"]

The planner is the first node in the graph. It analyzes the user request,
identifies the crypto project, and produces a research plan with tailored
queries that downstream nodes (news_scanner, project_profiler,
community_analyst) will use. This eliminates raw user input being passed
directly to external APIs and search engines.
"""

from __future__ import annotations

import re

from agent_common.llm import get_chat_model
from agent_common.tracing import verbose_log
from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.state import AgentState

SYSTEM_PROMPT = """\
You are a crypto project research planner. Given a user query, do three things:

1. **Identify the project.** On the FIRST line write exactly:
   PROJECT_NAME: <official project name>
   On the SECOND line write exactly:
   COIN_TICKER: <ticker symbol, uppercase>

2. **Create a focused research plan** (numbered list, one sentence per area):
   a. Recent news, announcements, partnerships, events — positive and negative signals.
   b. Project fundamentals via CoinGecko: market cap, price, volume, exchanges, \
team, genesis date, categories.
   c. Community and social sentiment: X/Twitter buzz, Reddit discussions, \
Telegram activity, overall retail mood.

3. **Generate tailored search queries** for downstream research agents.
   Write a section headed "NEWS_QUERIES:" with 3-4 web search queries \
optimised for finding recent project news, partnerships, and announcements.
   Write a section headed "COMMUNITY_QUERIES:" with 3-4 web search queries \
optimised for social media sentiment (use site:reddit.com or X/twitter keywords).

Keep the plan concise and actionable. Do NOT include price predictions."""


def _extract_field(text: str, label: str) -> str:
    """Pull a 'LABEL: value' field from the plan text."""
    pattern = rf"^{re.escape(label)}:\s*(.+)$"
    match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
    return match.group(1).strip() if match else ""


async def research_planner_node(state: AgentState) -> dict[str, str]:
    """Create a structured research plan and extract project identifiers."""
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

    project_name = _extract_field(plan, "PROJECT_NAME") or user_input.strip()
    coin_ticker = _extract_field(plan, "COIN_TICKER") or ""

    verbose_log(
        "ResearchPlanner",
        f"Identified project={project_name!r}, ticker={coin_ticker!r}, plan={len(plan)} chars",
    )

    return {"plan": plan, "project_name": project_name, "coin_ticker": coin_ticker}
