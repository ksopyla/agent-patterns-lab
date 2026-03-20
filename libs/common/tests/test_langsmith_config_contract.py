"""Contract tests for the shared LangSmith configuration helpers.

This module is intentionally narrow.

It exists to protect two repository-level behaviors implemented in
`agent_common.tracing`:

1. If tracing is requested without a usable API key, the shared setup helper
   must disable tracing and clear stale compatibility variables. This prevents
   accidental live ingest attempts during local development, Docker runs, or
   tests.
2. Public example entrypoints should be able to build a stable LangSmith run
   config while reusing one shared `LANGSMITH_PROJECT`. We separate examples by
   tags and metadata rather than by introducing extra per-example environment
   variables.

What this module is not for:
- It is not a live LangSmith integration test.
- It should not make network calls.
- It should not accumulate unrelated logging, tracing, or SDK behavior tests.

If future tracing behavior is added, prefer either extending these contract
tests only when the repository-level contract changes, or creating a separate
test module with a more specific name.
"""

from __future__ import annotations

import os

import pytest
from agent_common.config import get_settings
from agent_common.tracing import build_langsmith_run_config, setup_tracing


@pytest.fixture(autouse=True)
def _reset_settings_cache() -> None:
    """Ensure each test observes only its own environment overrides."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_setup_tracing_disables_tracing_when_key_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify the shared setup helper fails closed without a usable API key.

    This guards the regression where LangSmith tracing stayed effectively on and
    produced unauthorized ingest noise when configuration was incomplete.
    """
    monkeypatch.setenv("LANGSMITH_TRACING", "true")
    monkeypatch.setenv("LANGSMITH_API_KEY", "")
    monkeypatch.setenv("LANGCHAIN_API_KEY", "stale-key")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "true")

    setup_tracing()

    assert os.environ["LANGSMITH_TRACING"] == "false"
    assert os.environ["LANGCHAIN_TRACING_V2"] == "false"
    assert "LANGSMITH_API_KEY" not in os.environ
    assert "LANGCHAIN_API_KEY" not in os.environ


def test_build_langsmith_run_config_returns_shared_project_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify run config shape for the shared-project tagging convention.

    This checks the repository contract we want examples to follow:
    one shared LangSmith project plus stable per-example tags and metadata for
    filtering by example, environment, runtime, and provider.
    """
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("LANGSMITH_PROJECT", "agent-patterns-lab")

    config = build_langsmith_run_config(
        example_name="01-orchestrator-pipeline",
        pattern_slug="orchestrator-pipeline",
        run_name="pattern-01-orchestrator-pipeline",
        extra_tags=["surface:http"],
        metadata={"entrypoint": "POST /run"},
        environment="local",
        runtime="docker",
    )

    assert config["run_name"] == "pattern-01-orchestrator-pipeline"
    assert config["tags"] == [
        "example:01-orchestrator-pipeline",
        "pattern:orchestrator-pipeline",
        "env:local",
        "runtime:docker",
        "provider:anthropic",
        "surface:http",
    ]
    assert config["metadata"] == {
        "example_name": "01-orchestrator-pipeline",
        "pattern_slug": "orchestrator-pipeline",
        "environment": "local",
        "runtime": "docker",
        "llm_provider": "anthropic",
        "langsmith_project": "agent-patterns-lab",
        "entrypoint": "POST /run",
    }
