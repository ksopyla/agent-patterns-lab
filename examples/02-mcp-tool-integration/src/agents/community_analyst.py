"""Community Analyst agent -- analyzes social media sentiment and community activity.

Reads:  state["project_name"], state["coin_ticker"], state["community_queries"]
Writes: state["community"]

Uses DuckDuckGo with site-restricted queries (reddit.com, twitter/X keywords)
to gauge community sentiment. Does NOT call CoinGecko -- that data source is
owned exclusively by project_profiler. Shared search mechanics live in
src.agents.web_search.
"""

from __future__ import annotations

from datetime import UTC, datetime

from agent_common.llm import get_chat_model
from agent_common.tracing import verbose_log
from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.state import AgentState
from src.agents.web_search import format_search_results, run_search_queries

SYSTEM_PROMPT = """\
You are a crypto community and sentiment analyst. You receive web search results \
focused on social media discussions about a crypto project.

Assess the project's community health:
1. **Reddit sentiment** — what are people saying? Bullish, bearish, skeptical?
2. **X/Twitter buzz** — influencer mentions, trending topics, community debates
3. **Overall retail mood** — is the community growing, stable, or declining?
4. **Red flags** — scam warnings, rug-pull concerns, team complaints, abandonment signals

For each finding, cite the source. Be factual — distinguish between verified \
community activity and speculation.

End with a Community Health Rating: Strong / Moderate / Weak — with a one-sentence \
justification. If data is insufficient, rate as "Insufficient Data" and explain why."""


def _build_queries(project_name: str, ticker: str, community_queries: list[str]) -> list[str]:
    """Build social-focused queries from planner output and fallback templates."""
    if community_queries:
        return community_queries[:4]

    current_year = datetime.now(UTC).year
    return [
        f"{project_name} {ticker} site:reddit.com",
        f"{project_name} crypto twitter sentiment {current_year}",
        f"{project_name} {ticker} community discussion {current_year}",
    ]


async def community_analyst_node(state: AgentState) -> dict[str, str]:
    """Analyze community sentiment using social-focused web searches."""
    project_name = state.get("project_name", state["input"])
    ticker = state.get("coin_ticker", "")
    community_queries = state.get("community_queries", [])
    verbose_log("CommunityAnalyst", f"Analyzing community for: {project_name} ({ticker})")

    queries = _build_queries(project_name, ticker, community_queries)
    verbose_log("CommunityAnalyst", f"Running {len(queries)} social search queries")

    search_results = await run_search_queries(queries, "CommunityAnalyst")
    results_text = format_search_results(
        search_results,
        empty_message="[No social media results found]",
    )

    try:
        llm = get_chat_model()
        response = await llm.ainvoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(
                    content=(f"Project: {project_name} ({ticker})\n\nSocial media search results:\n{results_text}")
                ),
            ]
        )
        community = str(response.content)
    except Exception as exc:
        verbose_log("CommunityAnalyst", f"LLM call failed: {exc}")
        community = f"[Community analysis failed: {type(exc).__name__}]\nRaw data:\n{results_text}"

    verbose_log("CommunityAnalyst", f"Community analysis complete ({len(community)} chars)")
    return {"community": community}
