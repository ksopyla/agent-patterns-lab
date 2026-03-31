"""Shared runtime configuration for public pipeline entry points."""

from __future__ import annotations

from typing import cast

from agent_common.tracing import build_langsmith_run_config
from langchain_core.runnables import RunnableConfig

PIPELINE_TIMEOUT_SECONDS = 120.0


def build_pipeline_run_config() -> RunnableConfig:
    """Build trace metadata for public pipeline invocations."""
    return cast(
        RunnableConfig,
        build_langsmith_run_config(
            example_name="02-mcp-tool-integration",
            pattern_slug="mcp-tool-integration",
            run_name="pattern-02-mcp-tool-integration",
        ),
    )
