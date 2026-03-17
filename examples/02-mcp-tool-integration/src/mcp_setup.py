"""MCP client lifecycle management.

Initializes connections to MCP servers at startup and provides tool access to agents.
"""

from __future__ import annotations

import os
from typing import Any

from agent_common.tracing import verbose_log
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

_mcp_client: MultiServerMCPClient | None = None
_mcp_tools: dict[str, BaseTool] = {}


def _get_mcp_config() -> dict[str, dict[str, Any]]:
    crypto_data_url = os.environ.get("CRYPTO_DATA_MCP_URL", "http://localhost:8001/sse")
    return {
        "crypto-data": {
            "url": crypto_data_url,
            "transport": "sse",
        },
    }


async def init_mcp() -> None:
    """Connect to all MCP servers and load available tools."""
    global _mcp_client, _mcp_tools  # noqa: PLW0603
    config = _get_mcp_config()
    verbose_log("MCP", f"Connecting to MCP servers: {list(config.keys())}")

    client: MultiServerMCPClient = MultiServerMCPClient(config)  # type: ignore[arg-type]
    _mcp_client = await client.__aenter__()
    tools: list[BaseTool] = _mcp_client.get_tools()  # type: ignore[misc]
    _mcp_tools = {t.name: t for t in tools}
    verbose_log("MCP", f"Loaded {len(_mcp_tools)} tools: {list(_mcp_tools.keys())}")


async def close_mcp() -> None:
    """Disconnect from all MCP servers."""
    global _mcp_client, _mcp_tools  # noqa: PLW0603
    if _mcp_client:
        await _mcp_client.__aexit__(None, None, None)
        _mcp_client = None
        _mcp_tools = {}
        verbose_log("MCP", "Disconnected from MCP servers")


def get_mcp_tool(name: str) -> BaseTool:
    """Get an MCP tool by name. Raises KeyError if not found."""
    if name not in _mcp_tools:
        available = list(_mcp_tools.keys())
        msg = f"MCP tool '{name}' not found. Available: {available}"
        raise KeyError(msg)
    return _mcp_tools[name]


def get_all_mcp_tools() -> list[BaseTool]:
    """Get all available MCP tools."""
    return list(_mcp_tools.values())
