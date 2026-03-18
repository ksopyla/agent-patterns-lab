"""MCP server exposing CoinGecko crypto data as tools.

Run standalone: python -m src.mcp_servers.crypto_data
Connects to the free CoinGecko API (no API key required, rate-limited ~30 req/min).
"""

from __future__ import annotations

import json
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

COINGECKO_BASE = "https://api.coingecko.com/api/v3"

mcp = FastMCP(
    "crypto-data",
    host="0.0.0.0",
    port=8000,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=["127.0.0.1:*", "localhost:*", "crypto-data-mcp:*"],
    ),
)
app = mcp.sse_app()


async def _coingecko_get(path: str, params: dict[str, str] | None = None) -> Any:
    """Make a GET request to CoinGecko API."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(f"{COINGECKO_BASE}{path}", params=params or {})
        resp.raise_for_status()
        return resp.json()  # noqa: ANN401


@mcp.tool()
async def search_coins(query: str) -> str:
    """Search for cryptocurrency projects by name or symbol.

    Returns a list of matching coins with their IDs (use the ID for other tools).
    """
    data = await _coingecko_get("/search", {"query": query})
    coins = data.get("coins", [])[:8]
    results = [
        {"id": c["id"], "name": c["name"], "symbol": c["symbol"], "market_cap_rank": c.get("market_cap_rank")}
        for c in coins
    ]
    return json.dumps(results, indent=2)


@mcp.tool()
async def get_coin_info(coin_id: str) -> str:
    """Get detailed information about a cryptocurrency project.

    Returns: name, symbol, description, categories, links, genesis date,
    and developer/community stats. Use the coin ID from search_coins.
    """
    data = await _coingecko_get(
        f"/coins/{coin_id}",
        {"localization": "false", "tickers": "false", "market_data": "false", "community_data": "true"},
    )
    info = {
        "name": data.get("name"),
        "symbol": data.get("symbol"),
        "description": (data.get("description", {}).get("en", ""))[:1500],
        "categories": data.get("categories", []),
        "genesis_date": data.get("genesis_date"),
        "homepage": data.get("links", {}).get("homepage", [None])[0],
        "github": data.get("links", {}).get("repos_url", {}).get("github", []),
        "twitter": data.get("links", {}).get("twitter_screen_name"),
        "community_data": data.get("community_data", {}),
        "developer_data": {
            k: v for k, v in data.get("developer_data", {}).items() if isinstance(v, (int, float)) and v > 0
        },
    }
    return json.dumps(info, indent=2, default=str)


@mcp.tool()
async def get_coin_price(coin_id: str, vs_currency: str = "usd") -> str:
    """Get current price, market cap, volume, and 24h change for a cryptocurrency.

    Use the coin ID from search_coins (e.g., 'bitcoin', 'ethereum', 'arbitrum').
    """
    data = await _coingecko_get(
        "/simple/price",
        {
            "ids": coin_id,
            "vs_currencies": vs_currency,
            "include_market_cap": "true",
            "include_24hr_vol": "true",
            "include_24hr_change": "true",
        },
    )
    coin_data = data.get(coin_id, {})
    price_info = {
        "coin_id": coin_id,
        "currency": vs_currency,
        "price": coin_data.get(vs_currency),
        "market_cap": coin_data.get(f"{vs_currency}_market_cap"),
        "volume_24h": coin_data.get(f"{vs_currency}_24h_vol"),
        "change_24h_pct": coin_data.get(f"{vs_currency}_24h_change"),
    }
    return json.dumps(price_info, indent=2)


if __name__ == "__main__":
    mcp.run(transport="sse")
