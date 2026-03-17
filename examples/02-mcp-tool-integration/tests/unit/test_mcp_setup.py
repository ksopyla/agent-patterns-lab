"""Unit tests for MCP client lifecycle management."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.tools import BaseTool
from src import mcp_setup


@pytest.fixture(autouse=True)
def _reset_mcp_globals() -> None:
    """Reset module-level state before each test."""
    mcp_setup._mcp_client = None
    mcp_setup._mcp_tools = {}


def _make_fake_tool(name: str) -> MagicMock:
    tool = MagicMock(spec=BaseTool)
    tool.name = name
    return tool


@pytest.mark.asyncio
async def test_init_mcp_enters_async_context_manager() -> None:
    fake_tools: list[BaseTool] = [_make_fake_tool("search_coins"), _make_fake_tool("get_coin_price")]

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.get_tools = AsyncMock(return_value=fake_tools)

    with patch.object(mcp_setup, "MultiServerMCPClient", return_value=mock_client):
        await mcp_setup.init_mcp()

    mock_client.__aenter__.assert_awaited_once()
    mock_client.get_tools.assert_called_once()
    assert mcp_setup._mcp_client is mock_client
    assert set(mcp_setup._mcp_tools.keys()) == {"search_coins", "get_coin_price"}


@pytest.mark.asyncio
async def test_close_mcp_calls_aexit() -> None:
    mock_client = AsyncMock()
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mcp_setup._mcp_client = mock_client

    await mcp_setup.close_mcp()

    mock_client.__aexit__.assert_awaited_once_with(None, None, None)
    assert mcp_setup._mcp_client is None
    assert mcp_setup._mcp_tools == {}


@pytest.mark.asyncio
async def test_close_mcp_noop_when_no_client() -> None:
    assert mcp_setup._mcp_client is None
    await mcp_setup.close_mcp()
    assert mcp_setup._mcp_client is None


def test_get_mcp_tool_returns_tool() -> None:
    tool = _make_fake_tool("search_coins")
    mcp_setup._mcp_tools = {"search_coins": tool}

    result = mcp_setup.get_mcp_tool("search_coins")
    assert result is tool


def test_get_mcp_tool_raises_on_missing() -> None:
    mcp_setup._mcp_tools = {"search_coins": _make_fake_tool("search_coins")}

    with pytest.raises(KeyError, match="get_coin_price"):
        mcp_setup.get_mcp_tool("get_coin_price")


def test_get_all_mcp_tools_returns_list() -> None:
    tools = [_make_fake_tool("a"), _make_fake_tool("b")]
    mcp_setup._mcp_tools = {t.name: t for t in tools}

    result = mcp_setup.get_all_mcp_tools()
    assert len(result) == 2
    assert set(t.name for t in result) == {"a", "b"}
