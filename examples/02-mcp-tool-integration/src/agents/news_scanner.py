"""News Scanner agent -- searches the web for recent news about a crypto project.

Reads:  state["project_name"], state["coin_ticker"], state["news_queries"]
Writes: state["news"]

Uses DuckDuckGo web search directly (not through MCP). It receives typed search
queries from research_planner and falls back to simple templates when those are
missing. Shared search mechanics live in src.agents.web_search.
"""

from __future__ import annotations

from datetime import UTC, datetime

from agent_common.llm import get_chat_model
from agent_common.tracing import verbose_log
from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.state import AgentState
from src.agents.web_search import format_search_results, run_search_queries

SYSTEM_PROMPT = """\
You are a crypto news analyst. You receive raw web search results about a crypto project.

Your focus areas:
- Partnerships and strategic announcements
- Recent events — positive and negative
- Overall sentiment on finance portals and crypto media
- Regulatory or exchange-related developments
- Any red flags (hacks, lawsuits, team departures)

For each finding provide:
- The fact or claim (one sentence)
- Source attribution (site name or URL)
- How recent it appears

End with a 2-sentence "News Sentiment" summary (bullish / bearish / neutral with reasoning).
If search results are thin, say so explicitly — do NOT fabricate information."""


def _build_queries(project_name: str, ticker: str, news_queries: list[str]) -> list[str]:
    """Build search queries from planner output and fallback templates."""
    if news_queries:
        return news_queries[:4]

    current_year = datetime.now(UTC).year
    return [
        f"{project_name} latest news {current_year}",
        f"{project_name} partnership announcement",
        f"{project_name} {ticker} crypto update",
        f"{ticker} crypto regulatory news {current_year}",
    ]


async def news_scanner_node(state: AgentState) -> dict[str, str]:
    """Search the web for crypto project news and analyze results."""
    project_name = state.get("project_name", state["input"])
    ticker = state.get("coin_ticker", "")
    news_queries = state.get("news_queries", [])
    verbose_log("NewsScanner", f"Searching news for: {project_name} ({ticker})")

    queries = _build_queries(project_name, ticker, news_queries)
    verbose_log("NewsScanner", f"Running {len(queries)} search queries")

    search_results = await run_search_queries(queries, "NewsScanner")
    results_text = format_search_results(
        search_results,
        empty_message="[No search results found]",
    )

    try:
        llm = get_chat_model()
        response = await llm.ainvoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=(f"Project: {project_name} ({ticker})\n\nWeb search results:\n{results_text}")),
            ]
        )
        news = str(response.content)
    except Exception as exc:
        verbose_log("NewsScanner", f"LLM call failed: {exc}")
        news = f"[News analysis failed: {type(exc).__name__}] Raw data:\n{results_text}"

    verbose_log("NewsScanner", f"Analysis complete ({len(news)} chars)")
    return {"news": news}
