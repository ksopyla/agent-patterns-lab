<div align="center">

# Agent Design Patterns Lab

[![Python 3.14+](https://img.shields.io/badge/python-3.14+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.4+-1C3C3C?style=flat&logo=langchain&logoColor=white)](https://github.com/langchain-ai/langgraph)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg?style=flat)](LICENSE)
[![CI](https://github.com/ksopyla/agent-patterns-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/ksopyla/agent-patterns-lab/actions/workflows/ci.yml)

**Practical design patterns for distributed multi-agent systems**
<br/>
*From a single LangGraph pipeline to enterprise-grade, cloud-deployed agent architectures.*

[Curriculum](docs/curriculum.md) · [Vision & Roadmap](docs/vision.md) · [Blog](https://ai.ksopyla.com) · [Changelog](docs/CHANGELOG.md)

</div>

---

## The Problem

The AI agent landscape today is where microservices were in 2014. Frameworks multiply weekly -- LangGraph, CrewAI, AutoGen -- but few teams have shipped production multi-agent systems. The gap isn't tooling. **The gap is architectural knowledge**: how do you actually structure, deploy, and operate agents that work together across services, trust boundaries, and cloud environments?

This project closes that gap with **9 design patterns**, each solving a named architectural problem with working code you can run, study, and adapt.

## The Approach

Not tutorials. **Design patterns** -- in the tradition of Gang of Four, Cloud Design Patterns, and Microservices Patterns. Each pattern:

- Solves a **real architectural problem** that the previous pattern cannot handle
- Has clear **"when to use / when to avoid"** criteria
- Shows **trade-offs**, not just happy paths
- Builds on the previous pattern -- you experience the limitation before learning the solution

The progression itself tells a story. In Pattern 01 you build a familiar `POST /run` REST endpoint. By Pattern 05 that same FastAPI server hosts A2A JSON-RPC protocol endpoints. By Pattern 09 agents discover each other dynamically, authenticate via JWT, and deploy as independent cloud services. HTTP is still the transport -- but what travels over it has fundamentally changed.

> **This is the Software 2.0 → 3.0 transition, demonstrated through code.**

## The Story

Abstract patterns are hard to internalize. Concrete stories stick.

All nine patterns share a single, evolving domain: **a crypto intelligence platform** with three specialized teams that emerge as complexity demands them. Each team's arrival creates a genuine architectural challenge that motivates the next pattern.

### Act 1 &mdash; One Team, Growing Capabilities
<sup>Patterns 01-04</sup>

You are **Team 1: Intelligence**. Three agents research crypto projects inside a single LangGraph pipeline. It works -- until you realize tools are hardcoded, every request starts from scratch, and memory grows unbounded. Each limitation drives the next pattern: MCP for standardized tools, PostgreSQL-backed checkpointers for persistence, a Memory Refiner for lifecycle management.

### Act 2 &mdash; Teams Multiply, Protocols Emerge
<sup>Patterns 05-06</sup>

**Team 2: Technical Analysis** arrives -- a separate service, separate codebase, separate container. You can't `import` their code. You need a protocol. A2A enters. Then **Team 3: Trading Signals** needs data from *both* teams simultaneously. Sequential calls take 50+ seconds. Async communication and SSE streaming become the only viable path.

### Act 3 &mdash; Enterprise Reality
<sup>Patterns 07-09</sup>

Team 2 moves to an external partner. Implicit trust is gone -- JWT authentication on every call. New agents appear and need dynamic discovery. Three teams deploy to Azure as independent Container Apps with Infrastructure as Code, Managed Identity, and per-team CI/CD pipelines.

**From a single Python file to a cloud-deployed, authenticated, observable, dynamically-discoverable multi-agent system.**

## Design Patterns

<table>
<thead>
<tr>
<th></th>
<th>Pattern</th>
<th>What It Solves</th>
<th>Key Concepts</th>
</tr>
</thead>
<tbody>
<tr><td colspan="4"><strong>Foundation Tier</strong> · Single Docker network, one team, agent internals</td></tr>
<tr>
<td>01</td>
<td><a href="examples/01-orchestrator-pipeline/">Orchestrator Pipeline</a></td>
<td>Decomposing tasks across specialized agents</td>
<td>LangGraph StateGraph, tool use, LangSmith tracing</td>
</tr>
<tr>
<td>02</td>
<td><a href="examples/02-mcp-tool-integration/">MCP Tool Integration</a></td>
<td>Standardized tool access for agents & AI clients</td>
<td>MCP servers/clients, Claude Code integration</td>
</tr>
<tr>
<td>03</td>
<td><a href="examples/03-persistent-memory/">Persistent Memory</a></td>
<td>Remembering across conversations</td>
<td>Checkpointer, PostgreSQL, thread management</td>
</tr>
<tr>
<td>04</td>
<td><a href="examples/04-memory-lifecycle/">Memory Lifecycle</a> <sup>optional</sup></td>
<td>Managing growing knowledge bases</td>
<td>Memory refiner, fact TTL, hierarchical memory</td>
</tr>
<tr><td colspan="4"><strong>Distribution Tier</strong> · Multi-service, multi-team, real distributed systems</td></tr>
<tr>
<td>05</td>
<td><a href="examples/05-distributed-a2a/">Distributed A2A</a></td>
<td>Cross-team agent communication</td>
<td>A2A protocol, Agent Cards, JSON-RPC</td>
</tr>
<tr>
<td>06</td>
<td><a href="examples/06-async-streaming/">Async & Streaming</a></td>
<td>Non-blocking multi-team coordination</td>
<td>Async A2A, SSE streaming, parallel requests</td>
</tr>
<tr>
<td>07</td>
<td><a href="examples/07-cross-network-auth/">Cross-Network Auth</a></td>
<td>Securing agents across trust boundaries</td>
<td>Auth0 OIDC, JWT, M2M tokens, zero-trust</td>
</tr>
<tr><td colspan="4"><strong>Enterprise Tier</strong> · Production readiness, cloud deployment</td></tr>
<tr>
<td>08</td>
<td><a href="examples/08-discovery-observability/">Discovery & Observability</a></td>
<td>Finding agents and monitoring the system</td>
<td>Agent registry, OpenTelemetry, distributed tracing</td>
</tr>
<tr>
<td>09</td>
<td><a href="examples/09-cloud-deployment/">Cloud Deployment</a></td>
<td>Production infrastructure on Azure</td>
<td>Container Apps, Bicep IaC, Managed Identity, CI/CD</td>
</tr>
</tbody>
</table>

### Why Each Transition Matters

Every pattern exists because the previous one creates a real limitation:

```
P01 ─── Hardcoded tools can't be shared ──────────────── P02
P02 ─── Every request starts from scratch ────────────── P03
P03 ─┬─ Memory grows unbounded ──────────────────────── P04 (optional)
     └─ A second team arrives, can't import their code ─ P05
P05 ─── Third team needs both, sequential is too slow ── P06
P06 ─── Team 2 moves to external partner, no trust ──── P07
P07 ─── New agents appear, consumers need code changes ─ P08
P08 ─── Docker Compose doesn't work in production ───── P09
```

## Three Teams, One Platform

```
 ┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────┐
 │  TEAM 1: INTELLIGENCE   │  │ TEAM 2: TECHNICAL       │  │ TEAM 3: TRADING         │
 │  (Patterns 01-04)       │  │ ANALYSIS (Pattern 05+)  │  │ SIGNALS (Pattern 06+)   │
 │                         │  │                         │  │                         │
 │  Research Planner       │  │  Price Collector        │  │  Signal Synthesizer     │
 │  News Scanner           │  │  Indicator Calculator   │  │  Risk Assessor          │
 │  Project Profiler       │  │  Level Analyst          │  │  Trade Advisor          │
 │  Community Analyst      │  │  Technical Reporter     │  │                         │
 │  Intelligence Compiler  │  │                         │  │                         │
 └────────────┬────────────┘  └────────────┬────────────┘  └────────────┬────────────┘
              │                            │                            │
              │         A2A Protocol       │         A2A Protocol       │
              └────────────────────────────┴────────────────────────────┘
```

- **Team 1** researches fundamentals -- news, team, roadmap, community sentiment
- **Team 2** crunches numbers -- price action, indicators, support/resistance levels
- **Team 3** combines both into actionable trading signals with confidence levels

Each team deploys independently, communicates via A2A protocol, and authenticates across trust boundaries.

## Quick Start

```bash
git clone https://github.com/ksopyla/agent-patterns-lab.git
cd agent-patterns-lab
cp .env.example .env
# Fill in your API keys (Azure OpenAI or Anthropic, LangSmith)

# Install dependencies
make setup

# Run Pattern 01
make example EX=01-orchestrator-pipeline

# Verify it's running
curl http://localhost:8000/health

# Submit a research request
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"input": "Research the Arbitrum crypto project"}'
```

### Prerequisites

- **Python 3.14+** (managed via [uv](https://docs.astral.sh/uv/))
- **Docker** and **Docker Compose**
- **API keys**: Azure OpenAI or Anthropic (for LLM), LangSmith (for tracing)

## Project Structure

```
agent-patterns-lab/
├── examples/                  # One folder per pattern (self-contained)
│   ├── 01-orchestrator-pipeline/
│   │   ├── README.md          # Pattern documentation (theory + walkthrough)
│   │   ├── pyproject.toml
│   │   ├── docker-compose.yml
│   │   ├── src/
│   │   └── tests/
│   │       ├── unit/
│   │       ├── api/
│   │       └── e2e/
│   ├── 02-mcp-tool-integration/
│   └── ...
├── libs/common/               # Shared utilities (agent_common package)
│   └── src/agent_common/      # LLM config, tracing, MCP, A2A, auth helpers
├── docs/
│   ├── curriculum.md          # Technical pattern-by-pattern breakdown
│   ├── vision.md              # Full narrative, philosophy, and roadmap
│   └── CHANGELOG.md
├── infra/                     # Docker base images, Azure Bicep templates
└── .github/                   # CI/CD workflows, PR templates
```

## Verbose Mode

Every pattern supports `VERBOSE=true` (set in `.env`), which logs:

- Agent reasoning steps with timestamps
- Tool call inputs and outputs
- Inter-agent message payloads
- LangSmith trace IDs for quick lookup

This is a first-class feature, not an afterthought. Reading verbose output is how you learn what agents are actually doing.

## Testing

Each pattern maintains three test tiers:

- **`tests/unit/`** -- individual agent nodes with mocked LLM responses
- **`tests/api/`** -- HTTP/protocol endpoints with mocked agent graph
- **`tests/e2e/`** -- full pipeline with mocked LLM (graph compilation, state flow)

```bash
# Run full test suite
python scripts/testing/run_test_suite.py

# Install pre-commit hooks
uv run pre-commit install --install-hooks --hook-type pre-commit --hook-type commit-msg
```

## Tech Stack

| Layer | Technology | Role |
|-------|-----------|------|
| Language | Python 3.14+ / uv | Package and version management |
| Orchestration | LangGraph | Agent state graphs with typed state |
| Server | FastAPI | HTTP/protocol endpoints (REST → MCP → A2A) |
| Infrastructure | Docker Compose | Local multi-container environments |
| Observability | LangSmith | Tracing, debugging, performance monitoring |
| Tools | MCP | Standardized tool access (Pattern 02+) |
| Communication | A2A | Agent-to-agent protocol (Pattern 05+) |
| Authentication | Auth0 | OIDC-based M2M auth (Pattern 07+) |
| Cloud | Azure Container Apps | Production deployment (Pattern 09) |

## Further Reading

- **[Full Curriculum](docs/curriculum.md)** -- detailed technical breakdown of each pattern with architecture diagrams
- **[Vision & Roadmap](docs/vision.md)** -- the complete narrative, architectural philosophy, and future direction
- **[Blog](https://ai.ksopyla.com)** -- in-depth write-ups for each pattern
- **[Changelog](docs/CHANGELOG.md)** -- what changed and when

## License

[MIT](LICENSE) -- built by [Krzysztof Sopyła](https://ai.ksopyla.com)
