"""Planner and project-selection nodes for Pattern 03.

`research_planner_node` is intentionally limited to deterministic state updates
that can be checkpointed before any human interaction:
- Reads:  state["input"]
- Writes: state["plan"], state["project_name"], state["coin_ticker"],
          state["news_queries"], state["community_queries"]

`project_verifier_node` resolves the CoinGecko project using the planner's
structured output and stores either a verified `coin_id` or an
`ambiguous_matches` shortlist.

`project_selector_node` owns the actual `interrupt()` call. Because it reads
only persisted state instead of re-running the LLM planner, a resumed thread
can reliably apply the user's selected `coin_id`.
"""

from __future__ import annotations

import json
from typing import Any

from agent_common.llm import get_chat_model
from agent_common.tracing import verbose_log
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import interrupt
from pydantic import BaseModel, Field

from src.agents.state import AgentState, CoinMatch
from src.coingecko import search_coins

SYSTEM_PROMPT = """\
You are a crypto project research planner. Given a user query, do three things:

1. **Identify the project** with its official project name and ticker symbol.
2. **Create a focused research plan** (numbered list, one sentence per area):
   a. Recent news, announcements, partnerships, events — positive and negative signals.
   b. Project fundamentals via CoinGecko: market cap, price, volume, exchanges, \
team, genesis date, categories.
   c. Community and social sentiment: X/Twitter buzz, Reddit discussions, \
Telegram activity, overall retail mood.
3. **Generate tailored search queries** for downstream research agents:
   - 3-4 news queries optimized for recent partnerships, announcements, and project updates
   - 3-4 community queries optimized for Reddit, X/Twitter, and social sentiment

Keep the plan concise and actionable. Do NOT include price predictions."""


class ResearchPlan(BaseModel):
    """Structured planner output used by downstream research nodes."""

    project_name: str = Field(description="Official project name")
    coin_ticker: str = Field(description="Ticker symbol in uppercase, for example ETH or SOL")
    plan: str = Field(description="Concise numbered research plan covering news, fundamentals, and community")
    news_queries: list[str] = Field(description="Three to four targeted web search queries for recent project news")
    community_queries: list[str] = Field(
        description="Three to four targeted web search queries for community and social sentiment"
    )


def _normalize(value: str) -> str:
    return value.strip().lower()


def _parse_coin_matches(raw_results: str) -> list[CoinMatch]:
    """Convert CoinGecko search JSON into typed, compact match objects."""
    try:
        parsed = json.loads(raw_results) if raw_results else []
    except json.JSONDecodeError:
        return []

    matches: list[CoinMatch] = []
    for item in parsed[:5]:
        coin_id = str(item.get("id", "")).strip()
        name = str(item.get("name", "")).strip()
        symbol = str(item.get("symbol", "")).strip().upper()
        market_cap_rank_raw = item.get("market_cap_rank")
        market_cap_rank = market_cap_rank_raw if isinstance(market_cap_rank_raw, int) else None
        if coin_id and name:
            matches.append(
                {
                    "coin_id": coin_id,
                    "name": name,
                    "symbol": symbol,
                    "market_cap_rank": market_cap_rank,
                }
            )
    return matches


def _deduplicate_matches(matches: list[CoinMatch]) -> list[CoinMatch]:
    """Preserve order while removing duplicate coin IDs."""
    seen_coin_ids: set[str] = set()
    unique_matches: list[CoinMatch] = []
    for match in matches:
        coin_id = match["coin_id"]
        if coin_id not in seen_coin_ids:
            seen_coin_ids.add(coin_id)
            unique_matches.append(match)
    return unique_matches


def _select_matches(
    project_name: str, coin_ticker: str, matches: list[CoinMatch]
) -> tuple[CoinMatch | None, list[CoinMatch]]:
    """Pick a confident CoinGecko match or return a shortlist for human review."""
    normalized_project = _normalize(project_name)
    normalized_ticker = _normalize(coin_ticker)

    exact_name_matches = [match for match in matches if _normalize(match["name"]) == normalized_project]
    exact_symbol_matches = [
        match for match in matches if normalized_ticker and _normalize(match["symbol"]) == normalized_ticker
    ]

    if exact_name_matches and exact_symbol_matches:
        overlapping_ids = {match["coin_id"] for match in exact_name_matches} & {
            match["coin_id"] for match in exact_symbol_matches
        }
        if len(overlapping_ids) == 1:
            selected_coin_id = next(iter(overlapping_ids))
            selected = next(match for match in matches if match["coin_id"] == selected_coin_id)
            return selected, []

    if len(exact_name_matches) == 1 and not exact_symbol_matches:
        return exact_name_matches[0], []

    if len(exact_symbol_matches) == 1 and not exact_name_matches:
        return exact_symbol_matches[0], []

    candidates = _deduplicate_matches(exact_name_matches + exact_symbol_matches)
    if not candidates:
        candidates = matches[:3]

    if len(candidates) == 1:
        return candidates[0], []

    if len(candidates) > 1:
        return None, candidates

    return None, []


async def _verify_project(project_name: str, coin_ticker: str) -> tuple[str, list[CoinMatch]]:
    """Resolve the intended CoinGecko project without triggering interrupts."""
    try:
        raw_results = await search_coins(project_name)
    except Exception as exc:
        verbose_log("ProjectVerifier", f"CoinGecko verification failed: {exc}")
        return "", []

    matches = _parse_coin_matches(raw_results)
    if not matches:
        verbose_log("ProjectVerifier", "CoinGecko returned no matches; continuing without verified coin_id")
        return "", []

    selected, ambiguous_matches = _select_matches(project_name, coin_ticker, matches)
    if selected is not None:
        verbose_log("ProjectVerifier", f"Verified coin_id={selected['coin_id']!r} automatically")
        return selected["coin_id"], []

    if ambiguous_matches:
        verbose_log(
            "ProjectVerifier",
            f"Project is ambiguous; waiting for human selection across {len(ambiguous_matches)} matches",
        )
        return "", ambiguous_matches

    return "", []


async def research_planner_node(state: AgentState) -> dict[str, Any]:
    """Create a structured research plan without performing human interrupts."""
    user_input = state["input"]
    verbose_log("ResearchPlanner", f"Planning research for: {user_input[:100]}")

    llm = get_chat_model().with_structured_output(ResearchPlan)
    result = await llm.ainvoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_input),
        ]
    )

    project_name = result.project_name.strip() or user_input.strip()
    coin_ticker = result.coin_ticker.strip().upper()
    news_queries = [query.strip() for query in result.news_queries if query.strip()]
    community_queries = [query.strip() for query in result.community_queries if query.strip()]

    verbose_log(
        "ResearchPlanner",
        (
            f"Identified project={project_name!r}, ticker={coin_ticker!r}, "
            f"news_queries={len(news_queries)}, community_queries={len(community_queries)}"
        ),
    )

    return {
        "plan": result.plan,
        "project_name": project_name,
        "coin_ticker": coin_ticker,
        "news_queries": news_queries,
        "community_queries": community_queries,
    }


async def project_verifier_node(state: AgentState) -> dict[str, Any]:
    """Resolve the intended CoinGecko project from checkpointed planner state."""
    project_name = state.get("project_name", state["input"]).strip()
    coin_ticker = state.get("coin_ticker", "").strip().upper()
    verbose_log("ProjectVerifier", f"Verifying project={project_name!r}, ticker={coin_ticker!r}")

    coin_id, ambiguous_matches = await _verify_project(project_name, coin_ticker)
    return {
        "coin_id": coin_id,
        "ambiguous_matches": ambiguous_matches,
    }


async def project_selector_node(state: AgentState) -> dict[str, Any]:
    """Pause only when the verifier stored ambiguous CoinGecko candidates."""
    matches = state.get("ambiguous_matches", [])
    if not matches:
        verbose_log("ProjectSelector", "No human selection required")
        return {}

    project_name = state.get("project_name", state["input"]).strip()
    coin_ticker = state.get("coin_ticker", "").strip().upper()
    prompt_message = f"Multiple CoinGecko matches found for {project_name}. Choose the correct project to continue."

    while True:
        response = interrupt(
            {
                "interrupt_type": "ambiguous_project",
                "message": prompt_message,
                "project_name": project_name,
                "coin_ticker": coin_ticker,
                "matches": matches,
            }
        )
        selected_coin_id = ""
        if isinstance(response, dict):
            selected_coin_id = str(response.get("selected_coin_id", "")).strip()

        for match in matches:
            if match["coin_id"] == selected_coin_id:
                verbose_log("ProjectSelector", f"Human selected coin_id={selected_coin_id!r}")
                return {
                    "coin_id": selected_coin_id,
                    "ambiguous_matches": [],
                }

        prompt_message = f"Selection {selected_coin_id!r} is not valid. Choose one of the provided CoinGecko coin IDs."
        verbose_log("ProjectSelector", prompt_message)
