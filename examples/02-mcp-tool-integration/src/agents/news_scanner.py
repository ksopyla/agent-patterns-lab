"""News Scanner agent -- searches the web for recent news about a crypto project.

Uses DuckDuckGo web search directly (not through MCP). This agent demonstrates
that MCP and direct tools can coexist -- Pattern 02 introduces MCP for new
capabilities while keeping existing integrations.
"""

from __future__ import annotations

from agent_common.llm import get_chat_model
from agent_common.tracing import verbose_log
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.state import AgentState

SYSTEM_PROMPT = """\
You are a crypto news analyst. You receive raw web search results about a crypto project.

Extract and organize the most relevant recent information:
- Key news and announcements (with approximate dates if available)
- Partnership or integration announcements
- Regulatory or legal developments
- Notable community reactions or events

Be factual. Note which claims are well-sourced vs. speculative."""


async def news_scanner_node(state: AgentState) -> dict[str, str]:
    """Search the web for crypto project news and analyze results."""
    user_input = state["input"]
    verbose_log("NewsScanner", f"Searching for: {user_input[:80]}")

    search = DuckDuckGoSearchResults(max_results=8, output_format="list")
    raw_results = await search.ainvoke(f"{user_input} crypto project latest news 2026")
    verbose_log("NewsScanner", f"Got {len(raw_results) if isinstance(raw_results, list) else '?'} search results")

    llm = get_chat_model()
    response = await llm.ainvoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Crypto project: {user_input}\n\nWeb search results:\n{raw_results}"),
        ]
    )

    news = str(response.content)
    verbose_log("NewsScanner", f"News analysis complete ({len(news)} chars)")

    return {"news": news}
