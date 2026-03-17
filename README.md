# Agent Design Patterns Lab

> Practical design patterns for distributed multi-agent systems -- from a single LangGraph pipeline to enterprise-grade, cloud-deployed agent architectures.

## The Journey

You are building a **Crypto Intelligence Platform**. It starts as a simple research pipeline -- three agents collaborating inside one process to analyze crypto projects. Then, pattern by pattern, the system evolves:

Tools get standardized through **MCP**, so Claude Code can use the same data sources as your agents. Memory becomes persistent, so yesterday's research isn't lost. Then a second team appears -- **Technical Analysis** -- running in its own container, speaking **A2A protocol**. A third team, **Trading Signals**, needs data from both and can't afford to wait, so communication goes async with **SSE streaming**. The Technical Analysis team moves to an external partner, and suddenly you need **Auth0 JWT tokens** on every call. New agents appear and need to be discovered dynamically. Finally, the whole system deploys to **Azure**.

Each step solves a real architectural problem. No artificial exercises -- the domain demands the pattern.

## Design Patterns

| # | Pattern | What It Solves | Key Concepts |
|---|---------|---------------|--------------|
| 01 | [Orchestrator Pipeline](examples/01-orchestrator-pipeline/) | Decomposing tasks across specialized agents | LangGraph StateGraph, orchestrator pattern, tool use, LangSmith tracing |
| 02 | [MCP Tool Integration](examples/02-mcp-tool-integration/) | Standardized tool access for agents and AI clients | MCP servers, MCP clients, tool abstraction, Claude Code integration |
| 03 | [Persistent Memory](examples/03-persistent-memory/) | Remembering across conversations | LangGraph checkpointer, PostgreSQL, thread management |
| 04 | [Memory Lifecycle](examples/04-memory-lifecycle/) | Managing growing knowledge bases | Memory refiner, fact TTL, hierarchical memory |
| 05 | [Distributed Agents (A2A)](examples/05-distributed-a2a/) | Cross-team agent communication | A2A protocol, Agent Cards, JSON-RPC, task lifecycle |
| 06 | [Async Communication](examples/06-async-streaming/) | Non-blocking multi-team coordination | Async A2A, SSE streaming, parallel requests |
| 07 | [Cross-Network Auth](examples/07-cross-network-auth/) | Securing agents across trust boundaries | Auth0 OIDC, M2M tokens, JWT validation, zero-trust |
| 08 | [Discovery & Observability](examples/08-discovery-observability/) | Finding agents and monitoring the system | Agent registry, distributed tracing, OpenTelemetry |
| 09 | [Cloud Deployment](examples/09-cloud-deployment/) | Production infrastructure | Azure Container Apps, Bicep IaC, CI/CD, Managed Identity |

### Three Teams, One Platform

```
  Team 1: Intelligence          Team 2: Technical Analysis     Team 3: Trading Signals
  (Patterns 01-04)              (Pattern 05+)                  (Pattern 06+)

  Research Planner              Price Collector                 Signal Synthesizer
  News Scanner                  Indicator Calculator            Risk Assessor
  Project Profiler              Level Analyst                   Trade Advisor
  Community Analyst             Technical Reporter
  Intelligence Compiler
```

Team 1 researches fundamentals (news, team, roadmap, community). Team 2 crunches numbers (price, indicators, support/resistance). Team 3 combines both into actionable trading signals. Each team deploys independently, communicates via A2A protocol, and authenticates across trust boundaries.

## Quick Start

```bash
# Clone and setup
git clone https://github.com/ksopyla/agent-patterns-lab.git
cd agent-patterns-lab
cp .env.example .env
# Fill in your API keys in .env

# Install all dependencies
make setup

# Run Pattern 01
make example EX=01-orchestrator-pipeline

# Test it
curl http://localhost:8000/health
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"input": "Research the Arbitrum crypto project"}'
```

## Project Structure

```
agent-patterns-lab/
├── examples/                # One folder per pattern, each self-contained
│   ├── 01-orchestrator-pipeline/
│   ├── 02-mcp-tool-integration/
│   └── ...
├── libs/common/             # Shared utilities (LLM config, tracing, MCP, A2A, auth)
├── docs/                    # Curriculum, changelog
├── infra/                   # Docker base images, Azure Bicep
├── .github/                 # CI/CD workflows, PR templates
└── .cursor/                 # Cursor rules and skills for AI-assisted development
```

Each pattern folder is self-contained with its own `README.md`, `pyproject.toml`, `docker-compose.yml`, `src/`, and `tests/`.

## Verbose / Debug Mode

Every example supports `VERBOSE=true` (set in `.env`) which logs:

- Agent reasoning steps with timestamps
- Tool call inputs/outputs
- Inter-agent message payloads
- LangSmith trace IDs for quick lookup

## Testing

```bash
# Full suite (unit + API + e2e across all patterns)
python scripts/testing/run_test_suite.py

# Without coverage
python scripts/testing/run_test_suite.py --no-coverage

# Install git hooks
uv run pre-commit install --install-hooks --hook-type pre-commit --hook-type commit-msg
```

## Tech Stack

- **Python 3.14+** / **uv** -- package and Python version management
- **LangGraph** -- agent orchestration with typed state graphs
- **FastAPI** -- agent HTTP/protocol endpoints
- **Docker Compose** -- local multi-container environments
- **LangSmith** -- tracing and observability
- **MCP** -- standardized tool access (Pattern 02+)
- **A2A** -- agent-to-agent communication protocol (Pattern 05+)
- **Auth0** -- OIDC-based agent authentication (Pattern 07+)
- **Azure Container Apps** -- cloud deployment (Pattern 09)

## Blog

Detailed write-ups for each pattern at [ai.ksopyla.com](https://ai.ksopyla.com).

## License

MIT
