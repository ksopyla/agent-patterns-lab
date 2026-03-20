"""Pytest configuration for example 01 tests."""

from __future__ import annotations

import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from agent_common.config import get_settings

EXAMPLE_ROOT = Path(__file__).resolve().parents[1]

for key in list(sys.modules.keys()):
    if key == "src" or key.startswith("src."):
        mod = sys.modules[key]
        mod_file = getattr(mod, "__file__", None) or ""
        if mod_file and str(EXAMPLE_ROOT) not in mod_file:
            del sys.modules[key]

if str(EXAMPLE_ROOT) not in sys.path:
    sys.path.insert(0, str(EXAMPLE_ROOT))


@pytest.fixture(autouse=True)
def _disable_langsmith_tracing(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Keep tests local and deterministic even if the host has LangSmith configured."""
    monkeypatch.setenv("LANGSMITH_TRACING", "false")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGCHAIN_API_KEY", raising=False)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
