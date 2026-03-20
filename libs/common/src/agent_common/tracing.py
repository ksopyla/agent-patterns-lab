"""LangSmith tracing, run config, and verbose logging utilities."""

from __future__ import annotations

import os
import sys
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import Any

from langchain_core.runnables import RunnableConfig

from agent_common.config import get_settings

# ANSI color codes for verbose output
_COLORS = {
    "planner": "\033[94m",  # Blue
    "researcher": "\033[92m",  # Green
    "writer": "\033[93m",  # Yellow
    "orchestrator": "\033[95m",  # Magenta
    "tool": "\033[96m",  # Cyan
    "system": "\033[90m",  # Gray
}
_RESET = "\033[0m"
_BOLD = "\033[1m"


def _detect_environment() -> str:
    """Return a coarse execution environment label for trace filtering."""
    if os.getenv("GITHUB_ACTIONS") == "true" or os.getenv("CI") == "true":
        return "ci"
    return "local"


def _detect_runtime() -> str:
    """Return a runtime label for trace filtering."""
    if os.path.exists("/.dockerenv"):
        return "docker"
    return "local"


def _disable_tracing() -> None:
    """Disable LangSmith tracing and clear stale API key compatibility vars."""
    os.environ["LANGSMITH_TRACING"] = "false"
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    os.environ.pop("LANGSMITH_API_KEY", None)
    os.environ.pop("LANGCHAIN_API_KEY", None)


def setup_tracing() -> None:
    """Configure LangSmith tracing from settings.

    Call this once at application startup (e.g., in FastAPI lifespan).
    Sets the environment variables that LangSmith SDK reads.
    """
    settings = get_settings()

    if settings.langsmith_tracing and settings.langsmith_api_key:
        os.environ["LANGSMITH_TRACING"] = "true"
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
        os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
        os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project

        endpoint = os.getenv("LANGSMITH_ENDPOINT")
        if endpoint:
            os.environ["LANGCHAIN_ENDPOINT"] = endpoint

        verbose_log("system", f"LangSmith tracing enabled (project: {settings.langsmith_project})")
    elif settings.langsmith_tracing:
        _disable_tracing()
        verbose_log("system", "LangSmith tracing requested but LANGSMITH_API_KEY not set; tracing disabled")
    else:
        _disable_tracing()


def build_langsmith_run_config(
    *,
    example_name: str,
    pattern_slug: str,
    run_name: str,
    extra_tags: Sequence[str] | None = None,
    metadata: Mapping[str, Any] | None = None,
    environment: str | None = None,
    runtime: str | None = None,
) -> RunnableConfig:
    """Build a consistent LangSmith run config for example graph invocations."""
    settings = get_settings()
    resolved_environment = environment or _detect_environment()
    resolved_runtime = runtime or _detect_runtime()

    tags = [
        f"example:{example_name}",
        f"pattern:{pattern_slug}",
        f"env:{resolved_environment}",
        f"runtime:{resolved_runtime}",
        f"provider:{settings.llm_provider}",
    ]
    if extra_tags:
        tags.extend(extra_tags)

    run_metadata: dict[str, Any] = {
        "example_name": example_name,
        "pattern_slug": pattern_slug,
        "environment": resolved_environment,
        "runtime": resolved_runtime,
        "llm_provider": settings.llm_provider,
        "langsmith_project": settings.langsmith_project,
    }
    if metadata:
        run_metadata.update(metadata)

    return {
        "run_name": run_name,
        "tags": tags,
        "metadata": run_metadata,
    }


def verbose_log(agent_name: str, message: str, data: object | None = None) -> None:
    """Log a message with agent name and timestamp when VERBOSE=true.

    Args:
        agent_name: Name of the agent or component producing the log.
        message: Human-readable log message.
        data: Optional structured data to include (tool inputs/outputs, payloads).
    """
    settings = get_settings()
    if not settings.verbose:
        return

    now = datetime.now(UTC).strftime("%H:%M:%S.%f")[:-3]
    color = _COLORS.get(agent_name.lower(), "\033[97m")
    prefix = f"{_BOLD}{color}[{now}] [{agent_name}]{_RESET}"

    print(f"{prefix} {message}", file=sys.stderr)
    if data is not None:
        print(f"{prefix}   └─ {data}", file=sys.stderr)
