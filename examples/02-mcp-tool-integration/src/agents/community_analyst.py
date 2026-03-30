"""Community Analyst agent -- analyzes social media sentiment and community activity.

Reads:  state["project_name"], state["coin_ticker"], state["plan"]
Writes: state["community"]

Uses DuckDuckGo with site-restricted queries (reddit.com, twitter/X keywords)
to gauge community sentiment. Does NOT call CoinGecko -- that data source is
owned exclusively by project_profiler.
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


def _extract_plan_queries(plan: str) -> list[str]:
    """Pull queries from the COMMUNITY_QUERIES: section of the research plan."""
    match = re.search(
        r"COMMUNITY_QUERIES:\s*\n(.*?)(?:\n\s*\n|\Z)",
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
    """Build social-focused search queries from plan and fallback templates."""
    plan_queries = _extract_plan_queries(plan)
    if plan_queries:
        return plan_queries[:4]

    current_year = datetime.now(UTC).year
    return [
        f"{project_name} {ticker} site:reddit.com",
        f"{project_name} crypto twitter sentiment {current_year}",
        f"{project_name} {ticker} community discussion {current_year}",
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


async def community_analyst_node(state: AgentState) -> dict[str, str]:
    """Analyze community sentiment using social-focused web searches."""
    project_name = state.get("project_name", state["input"])
    ticker = state.get("coin_ticker", "")
    plan = state.get("plan", "")
    verbose_log("CommunityAnalyst", f"Analyzing community for: {project_name} ({ticker})")

    queries = _build_queries(project_name, ticker, plan)
    verbose_log("CommunityAnalyst", f"Running {len(queries)} social search queries")

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
                verbose_log("CommunityAnalyst", f"  [{query[:50]}] → {len(raw)} results")
        except Exception as exc:
            verbose_log("CommunityAnalyst", f"  [{query[:50]}] search failed: {exc}")

    unique_results = _deduplicate_results(all_results)
    verbose_log(
        "CommunityAnalyst",
        f"Total: {len(all_results)} raw → {len(unique_results)} unique results",
    )

    results_text = (
        "\n".join(f"- [{r.get('title', 'N/A')}]({r.get('link', '')}): {r.get('snippet', '')}" for r in unique_results)
        or "[No social media results found]"
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
