"""Project Profiler agent -- gathers project fundamentals via MCP tools.

This agent uses the crypto-data MCP server to get structured project information
from CoinGecko, demonstrating MCP-based tool access.
"""

from __future__ import annotations

from agent_common.llm import get_chat_model
from agent_common.tracing import verbose_log
from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.state import AgentState
from src.mcp_setup import get_mcp_tool

SYSTEM_PROMPT = """\
You are a crypto project profiler. You receive structured data from CoinGecko
about a crypto project (info and current price).

Create a concise project profile covering:
- What the project does (technology, use case)
- Key stats: market cap, current price, 24h change
- Project maturity: genesis date, development activity
- Category positioning and notable links

Be factual and quantitative where possible."""


async def project_profiler_node(state: AgentState) -> dict[str, str]:
    """Gather project fundamentals using MCP crypto-data tools."""
    user_input = state["input"]
    verbose_log("ProjectProfiler", f"Profiling: {user_input[:80]}")

    search_tool = get_mcp_tool("search_coins")
    search_results = await search_tool.ainvoke({"query": user_input})
    verbose_log("ProjectProfiler", f"Coin search returned: {str(search_results)[:200]}")

    import json

    coins = json.loads(search_results) if isinstance(search_results, str) else search_results
    coin_id = coins[0]["id"] if coins else user_input.lower().replace(" ", "-")

    info_tool = get_mcp_tool("get_coin_info")
    price_tool = get_mcp_tool("get_coin_price")

    coin_info = await info_tool.ainvoke({"coin_id": coin_id})
    coin_price = await price_tool.ainvoke({"coin_id": coin_id})
    verbose_log("ProjectProfiler", "Got coin info and price data via MCP")

    llm = get_chat_model()
    response = await llm.ainvoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"Project query: {user_input}\n\n"
                    f"CoinGecko project info:\n{coin_info}\n\n"
                    f"Current price data:\n{coin_price}"
                )
            ),
        ]
    )

    profile = str(response.content)
    verbose_log("ProjectProfiler", f"Profile complete ({len(profile)} chars)")

    return {"profile": profile}
