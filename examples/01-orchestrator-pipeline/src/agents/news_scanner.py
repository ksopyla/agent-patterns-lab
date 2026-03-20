"""News Scanner agent -- searches the web and analyzes findings about a crypto project."""

from __future__ import annotations

from datetime import UTC, datetime

from agent_common.llm import get_chat_model
from agent_common.tracing import verbose_log
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.state import AgentState

SYSTEM_PROMPT = """\
You are a crypto news analyst. You receive a research plan and raw web search results
about a crypto project.

Analyze the search results and extract the most relevant information organized by
the research plan's areas. For each area, provide:
- Key facts and data points found
- Notable quotes or claims
- How recent and reliable the information appears

If search results don't cover an area, note it as "No data found."
Be factual and cite sources where possible."""


async def news_scanner_node(state: AgentState) -> dict[str, str]:
    """Search the web for crypto project information and analyze results."""
    user_input = state["input"]
    plan = state.get("plan", "")
    verbose_log("NewsScanner", f"Searching for: {user_input[:80]}")

    try:
        search = DuckDuckGoSearchResults(
            max_results=8,  # type: ignore[call-arg]
            output_format="list",
        )
        current_year = datetime.now(UTC).year
        raw_results = await search.ainvoke(f"{user_input} crypto project news {current_year}")
        verbose_log("NewsScanner", f"Got {len(raw_results) if isinstance(raw_results, list) else '?'} search results")
    except Exception as exc:
        verbose_log("NewsScanner", f"Search failed: {exc}")
        raw_results = f"[Search unavailable: {type(exc).__name__}]"

    try:
        llm = get_chat_model()
        response = await llm.ainvoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(
                    content=(
                        f"Crypto project query: {user_input}\n\n"
                        f"Research plan:\n{plan}\n\n"
                        f"Web search results:\n{raw_results}"
                    )
                ),
            ]
        )
        news = str(response.content)
    except Exception as exc:
        verbose_log("NewsScanner", f"LLM call failed: {exc}")
        news = f"[News analysis failed: {type(exc).__name__}] Raw search data: {raw_results}"

    verbose_log("NewsScanner", f"Analysis complete ({len(news)} chars)")
    return {"news": news}
