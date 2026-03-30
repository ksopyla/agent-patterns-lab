# Changelog

All notable changes to this project are documented here.

## [2026-03-30] Pattern 02: MCP Tool Integration -- Architecture Redesign

### Added
- Parallel fan-out/fan-in graph: research_planner -> [news_scanner | project_profiler | community_analyst] -> intelligence_compiler
- Research planner extracts `project_name` and `coin_ticker` via LLM, generates tailored `NEWS_QUERIES` and `COMMUNITY_QUERIES` for downstream nodes
- CoinGecko retry with exponential backoff (3 attempts, handles 429 rate limits and 5xx errors)
- Project profiler ticker fallback resolution (search by name, then by ticker symbol)
- News scanner fires 3-4 targeted queries per run and deduplicates results by URL
- Community analyst uses DuckDuckGo with site:reddit.com and Twitter-focused queries for social sentiment
- `docs/CHANGELOG.md` created for tracking project evolution

### Changed
- P02 architecture from outcome-oriented MCP tool (one `research_crypto_project` tool wraps the full pipeline) instead of raw API wrappers as MCP tools
- Sequential graph (5 steps, ~61s) replaced with parallel graph (3 steps, ~51s)
- Community analyst no longer calls CoinGecko -- eliminated data duplication with project profiler
- All agent prompts improved with anti-hallucination rules and explicit output structure
- Intelligence compiler prompt demands source attribution and "Data not available" instead of guessing

### Architecture Decisions
- **Parallel over sequential**: news, profiler, and community have zero data dependencies -- running them in parallel is strictly better. LangGraph native `add_edge` fan-out/fan-in used (no Send API needed)
- **Data source ownership**: each node owns exactly one external data source. Profiler owns CoinGecko (market + dev data). News and community own DuckDuckGo (with different query strategies). Compiler is LLM-only synthesis
- **LLM query generation over regex**: research planner uses the LLM to understand user intent and generate search-engine-optimized queries, replacing brittle `_normalize_query` regex
- **Retry over fail-fast for external APIs**: CoinGecko free tier has aggressive rate limits; retry with backoff prevents silent data loss that was observed in production traces
- **Outcome-oriented MCP**: the MCP server exposes `research_crypto_project` (the full pipeline result) rather than raw API wrappers -- this is the Software 3.0 lesson: expose capabilities, not plumbing

### Dependencies
- No new dependencies added; removed `langchain-mcp-adapters` (MCP client no longer needed inside agents)

## [2026-03-29] Pattern 02: MCP Tool Integration -- Initial Implementation

### Added
- 5-agent intelligence pipeline: Research Planner, News Scanner, Project Profiler, Community Analyst, Intelligence Compiler
- FastAPI REST entry point (`POST /run`) and FastMCP server entry point (`research_crypto_project` tool)
- CoinGecko API client (`src/coingecko.py`) with search, info, and price endpoints
- DuckDuckGo web search integration for news scanning
- Multi-container Docker Compose (agent :8000, MCP server :8001)
- LangSmith tracing with tagged runs (pattern, example, provider, runtime, env)
- Unit tests (10), API tests (7), e2e test (1) -- 23 total, 99% coverage

## [2026-03-28] Pattern 01: Orchestrator Pipeline

### Added
- 3-agent pipeline: Research Planner, News Scanner, Intelligence Compiler
- LangGraph StateGraph with TypedDict state
- FastAPI entry point with LangSmith tracing
- Docker Compose single-container deployment
- Shared library `libs/common/` with `agent_common` (LLM, tracing utilities)
