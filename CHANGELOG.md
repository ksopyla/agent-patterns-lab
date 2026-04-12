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

---

## [2026-03-29] Pattern 02: MCP Tool Integration -- complete

### Summary
Full Team 1 intelligence pipeline (5 agents) with crypto-intelligence MCP server
wrapping CoinGecko. Demonstrates MCP from the builder's perspective: standardized
tool access that any MCP client (agents, Claude Desktop, Cursor) can connect to.

### Added
- `crypto-intelligence` MCP server (`src/mcp_servers/crypto_intelligence.py`) with 3 CoinGecko tools: `search_coins`, `get_coin_info`, `get_coin_price`
- Project Profiler agent -- gathers project fundamentals via MCP tools
- Community Analyst agent -- assesses community/developer health via MCP tools
- MCP client lifecycle management (`mcp_setup.py`) with `MultiServerMCPClient`
- Multi-container Docker Compose (agent + crypto-intelligence MCP server)
- Claude Desktop integration instructions in README
- Graceful degradation in all agent nodes (MCP failures, search failures, LLM failures produce partial output)
- Input validation (`3-500 chars`), error handling (502 on pipeline failure), LangSmith run config -- matching Pattern 01 conventions
- Full test suite: 30 tests (unit for all 5 nodes + MCP server + MCP setup, API for validation/errors/pipeline, e2e for graph execution order)

### Changed
- Renamed `crypto-data` → `crypto-intelligence` MCP server (better name reflecting purpose)
- Updated `docs/curriculum.md` with sharper Pattern 02 goal and implementation details
- Updated `docs/vision.md` Pattern 02 narrative
- Example README rewritten matching Pattern 01 structure (Quick Start, At a Glance, Architecture, When to Use, Implementation Walkthrough, Verification, Exercises, Trade-offs)

### Architecture Decisions
- **CoinGecko as MCP server, not raw API**: Wrapping CoinGecko in MCP demonstrates the core lesson -- standardized tool access. Free tier (no API key) keeps onboarding simple.
- **DuckDuckGo stays as direct tool**: MCP and direct tools coexist pragmatically. Use MCP for shared, reusable domain tools; keep direct calls for single-use commodity tools.
- **No external MCP consumption in this pattern**: Considered Brave Search MCP (stdio transport) but rejected -- adds Node.js dependency, API key requirement, and complexity without proportional teaching value. External MCP consumption suggested as an exercise instead.
- **Graph built once in lifespan, not per request**: Matches Pattern 01 convention and avoids unnecessary overhead.

### Dependencies
- langchain-mcp-adapters >= 0.2 (MCP client for LangGraph agents)
- mcp >= 1.0 (MCP server SDK with FastMCP)

---

## [2026-03-29] Pattern 01: Orchestrator Pipeline -- complete

### Summary
Three-agent crypto intelligence pipeline (Research Planner, News Scanner, Intelligence Compiler)
with LangGraph StateGraph, FastAPI, and Docker Compose. First runnable pattern in the series.

### Highlights
- Async agent nodes with graceful degradation (search failure and LLM failure produce partial output, not crashes)
- Full test suite: unit tests for state and all 3 nodes, API tests for all endpoints and validation edges, e2e test for graph execution order
- LangSmith tracing with per-example tags and metadata for filtering across a shared project
- Comprehensive README with architecture diagram, implementation walkthrough, exercises, and trade-offs
- Narrative bridge to Pattern 02 (hardcoded tools don't scale to shared or cross-client use)

### Fixed
- `.env.example` terminology: "Lesson 4+" updated to "Pattern 07+"
- Makefile `lint` target: replaced raw `mypy` invocation with `scripts/linting/run_mypy.py` wrapper to avoid duplicate module errors in monorepo

---

## [2026-03-21] Shared agent Docker build

### Changed
- Examples 01 and 02 build from `infra/docker/base/Dockerfile.agent` only; per-example `Dockerfiles` removed.
- Each `docker-compose.yml` passes `PACKAGE_NAME`, `EXAMPLE_PYPROJECT`, and `EXAMPLE_SRC` as build args.
- Deploy workflow builds with the same Dockerfile and args convention.

## [2026-03-15] Initial Repository Setup

### Added
- Root project configuration with uv workspace (`pyproject.toml`)
- Shared library `libs/common/` with LLM config, LangSmith tracing, and verbose logging utilities
- Cursor rule `tech-stack.mdc` for Python, uv, Docker, LangGraph, FastAPI conventions
- Cursor skills: agent-patterns-advisor, documentation-writer, example-scaffolder, engineering-tracker
- GitHub Actions workflows: CI (lint, type-check, test), security (audit, scanning), deploy (Azure)
- PR template and CODEOWNERS
- Pre-commit hooks: ruff, mypy, detect-secrets, conventional commits
- Base Docker image for agent services (`infra/docker/base/Dockerfile.agent`)
- Curriculum document with 8-lesson Phase 1 plan
- Phase 2 planning document (conversational tutoring system)
- Example 01: Multi-Agent Single System (LangGraph + FastAPI + Docker)

### Architecture Decisions
- **uv over Poetry**: 10-100x faster, PEP 621 native, bundles Python version management
- **Auth0 over Keycloak**: Enterprise standard, free tier sufficient, purpose-built AI agent features
- **LangSmith from day one**: Tracing integrated in shared lib, every agent traced by default
- **A2A + MCP complementary**: MCP for tool access, A2A for agent-to-agent communication
- **Azure Container Apps for deployment**: Stateful, event-driven, fits LangGraph's requirements
- **Verbose mode as cross-cutting concern**: Every agent logs reasoning to stdout when VERBOSE=true

### Dependencies
- langgraph >= 0.4 (agent orchestration)
- langchain-openai >= 0.3 (Azure OpenAI integration)
- langchain-anthropic >= 0.3 (Claude integration)
- langsmith >= 0.3 (tracing and observability)
- fastapi >= 0.115 (HTTP endpoints)
- pydantic >= 2.0 (data validation)
- pydantic-settings >= 2.0 (environment configuration)
