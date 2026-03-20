"""Community Analyst agent -- analyzes community and developer activity via MCP.

Uses the crypto-data MCP server to access community/developer stats and
combines with LLM analysis for a community health assessment.
"""

from __future__ import annotations

import json

from agent_common.llm import get_chat_model
from agent_common.tracing import verbose_log
from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.state import AgentState
from src.mcp_setup import get_mcp_tool, mcp_result_to_text, normalize_project_query

SYSTEM_PROMPT = """\
You are a crypto community analyst. You receive community and developer data
about a crypto project from CoinGecko.

Assess the project's community health:
- Developer activity: GitHub commits, contributors, forks, stars
- Community size: Twitter followers, Reddit subscribers, Telegram users
- Activity trends: is the community growing or shrinking?
- Red flags: low developer activity, declining community, etc.

Provide a brief community health rating (Strong / Moderate / Weak) with justification."""


async def community_analyst_node(state: AgentState) -> dict[str, str]:
    """Analyze community and developer activity using MCP tools."""
    user_input = state["input"]
    verbose_log("CommunityAnalyst", f"Analyzing community for: {user_input[:80]}")
    search_query = normalize_project_query(user_input)

    search_tool = get_mcp_tool("search_coins")
    search_results = await search_tool.ainvoke({"query": search_query})
    search_results_text = mcp_result_to_text(search_results)

    coins = json.loads(search_results_text) if search_results_text else []
    coin_id = coins[0]["id"] if coins else search_query.lower().replace(" ", "-")

    info_tool = get_mcp_tool("get_coin_info")
    coin_info = mcp_result_to_text(await info_tool.ainvoke({"coin_id": coin_id}))
    verbose_log("CommunityAnalyst", "Got community/developer data via MCP")

    llm = get_chat_model()
    response = await llm.ainvoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"Project: {user_input}\n\n"
                    f"CoinGecko project data (includes community_data and developer_data):\n{coin_info}"
                )
            ),
        ]
    )

    community = str(response.content)
    verbose_log("CommunityAnalyst", f"Community analysis complete ({len(community)} chars)")

    return {"community": community}
