"""MCP server exposing the crypto intelligence agent pipeline as a tool.

This is the Software 3.0 entry point: instead of a REST endpoint, the agent
exposes its capability via MCP. Any MCP client (Claude Desktop, Cursor,
Claude Code) can call `research_crypto_project` and get a full intelligence
report -- the same result as POST /run, through a standard protocol.

Run standalone: python -m src.mcp_servers.crypto_intelligence
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from agent_common.tracing import setup_tracing, verbose_log
from mcp.server.fastmcp import FastMCP

from src.agents.graph import build_graph
from src.runtime import PIPELINE_TIMEOUT_SECONDS, build_pipeline_run_config

mcp = FastMCP(
    "crypto-intelligence",
    host="0.0.0.0",
    port=8000,
)
_graph: Any | None = None
_tracing_initialized = False


def _ensure_runtime_initialized() -> Any:
    """Initialize tracing and graph lazily for the MCP server."""
    global _graph, _tracing_initialized

    if not _tracing_initialized:
        setup_tracing()
        _tracing_initialized = True

    if _graph is None:
        _graph = build_graph()
        verbose_log("MCP", "MCP server runtime initialized")

    return _graph


@asynccontextmanager
async def mcp_lifespan(_: object) -> AsyncIterator[None]:
    _ensure_runtime_initialized()
    verbose_log("MCP", "MCP server started")
    yield
    verbose_log("MCP", "MCP server shutting down")


app = mcp.sse_app()
app.router.lifespan_context = mcp_lifespan


@mcp.tool()
async def research_crypto_project(query: str) -> str:
    """Research a cryptocurrency project and produce a structured intelligence report.

    Accepts the same natural-language research queries as the REST API (POST /run).
    Runs a 5-agent pipeline: Research Planner, News Scanner, Project Profiler,
    Community Analyst, and Intelligence Compiler.

    Example queries:
    - "Research the Arbitrum crypto project"
    - "Analyze Solana's recent partnerships and developer activity"
    - "What is Ethereum's community health and market position?"

    Args:
        query: A natural-language research request about a crypto project.

    Returns:
        A structured intelligence report with executive summary, market snapshot,
        key findings, recent developments, community health, risk factors, and outlook.
    """
    graph = _ensure_runtime_initialized()
    preview = repr(query[:80])
    verbose_log("MCP", f"research_crypto_project({preview}) -- starting pipeline")

    try:
        result = await asyncio.wait_for(
            graph.ainvoke(
                {"input": query},
                config=build_pipeline_run_config(),
            ),
            timeout=PIPELINE_TIMEOUT_SECONDS,
        )
    except TimeoutError:
        message = f"Pipeline timed out after {PIPELINE_TIMEOUT_SECONDS:.0f}s"
        verbose_log("MCP", message)
        return f"[Pipeline timeout] {message}"
    except Exception as exc:
        verbose_log("MCP", f"research_crypto_project failed: {exc}")
        return f"[Pipeline failed] {type(exc).__name__}: {exc}"

    report: str = result.get("report", "")
    verbose_log("MCP", f"research_crypto_project -- complete ({len(report)} chars)")
    return report


if __name__ == "__main__":
    mcp.run(transport="sse")
