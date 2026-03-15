"""LangSmith tracing and verbose logging utilities."""

from __future__ import annotations

import os
import sys
from datetime import UTC, datetime

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


def setup_tracing() -> None:
    """Configure LangSmith tracing from settings.

    Call this once at application startup (e.g., in FastAPI lifespan).
    Sets the environment variables that LangSmith SDK reads.
    """
    settings = get_settings()

    if settings.langsmith_tracing and settings.langsmith_api_key:
        os.environ["LANGSMITH_TRACING"] = "true"
        os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
        os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
        verbose_log("system", f"LangSmith tracing enabled (project: {settings.langsmith_project})")
    elif settings.langsmith_tracing:
        verbose_log("system", "LangSmith tracing requested but LANGSMITH_API_KEY not set")


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
