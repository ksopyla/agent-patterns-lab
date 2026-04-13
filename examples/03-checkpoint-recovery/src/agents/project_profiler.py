"""Project Profiler agent -- gathers project fundamentals from CoinGecko.

Reads:  state["project_name"], state["coin_ticker"], state["coin_id"]
Writes: state["profile"]

Owns ALL CoinGecko data: market stats, price, categories, description,
genesis date, homepage, AND developer_data (GitHub stats from CoinGecko).
Pattern 03 prefers the planner-verified `coin_id` when available so resumed
threads do not need to repeat ambiguous project resolution.
"""

from __future__ import annotations

import json

from agent_common.llm import get_chat_model
from agent_common.tracing import verbose_log
from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.state import AgentState
from src.coingecko import get_coin_info, get_coin_price, search_coins

SYSTEM_PROMPT = """\
You are a crypto project profiler. You receive structured data from CoinGecko.

Create a concise project profile covering:
1. **Project overview** — what it does, technology, use case
2. **Market data** — current price, market cap, 24h volume, 24h change percentage
3. **Project maturity** — genesis date, categories, notable links (homepage, GitHub)
4. **Developer activity** — GitHub stars, forks, contributors, recent commits, \
merged PRs (from developer_data)
5. **Exchanges & liquidity** — where it trades (if available)

Be factual and quantitative. If a data field is missing or unavailable, \
state "Data not available" — do NOT guess or hallucinate numbers."""


async def _resolve_coin_id(project_name: str, ticker: str, preferred_coin_id: str = "") -> str:
    """Find the CoinGecko coin ID using the planner-verified value first."""
    if preferred_coin_id:
        verbose_log("ProjectProfiler", f"Using planner-verified coin_id={preferred_coin_id!r}")
        return preferred_coin_id

    for query in [project_name, ticker]:
        if not query:
            continue
        try:
            search_results = await search_coins(query)
            coins = json.loads(search_results) if search_results else []
            if coins:
                coin_id: str = str(coins[0]["id"])
                verbose_log(
                    "ProjectProfiler",
                    f"Resolved {query!r} → coin_id={coin_id!r}",
                )
                return coin_id
        except Exception as exc:
            verbose_log("ProjectProfiler", f"Search for {query!r} failed: {exc}")

    fallback = project_name.lower().replace(" ", "-")
    verbose_log("ProjectProfiler", f"Using fallback coin_id={fallback!r}")
    return fallback


async def project_profiler_node(state: AgentState) -> dict[str, str]:
    """Gather project fundamentals from CoinGecko."""
    project_name = state.get("project_name", state["input"])
    ticker = state.get("coin_ticker", "")
    preferred_coin_id = state.get("coin_id", "")
    verbose_log("ProjectProfiler", f"Profiling: {project_name} ({ticker})")

    coin_id = await _resolve_coin_id(project_name, ticker, preferred_coin_id)

    coin_info: str
    coin_price: str
    try:
        coin_info = await get_coin_info(coin_id)
        verbose_log("ProjectProfiler", "Got coin info (includes developer_data)")
    except Exception as exc:
        verbose_log("ProjectProfiler", f"get_coin_info failed: {exc}")
        coin_info = f"[Project data unavailable: {type(exc).__name__}]"

    try:
        coin_price = await get_coin_price(coin_id)
        verbose_log("ProjectProfiler", "Got price data")
    except Exception as exc:
        verbose_log("ProjectProfiler", f"get_coin_price failed: {exc}")
        coin_price = "[Price data unavailable]"

    try:
        llm = get_chat_model()
        response = await llm.ainvoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(
                    content=(
                        f"Project: {project_name} ({ticker})\n\n"
                        f"CoinGecko project info (includes developer_data):\n{coin_info}\n\n"
                        f"Current price data:\n{coin_price}"
                    )
                ),
            ]
        )
        profile = str(response.content)
    except Exception as exc:
        verbose_log("ProjectProfiler", f"LLM call failed: {exc}")
        profile = f"[Profile generation failed: {type(exc).__name__}]\nRaw info: {coin_info}\nRaw price: {coin_price}"

    verbose_log("ProjectProfiler", f"Profile complete ({len(profile)} chars)")
    return {"profile": profile}
