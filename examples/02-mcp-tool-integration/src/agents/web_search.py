"""Shared DuckDuckGo search helpers for research agents."""

from __future__ import annotations

from agent_common.tracing import verbose_log
from langchain_community.tools import DuckDuckGoSearchResults


def _deduplicate_results(all_results: list[dict[str, str]]) -> list[dict[str, str]]:
    """Remove duplicate search results by URL."""
    seen_urls: set[str] = set()
    unique_results: list[dict[str, str]] = []

    for item in all_results:
        url = item.get("link", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(item)

    return unique_results


async def run_search_queries(
    queries: list[str],
    agent_name: str,
    max_results: int = 5,
) -> list[dict[str, str]]:
    """Run multiple searches and deduplicate results by URL."""
    all_results: list[dict[str, str]] = []
    search = DuckDuckGoSearchResults(
        max_results=max_results,  # type: ignore[call-arg]
        output_format="list",
    )

    for query in queries:
        try:
            raw = await search.ainvoke(query)
            if isinstance(raw, list):
                all_results.extend(raw)
                verbose_log(agent_name, f"  [{query[:50]}] -> {len(raw)} results")
        except Exception as exc:
            verbose_log(agent_name, f"  [{query[:50]}] search failed: {exc}")

    unique_results = _deduplicate_results(all_results)
    verbose_log(
        agent_name,
        f"Total: {len(all_results)} raw -> {len(unique_results)} unique results",
    )
    return unique_results


def format_search_results(
    results: list[dict[str, str]],
    empty_message: str = "[No results found]",
) -> str:
    """Format search results as a markdown list for LLM consumption."""
    return (
        "\n".join(
            f"- [{item.get('title', 'N/A')}]({item.get('link', '')}): {item.get('snippet', '')}" for item in results
        )
        or empty_message
    )
