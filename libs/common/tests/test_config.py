"""Tests for shared environment-backed settings."""

from __future__ import annotations

import pytest
from agent_common.config import get_settings


def test_settings_default_llm_values() -> None:
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.azure_openai_api_version == "2025-01-01-preview"
    assert settings.anthropic_model == "claude-sonnet-4-6"


def test_settings_read_llm_overrides_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-sonnet-override")
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.azure_openai_api_version == "2025-01-01-preview"
    assert settings.anthropic_model == "claude-sonnet-override"

    get_settings.cache_clear()
