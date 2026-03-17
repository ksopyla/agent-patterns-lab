# Agent Design Patterns -- Curriculum

A progressive, hands-on curriculum that takes you from a single LangGraph pipeline to a fully distributed, authenticated, cloud-deployed multi-agent system. Every pattern builds on the previous one, with working code, Docker Compose for local execution, LangSmith tracing, and verbose debug output.

## Domain: Crypto Intelligence Platform

All patterns share a single compelling domain -- **crypto project intelligence**. Three specialized teams emerge as complexity grows:

### Team 1: Intelligence (Fundamentals Research)

Built in Patterns 01-04. Focuses on non-technical, qualitative signals.

| Agent | Responsibility |
|-------|---------------|
| Research Planner | Analyzes the crypto project request, creates a structured research plan |
| News Scanner | Searches the web for recent news, announcements, partnerships |
| Project Profiler | Researches project goals, whitepaper, technology, roadmap, team/founders |
| Community Analyst | Monitors X/Twitter sentiment, community discussions, GitHub activity |
| Intelligence Compiler | Synthesizes all findings into a structured fundamentals report |

### Team 2: Technical Analysis

Introduced in Pattern 05. Focuses on price-based, quantitative analysis.

| Agent | Responsibility |
|-------|---------------|
| Price Collector | Gets current and historical price/volume data via MCP (CoinGecko) |
| Indicator Calculator | Computes technical indicators (MA, RSI, MACD, Bollinger Bands) |
| Level Analyst | Identifies support/resistance levels, key price zones |
| Technical Reporter | Produces a technical analysis summary |

### Team 3: Trading Signals

Introduced in Pattern 06. Consumes output from both Team 1 and Team 2.

| Agent | Responsibility |
|-------|---------------|
| Signal Synthesizer | Combines fundamentals intelligence + technical analysis |
| Risk Assessor | Evaluates risk (volatility, market conditions, project health) |
| Trade Advisor | Produces actionable buy/sell/hold recommendations with confidence levels |

---

## Pattern Progression

```mermaid
graph TD
    subgraph foundation ["Foundation Tier"]
        P01["P01: Orchestrator Pipeline"]
        P02["P02: MCP Tool Integration"]
        P03["P03: Persistent Memory"]
        P04["P04: Memory Lifecycle\n(enrichment)"]
    end
    subgraph distribution ["Distribution Tier"]
        P05["P05: Distributed A2A"]
        P06["P06: Async + Streaming"]
    end
    subgraph enterprise ["Enterprise Tier"]
        P07["P07: Cross-Network Auth"]
        P08["P08: Discovery + Observability"]
        P09["P09: Cloud Deployment"]
    end
    P01 --> P02
    P02 --> P03
    P03 --> P04
    P03 --> P05
    P04 -.-> P05
    P05 --> P06
    P06 --> P07
    P07 --> P08
    P08 --> P09
```

**Main path**: P01 -> P02 -> P03 -> P05 -> P06 -> P07 -> P08 -> P09

**Optional enrichment**: P04 branches off P03 (can be skipped without breaking the progression)

**Team introduction timeline**:

- Patterns 01-04: Team 1 only (single service, growing capabilities)
- Pattern 05: Team 2 arrives (2 services, A2A communication)
- Pattern 06+: Team 3 arrives (3 services, full distributed system)

---

## Foundation Tier (Patterns 01-04)

Focus: agent internals -- orchestration, tools, memory. All run in a single Docker network with no authentication overhead.

---

### Pattern 01: Orchestrator Pipeline

**Folder:** `examples/01-orchestrator-pipeline/`

**Goal:** Decompose a complex research task across multiple specialized agents within a single LangGraph StateGraph, exposed via FastAPI, with LangSmith tracing and verbose debug output.

**What it solves:** A single monolithic LLM prompt tries to plan, research, and write all at once, producing shallow and inconsistent results. The orchestrator pattern splits responsibility across focused agents that each do one thing well.

**Team focus:** Team 1 (Intelligence) -- first 3 agents as a minimal viable pipeline.

**Agents:**

| Agent | Role | Tool |
|-------|------|------|
| Research Planner | Breaks down "Research project X" into subtasks | None (LLM only) |
| News Scanner | Searches the web for recent news and project info | DuckDuckGo web search |
| Intelligence Compiler | Synthesizes findings into a structured report | None (LLM only) |

**Architecture:**

```mermaid
graph TD
    User["User Request\n(POST /run)"] --> FastAPI
    FastAPI --> StateGraph
    subgraph StateGraph ["LangGraph StateGraph"]
        Planner["Research Planner\n(creates research plan)"]
        Scanner["News Scanner\n(web search + analysis)"]
        Compiler["Intelligence Compiler\n(structured report)"]
        Planner --> Scanner
        Scanner --> Compiler
    end
    Compiler --> Response["Intelligence Report\n(JSON)"]
    StateGraph -.->|traces| LangSmith
```

**Key concepts:**

- LangGraph StateGraph with TypedDict state
- Orchestrator pattern (single graph coordinates multiple agent nodes)
- Simple tool use (DuckDuckGo web search as a direct tool call)
- LangSmith tracing setup and trace inspection
- Verbose mode for learning/debugging
- Docker Compose single-container deployment
- FastAPI as a simple trigger endpoint (Software 2.0 entry point)

**Use case example:** "Research the Arbitrum crypto project" -- plan the research, scan the web for news and project info, compile into a structured intelligence report.

**Prerequisites:** Python 3.14+, Docker, uv, API keys (Azure OpenAI or Anthropic), LangSmith account

---

### Pattern 02: MCP Tool Integration

**Folder:** `examples/02-mcp-tool-integration/`

**Goal:** Give agents standardized access to external tools and data sources via the Model Context Protocol (MCP). Build a custom MCP server, connect agents as MCP clients, and show how Claude Code can use the same tools.

**What it solves:** In Pattern 01, tools are hardcoded Python function calls. This doesn't scale -- if you want to share tools across agents, teams, or even with external AI clients (Claude Code, Cursor), you need a standard protocol. MCP provides that abstraction layer.

**Team focus:** Team 1 (Intelligence) -- expands to full 5-agent lineup with specialized MCP tools.

**Agents:**

| Agent | Role | MCP Tools Used |
|-------|------|---------------|
| Research Planner | Creates research plan | None |
| News Scanner | Web search for news | web-search MCP server |
| Project Profiler | Project info, team, roadmap | crypto-data + web-search MCP |
| Community Analyst | GitHub activity, social signals | crypto-data MCP |
| Intelligence Compiler | Synthesizes all outputs | None |

**Architecture:**

```mermaid
graph TD
    User["User / Claude Code"] --> FastAPI["Agent Service\n(FastAPI :8000)"]
    FastAPI --> Pipeline["LangGraph Pipeline\n(5 agents)"]
    Pipeline -->|MCP client| CryptoMCP["crypto-data MCP Server\n(:8001)"]
    Pipeline -->|MCP client| WebMCP["web-search MCP Server\n(:8002)"]
    CryptoMCP --> CoinGecko["CoinGecko API"]
    WebMCP --> DDG["DuckDuckGo"]
    ClaudeCode["Claude Code\n(MCP client)"] -->|MCP| CryptoMCP
    ClaudeCode -->|MCP| WebMCP
```

**Key concepts:**

- MCP server implementation (exposing tools as MCP resources)
- MCP client in LangGraph agents (via `langchain-mcp-adapters`)
- Tool abstraction: agents don't know/care about the underlying API
- Multi-container Docker Compose (agent + MCP servers)
- Claude Code integration: configure Claude Code to connect to the same MCP servers on localhost
- Free crypto data via CoinGecko API (no API key required for basic endpoints)
- Software 3.0 principle: standardized tool access replaces bespoke integrations

**Builds on:** Pattern 01

---

### Pattern 03: Persistent Memory

**Folder:** `examples/03-persistent-memory/`

**Goal:** Add persistent state across conversations using LangGraph's checkpointer backed by PostgreSQL. When a user asks about a crypto project a second time, the system remembers previous research and provides incremental updates instead of starting from scratch.

**What it solves:** In Patterns 01-02, every request starts fresh. For a research platform, this wastes tokens and time -- if you researched Arbitrum yesterday, you should build on that knowledge, not repeat it.

**Team focus:** Team 1 (Intelligence) -- same 5 agents, now with persistent memory.

**Architecture:**

```mermaid
graph TD
    User --> FastAPI["Agent Service\n(FastAPI :8000)"]
    FastAPI --> Pipeline["LangGraph Pipeline\n+ Checkpointer"]
    Pipeline --> PG["PostgreSQL\n(conversation state + research cache)"]
    Pipeline --> CryptoMCP["crypto-data MCP\n(:8001)"]
    Pipeline --> WebMCP["web-search MCP\n(:8002)"]
```

**Key concepts:**

- LangGraph checkpointer with PostgreSQL backend
- Thread-based conversation management (each project = a thread)
- Research result caching and incremental updates
- State persistence across agent restarts
- Docker Compose with PostgreSQL container

**libs/common additions:** `agent_common.memory` -- checkpointer setup utilities

**Builds on:** Pattern 02

---

### Pattern 04: Memory Lifecycle Management (Enrichment)

**Folder:** `examples/04-memory-lifecycle/`

**Goal:** Manage growing agent memory with consolidation, expiration, and hierarchical organization. Introduce a Memory Refiner agent that runs periodically to keep the knowledge base accurate and compact.

**What it solves:** After many research sessions, memory grows unbounded. Stale facts ("BTC price is $67k") pollute new analyses. The system needs to distinguish between ephemeral data (prices, news) and durable knowledge (project launch date, team composition).

**Note:** This is an enrichment pattern. The main progression continues from Pattern 03 to Pattern 05. Skip this if your priority is distributed architecture.

**Key concepts:**

- Memory Refiner agent (consolidates and prunes the knowledge base)
- Fact TTL: timestamped facts with expiration policies
  - Price data: 1-hour TTL
  - News: 7-day TTL
  - Project fundamentals: no expiration
- Hierarchical memory tiers:
  - Working memory (current conversation context)
  - Episodic memory (past research sessions)
  - Semantic memory (consolidated, long-term knowledge)
- Memory compaction strategies

**Builds on:** Pattern 03

---

## Distribution Tier (Patterns 05-07)

Focus: splitting agents into separate services, introducing real distributed systems concerns. Each new team creates a genuine architectural challenge.

---

### Pattern 05: Distributed Agents -- A2A Protocol

**Folder:** `examples/05-distributed-a2a/`

**Goal:** Split agents across separate Docker containers -- simulating separate teams in an organization -- and communicate via the A2A (Agent-to-Agent) protocol.

**What it solves:** In a real company, different teams build and deploy their agents independently. Team 1 (Intelligence) cannot import Team 2's code directly. They need a standardized protocol for task handoff: "Here's a crypto project name, give me a technical analysis." A2A provides this.

**Story:** Team 2 (Technical Analysis) has built their own agent service with price data and indicator calculations. Team 1 needs to request technical analysis to enrich intelligence reports. The teams deploy independently and communicate via A2A.

**Architecture:**

```mermaid
graph TD
    subgraph team1net ["Team 1: Intelligence Service (:8001)"]
        RP["Research Planner"]
        NS["News Scanner"]
        PP["Project Profiler"]
        CA["Community Analyst"]
        IC["Intelligence Compiler"]
        RP --> NS --> PP --> CA --> IC
    end
    subgraph team2net ["Team 2: Technical Analysis (:8002)"]
        PC["Price Collector"]
        IndCalc["Indicator Calculator"]
        LA["Level Analyst"]
        TR["Technical Reporter"]
        PC --> IndCalc --> LA --> TR
    end
    IC -->|"A2A JSON-RPC\ntask/send"| TR
    team1net -->|".well-known/agent-card.json"| Discovery
    team2net -->|".well-known/agent-card.json"| Discovery["Capability\nAdvertisement"]
```

**Key concepts:**

- A2A (Agent-to-Agent) protocol: JSON-RPC over HTTP
- Agent Cards (`.well-known/agent-card.json`) for capability advertisement
- Task lifecycle: `submitted` -> `working` -> `completed`
- Separate FastAPI services per team (independent deployment)
- Docker Compose with multiple services on the same network
- Protocol-driven endpoints replace REST API design

**libs/common additions:** `agent_common.a2a` -- A2A protocol client/server helpers

**Builds on:** Pattern 03

---

### Pattern 06: Async Communication and Streaming

**Folder:** `examples/06-async-streaming/`

**Goal:** Enable non-blocking agent communication and stream partial results as they become available.

**What it solves:** Team 3 (Trading Signals) needs data from BOTH Team 1 and Team 2. Calling them sequentially takes 60+ seconds. Team 3 must fire parallel async requests and stream partial signals as data arrives. Synchronous A2A calls from Pattern 05 become a bottleneck.

**Story:** Team 3 (Trading Signals) arrives. It fires parallel A2A requests to Team 1 and Team 2, merges results as they arrive, and streams buy/sell signals via SSE to the caller.

**Architecture:**

```mermaid
graph LR
    subgraph team3 ["Team 3: Trading Signals (:8003)"]
        SS["Signal Synthesizer"]
        RA["Risk Assessor"]
        TA["Trade Advisor"]
        SS --> RA --> TA
    end
    T1["Team 1\nIntelligence\n(:8001)"] -->|"A2A async\npartial results"| SS
    T2["Team 2\nTechnical\n(:8002)"] -->|"A2A async\npartial results"| SS
    TA -->|"SSE stream"| Client["Client /\nClaude Code"]
```

**Key concepts:**

- Async task submission (fire-and-poll vs. fire-and-wait)
- SSE (Server-Sent Events) for streaming partial results
- Parallel A2A requests: Team 3 calls Team 1 and Team 2 concurrently
- A2A async extensions (task status polling, push notifications)
- Non-blocking agent handoffs
- Backpressure and timeout patterns

**Builds on:** Pattern 05

---

### Pattern 07: Cross-Network Authentication

**Folder:** `examples/07-cross-network-auth/`

**Goal:** Secure agent-to-agent communication when agents operate in different trust zones, using Auth0 as a shared OIDC provider.

**What it solves:** Team 2 (Technical Analysis) is now operated by an external partner company. They run on a separate network with no implicit trust. Every A2A request must carry a JWT token. Without authentication, any service on the network could impersonate Team 1 and exfiltrate data from Team 2.

**Story:** Team 2 moves to a partner organization. Teams 1 and 3 must authenticate every A2A call with JWT tokens issued by Auth0. Team 2 validates tokens before processing any task.

**Architecture:**

```mermaid
graph TD
    subgraph internalNet ["Internal Network"]
        T1["Team 1:\nIntelligence\n(:8001)"]
        T3["Team 3:\nTrading Signals\n(:8003)"]
    end
    subgraph partnerNet ["Partner Network"]
        T2["Team 2:\nTechnical Analysis\n(:8002)"]
    end
    Auth0["Auth0\n(OIDC Provider)"]
    T1 -->|"1. Get M2M token"| Auth0
    T1 -->|"2. A2A + JWT"| T2
    T3 -->|"1. Get M2M token"| Auth0
    T3 -->|"2. A2A + JWT"| T2
    T2 -->|"Validate JWT"| Auth0
```

**Key concepts:**

- Separate Docker networks simulating different organizational boundaries
- Auth0 OIDC / OAuth 2.0 for M2M (machine-to-machine) authentication
- JWT token flow: request -> attach to A2A call -> validate on receiver
- FastAPI JWT validation middleware
- Per-team client credentials
- Token caching and refresh patterns
- Zero-trust agent communication

**libs/common additions:** `agent_common.auth` -- auth middleware and token client

**Builds on:** Pattern 06

---

## Enterprise Tier (Patterns 08-09)

Focus: production readiness -- discovery, observability, and cloud deployment.

---

### Pattern 08: Agent Discovery and Observability

**Folder:** `examples/08-discovery-observability/`

**Goal:** Enable agents to find each other dynamically in enterprise environments, and monitor the full distributed system with distributed tracing.

**What it solves:** With hardcoded URLs, adding a new agent capability requires code changes in every consumer. When Team 2 adds a "Whale Tracker" agent, Team 3 should discover and use it without redeployment. Meanwhile, with 12+ agents across 3 teams, debugging failures requires distributed tracing across A2A calls.

**Story:** Team 2 adds a Whale Tracker agent that monitors large wallet movements. Team 3 discovers it dynamically through the shared agent registry and starts using it for trading signals -- no code changes, no redeployment.

**Key concepts (Discovery):**

- Three discovery patterns compared:
  1. Static/explicit (hardcoded URLs -- simplest, least flexible)
  2. Shared registry service (central catalog -- most common in enterprise)
  3. A2A Agent Cards with network scanning (decentralized -- most resilient)
- Registry service implementation (FastAPI + PostgreSQL)
- Agent registration, deregistration, health checking
- Capability-based agent matching
- Versioning and deprecation patterns

**Key concepts (Observability):**

- LangSmith dashboard: traces, latency, error rates across all 3 teams
- OpenTelemetry integration for infrastructure metrics
- Distributed tracing: correlate traces across A2A calls
- Health check patterns for agent liveness/readiness

**Builds on:** Pattern 07

---

### Pattern 09: Cloud Deployment (Azure)

**Folder:** `examples/09-cloud-deployment/`

**Goal:** Deploy the full three-team distributed system to Azure using Infrastructure as Code with automated CI/CD.

**What it solves:** Docker Compose is great for local development, but production needs managed infrastructure: auto-scaling, secret management, centralized logging, health monitoring, and independent deployment pipelines per team.

**Story:** All three teams go to production. Each deploys independently as an Azure Container App. Teams 1 and 3 are internal (Azure Managed Identity for auth), Team 2 is the external partner (Auth0 remains for cross-org calls).

**Key concepts:**

- Azure Container Apps for agent hosting (one per team)
- Azure Bicep templates for Infrastructure as Code
- Azure Container Registry for container images
- Azure Key Vault for secrets (replaces `.env`)
- Azure Managed Identity for internal auth (Team 1 <-> Team 3)
- Auth0 for cross-organization auth (Teams 1/3 <-> Team 2)
- GitHub Actions CI/CD pipeline (separate workflows per team)
- Log Analytics for centralized logging
- Cost optimization: scale-to-zero, consumption plans

**Builds on:** Pattern 08

---

## Deliverables Per Pattern

1. Self-contained working code (`docker compose up --build` to run)
2. Comprehensive `README.md` in the pattern folder
3. Full test suite (`tests/unit/`, `tests/api/`, `tests/e2e/`)
4. CHANGELOG entry

---

## Tech Stack

- **Python 3.14+** with **uv** for package and Python version management
- **LangGraph** for agent orchestration (StateGraph with typed state)
- **FastAPI** for agent HTTP/protocol endpoints
- **Docker Compose** for local multi-container environments
- **LangSmith** for tracing and observability
- **MCP** for standardized tool access (Pattern 02+)
- **A2A** for agent-to-agent communication (Pattern 05+)
- **Auth0** for OIDC-based agent authentication (Pattern 07+)
- **Azure Container Apps** for cloud deployment (Pattern 09)
