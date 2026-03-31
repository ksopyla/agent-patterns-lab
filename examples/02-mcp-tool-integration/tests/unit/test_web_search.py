"""Unit tests for shared web search helpers."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from src.agents import web_search


@pytest.mark.asyncio
async def test_run_search_queries_deduplicates_urls(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_search = AsyncMock()
    mock_search.ainvoke = AsyncMock(
        side_effect=[
            [
                {"title": "Same article", "snippet": "Content", "link": "https://example.com/same"},
                {"title": "Unique article", "snippet": "More", "link": "https://example.com/unique"},
            ],
            [
                {"title": "Same article copy", "snippet": "Content", "link": "https://example.com/same"},
            ],
        ]
    )
    monkeypatch.setattr(web_search, "DuckDuckGoSearchResults", lambda **_: mock_search)

    results = await web_search.run_search_queries(["query one", "query two"], "NewsScanner")

    assert results == [
        {"title": "Same article", "snippet": "Content", "link": "https://example.com/same"},
        {"title": "Unique article", "snippet": "More", "link": "https://example.com/unique"},
    ]


@pytest.mark.asyncio
async def test_run_search_queries_ignores_search_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_search = AsyncMock()
    mock_search.ainvoke = AsyncMock(
        side_effect=[
            RuntimeError("Search API down"),
            [{"title": "Recovered", "snippet": "Working again", "link": "https://example.com/recovered"}],
        ]
    )
    monkeypatch.setattr(web_search, "DuckDuckGoSearchResults", lambda **_: mock_search)

    results = await web_search.run_search_queries(["first", "second"], "CommunityAnalyst")

    assert results == [
        {"title": "Recovered", "snippet": "Working again", "link": "https://example.com/recovered"},
    ]


def test_format_search_results_formats_markdown_list() -> None:
    formatted = web_search.format_search_results(
        [{"title": "Arbitrum news", "snippet": "Orbit chains launched", "link": "https://example.com/1"}]
    )

    assert formatted == "- [Arbitrum news](https://example.com/1): Orbit chains launched"


def test_format_search_results_handles_empty_results() -> None:
    assert web_search.format_search_results([], empty_message="[No social media results found]") == (
        "[No social media results found]"
    )
