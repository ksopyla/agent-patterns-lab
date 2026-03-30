"""News Scanner agent -- searches the web for recent news about a crypto project.

Reads:  state["project_name"], state["coin_ticker"], state["plan"]
Writes: state["news"]

Uses DuckDuckGo web search directly (not through MCP). Fires multiple targeted
queries built from the project name and plan, then deduplicates results before
passing them to the LLM for analysis. Focuses on: news, partnerships,
announcements, events, sentiment from finance/crypto portals.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime

from agent_common.llm import get_chat_model
from agent_common.tracing import verbose_log
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.state import AgentState

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


def _extract_plan_queries(plan: str) -> list[str]:
    """Pull queries from the NEWS_QUERIES: section of the research plan."""
    match = re.search(
        r"NEWS_QUERIES:\s*\n(.*?)(?:\n\s*\n|\nCOMMUNITY_QUERIES:|\Z)",
        plan,
        re.DOTALL | re.IGNORECASE,
    )
    if not match:
        return []
    lines = match.group(1).strip().splitlines()
    queries: list[str] = []
    for line in lines:
        cleaned = re.sub(r"^[\s\-\d.*•]+", "", line).strip().strip('"').strip("'")
        if cleaned:
            queries.append(cleaned)
    return queries


def _build_queries(project_name: str, ticker: str, plan: str) -> list[str]:
    """Build search queries from plan and fallback templates."""
    plan_queries = _extract_plan_queries(plan)
    if plan_queries:
        return plan_queries[:4]

    current_year = datetime.now(UTC).year
    return [
        f"{project_name} latest news {current_year}",
        f"{project_name} partnership announcement",
        f"{project_name} {ticker} crypto update",
        f"{ticker} crypto regulatory news {current_year}",
    ]


def _deduplicate_results(all_results: list[dict[str, str]]) -> list[dict[str, str]]:
    """Remove duplicate search results by URL."""
    seen_urls: set[str] = set()
    unique: list[dict[str, str]] = []
    for item in all_results:
        url = item.get("link", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique.append(item)
    return unique


async def news_scanner_node(state: AgentState) -> dict[str, str]:
    """Search the web for crypto project news and analyze results."""
    project_name = state.get("project_name", state["input"])
    ticker = state.get("coin_ticker", "")
    plan = state.get("plan", "")
    verbose_log("NewsScanner", f"Searching news for: {project_name} ({ticker})")

    queries = _build_queries(project_name, ticker, plan)
    verbose_log("NewsScanner", f"Running {len(queries)} search queries")

    all_results: list[dict[str, str]] = []
    search = DuckDuckGoSearchResults(
        max_results=5,  # type: ignore[call-arg]
        output_format="list",
    )

    for query in queries:
        try:
            raw = await search.ainvoke(query)
            if isinstance(raw, list):
                all_results.extend(raw)
                verbose_log("NewsScanner", f"  [{query[:50]}] → {len(raw)} results")
        except Exception as exc:
            verbose_log("NewsScanner", f"  [{query[:50]}] search failed: {exc}")

    unique_results = _deduplicate_results(all_results)
    verbose_log(
        "NewsScanner",
        f"Total: {len(all_results)} raw → {len(unique_results)} unique results",
    )

    results_text = (
        "\n".join(f"- [{r.get('title', 'N/A')}]({r.get('link', '')}): {r.get('snippet', '')}" for r in unique_results)
        or "[No search results found]"
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
