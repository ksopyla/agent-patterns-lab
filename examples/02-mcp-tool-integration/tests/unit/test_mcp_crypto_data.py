"""Unit tests for the crypto-intelligence MCP server tools."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest
from src.mcp_servers.crypto_intelligence import get_coin_info, get_coin_price, search_coins


@pytest.mark.asyncio
async def test_search_coins_returns_formatted_results() -> None:
    mock_response = {
        "coins": [
            {"id": "arbitrum", "name": "Arbitrum", "symbol": "ARB", "market_cap_rank": 35},
            {"id": "ethereum", "name": "Ethereum", "symbol": "ETH", "market_cap_rank": 2},
        ]
    }
    with patch(
        "src.mcp_servers.crypto_intelligence._coingecko_get",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        result = await search_coins("arbitrum")

    data = json.loads(result)
    assert len(data) == 2
    assert data[0]["id"] == "arbitrum"
    assert data[0]["symbol"] == "ARB"


@pytest.mark.asyncio
async def test_get_coin_info_extracts_key_fields() -> None:
    mock_response = {
        "name": "Arbitrum",
        "symbol": "arb",
        "description": {"en": "Arbitrum is a Layer 2 optimistic rollup."},
        "categories": ["Layer 2", "Ethereum Ecosystem"],
        "genesis_date": "2023-03-23",
        "links": {
            "homepage": ["https://arbitrum.io"],
            "repos_url": {"github": ["https://github.com/OffchainLabs/nitro"]},
            "twitter_screen_name": "arbitrum",
        },
        "community_data": {"twitter_followers": 500000},
        "developer_data": {"commits_4_weeks": 120, "forks": 350, "stars": 8000, "pull_request_contributors": 0},
    }
    with patch(
        "src.mcp_servers.crypto_intelligence._coingecko_get",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        result = await get_coin_info("arbitrum")

    data = json.loads(result)
    assert data["name"] == "Arbitrum"
    assert "Layer 2" in data["categories"]
    assert data["twitter"] == "arbitrum"
    assert data["developer_data"]["commits_4_weeks"] == 120
    assert "pull_request_contributors" not in data["developer_data"]


@pytest.mark.asyncio
async def test_get_coin_price_returns_market_data() -> None:
    mock_response = {
        "arbitrum": {
            "usd": 1.23,
            "usd_market_cap": 4500000000,
            "usd_24h_vol": 350000000,
            "usd_24h_change": 5.67,
        }
    }
    with patch(
        "src.mcp_servers.crypto_intelligence._coingecko_get",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        result = await get_coin_price("arbitrum")

    data = json.loads(result)
    assert data["price"] == 1.23
    assert data["market_cap"] == 4500000000
    assert data["change_24h_pct"] == 5.67
