"""Research Planner agent -- orchestrates the research pipeline.

Reads:  state["input"]
Writes: state["plan"], state["project_name"], state["coin_ticker"],
        state["news_queries"], state["community_queries"]

The planner is the first node in the graph. It analyzes the user request,
identifies the crypto project, and produces a research plan with typed query
lists that downstream nodes use directly. This eliminates raw user input being
passed to external APIs and removes the need for regex parsing of LLM text.
"""

from __future__ import annotations

from agent_common.llm import get_chat_model
from agent_common.tracing import verbose_log
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from src.agents.state import AgentState

SYSTEM_PROMPT = """\
You are a crypto project research planner. Given a user query, do three things:

1. **Identify the project** with its official project name and ticker symbol.
2. **Create a focused research plan** (numbered list, one sentence per area):
   a. Recent news, announcements, partnerships, events — positive and negative signals.
   b. Project fundamentals via CoinGecko: market cap, price, volume, exchanges, \
team, genesis date, categories.
   c. Community and social sentiment: X/Twitter buzz, Reddit discussions, \
Telegram activity, overall retail mood.
3. **Generate tailored search queries** for downstream research agents:
   - 3-4 news queries optimized for recent partnerships, announcements, and project updates
   - 3-4 community queries optimized for Reddit, X/Twitter, and social sentiment

Keep the plan concise and actionable. Do NOT include price predictions."""


class ResearchPlan(BaseModel):
    """Structured planner output used by downstream research nodes."""

    project_name: str = Field(description="Official project name")
    coin_ticker: str = Field(description="Ticker symbol in uppercase, for example ETH or SOL")
    plan: str = Field(description="Concise numbered research plan covering news, fundamentals, and community")
    news_queries: list[str] = Field(description="Three to four targeted web search queries for recent project news")
    community_queries: list[str] = Field(
        description="Three to four targeted web search queries for community and social sentiment"
    )


async def research_planner_node(state: AgentState) -> dict[str, str | list[str]]:
    """Create a structured research plan and extract project identifiers."""
    user_input = state["input"]
    verbose_log("ResearchPlanner", f"Planning research for: {user_input[:100]}")

    llm = get_chat_model().with_structured_output(ResearchPlan)
    result = await llm.ainvoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_input),
        ]
    )

    project_name = result.project_name.strip() or user_input.strip()
    coin_ticker = result.coin_ticker.strip().upper()
    news_queries = [query.strip() for query in result.news_queries if query.strip()]
    community_queries = [query.strip() for query in result.community_queries if query.strip()]

    verbose_log(
        "ResearchPlanner",
        (
            f"Identified project={project_name!r}, ticker={coin_ticker!r}, "
            f"news_queries={len(news_queries)}, community_queries={len(community_queries)}"
        ),
    )

    return {
        "plan": result.plan,
        "project_name": project_name,
        "coin_ticker": coin_ticker,
        "news_queries": news_queries,
        "community_queries": community_queries,
    }
