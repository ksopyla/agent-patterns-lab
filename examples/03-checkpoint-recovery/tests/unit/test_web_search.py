"""Unit tests for the shared DuckDuckGo helper logic."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from src.agents import web_search


def test_deduplicate_results_removes_duplicate_urls() -> None:
    raw_results = [
        {"title": "A", "snippet": "one", "link": "https://example.com/a"},
        {"title": "B", "snippet": "two", "link": "https://example.com/b"},
        {"title": "A duplicate", "snippet": "three", "link": "https://example.com/a"},
    ]

    unique = web_search._deduplicate_results(raw_results)

    assert len(unique) == 2
    assert [item["link"] for item in unique] == [
        "https://example.com/a",
        "https://example.com/b",
    ]


@pytest.mark.asyncio
async def test_run_search_queries_ignores_failed_query(monkeypatch: pytest.MonkeyPatch) -> None:
    search = AsyncMock()
    search.ainvoke = AsyncMock(
        side_effect=[
            [{"title": "A", "snippet": "one", "link": "https://example.com/a"}],
            RuntimeError("search down"),
            [{"title": "B", "snippet": "two", "link": "https://example.com/b"}],
        ]
    )
    monkeypatch.setattr(web_search, "DuckDuckGoSearchResults", lambda **kwargs: search)

    results = await web_search.run_search_queries(
        ["query one", "query two", "query three"],
        "NewsScanner",
    )

    assert len(results) == 2
    assert {item["link"] for item in results} == {
        "https://example.com/a",
        "https://example.com/b",
    }


def test_format_search_results_returns_markdown_list() -> None:
    formatted = web_search.format_search_results(
        [
            {"title": "A", "snippet": "one", "link": "https://example.com/a"},
            {"title": "B", "snippet": "two", "link": "https://example.com/b"},
        ]
    )

    assert "- [A](https://example.com/a): one" in formatted
    assert "- [B](https://example.com/b): two" in formatted


def test_format_search_results_handles_empty_results() -> None:
    assert web_search.format_search_results([]) == "[No results found]"
