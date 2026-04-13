"""CoinGecko API client for crypto project data.

Direct httpx calls to the free CoinGecko API (no API key required, ~30 req/min).
This is an internal data layer -- not exposed via MCP. The MCP server exposes
the agent pipeline capability, not raw API wrappers.

Includes retry with exponential backoff for transient failures (rate limits,
server errors). Max 3 attempts per call.
"""

from __future__ import annotations

import asyncio
import json

import httpx
from agent_common.tracing import verbose_log

COINGECKO_BASE = "https://api.coingecko.com/api/v3"
_MAX_RETRIES = 3
_BASE_DELAY = 1.0


async def _get(path: str, params: dict[str, str] | None = None) -> dict:  # type: ignore[type-arg]
    """Make a GET request to CoinGecko API with retry and backoff."""
    url = f"{COINGECKO_BASE}{path}"
    last_exc: Exception | None = None

    async with httpx.AsyncClient(timeout=15.0) as client:
        for attempt in range(_MAX_RETRIES):
            try:
                resp = await client.get(url, params=params or {})
                resp.raise_for_status()
                return resp.json()  # type: ignore[no-any-return]
            except (httpx.HTTPStatusError, httpx.ConnectError, httpx.ReadTimeout) as exc:
                last_exc = exc
                is_client_error = (
                    isinstance(exc, httpx.HTTPStatusError)
                    and exc.response.status_code < 500
                    and exc.response.status_code != 429
                )
                if is_client_error:
                    raise
                delay = _BASE_DELAY * (2**attempt)
                verbose_log(
                    "CoinGecko",
                    (
                        f"Request to {path} failed (attempt {attempt + 1}/{_MAX_RETRIES}): "
                        f"{exc!r} — retrying in {delay:.1f}s"
                    ),
                )
                await asyncio.sleep(delay)

    assert last_exc is not None
    raise last_exc


async def search_coins(query: str) -> str:
    """Search for cryptocurrency projects by name or symbol."""
    data = await _get("/search", {"query": query})
    coins = data.get("coins", [])[:8]
    results = [
        {"id": c["id"], "name": c["name"], "symbol": c["symbol"], "market_cap_rank": c.get("market_cap_rank")}
        for c in coins
    ]
    verbose_log("CoinGecko", f"search_coins({query!r}) → {len(results)} results")
    return json.dumps(results, indent=2)


async def get_coin_info(coin_id: str) -> str:
    """Get detailed project info: description, categories, links, community/developer stats."""
    data = await _get(
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
    verbose_log("CoinGecko", f"get_coin_info({coin_id!r}) → {info.get('name')}")
    return json.dumps(info, indent=2, default=str)


async def get_coin_price(coin_id: str, vs_currency: str = "usd") -> str:
    """Get current price, market cap, volume, and 24h change."""
    data = await _get(
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
    verbose_log("CoinGecko", f"get_coin_price({coin_id!r}) → ${price_info.get('price')}")
    return json.dumps(price_info, indent=2)
