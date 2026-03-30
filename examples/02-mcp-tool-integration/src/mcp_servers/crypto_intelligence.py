"""MCP server exposing the crypto intelligence agent pipeline as a tool.

This is the Software 3.0 entry point: instead of a REST endpoint, the agent
exposes its capability via MCP. Any MCP client (Claude Desktop, Cursor,
Claude Code) can call `research_crypto_project` and get a full intelligence
report -- the same result as POST /run, through a standard protocol.

Run standalone: python -m src.mcp_servers.crypto_intelligence
"""

from __future__ import annotations

from agent_common.tracing import setup_tracing, verbose_log
from mcp.server.fastmcp import FastMCP

from src.agents.graph import build_graph

setup_tracing()

mcp = FastMCP(
    "crypto-intelligence",
    host="0.0.0.0",
    port=8000,
)
app = mcp.sse_app()

_graph = build_graph()


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
    verbose_log("MCP", f"research_crypto_project({query!r:.80}) -- starting pipeline")

    result = await _graph.ainvoke({"input": query})

    report: str = result.get("report", "")
    verbose_log("MCP", f"research_crypto_project -- complete ({len(report)} chars)")

    return report


if __name__ == "__main__":
    mcp.run(transport="sse")
