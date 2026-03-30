# Vision & Roadmap

## Why This Exists

The AI agent landscape in 2025-2026 is where microservices were in 2014: everyone talks about it, frameworks multiply weekly, but few teams have shipped production multi-agent systems. The gap isn't tooling -- LangGraph, CrewAI, AutoGen all work. The gap is **architectural knowledge**: how do you actually structure, deploy, and operate agents that work together?

This project exists to close that gap. Not with slides or blog posts, but with **working code that progresses through real architectural challenges**, from a single Python process to a cloud-deployed distributed system.

## The Software 3.0 Thesis

Software engineering is undergoing a paradigm shift:

**Software 1.0** -- Deterministic code. You write every instruction. Input → fixed logic → output.

**Software 2.0** -- Machine learning models. You provide data, the model learns patterns. But the interface is still REST APIs, dashboards, and human-operated UIs.

**Software 3.0** -- Autonomous agents. AI systems that reason, plan, use tools, and collaborate with other AI systems. The interface isn't a dashboard -- it's a protocol. Agents expose capabilities via MCP. Agents discover and invoke each other via A2A. The human interacts through an AI client (Claude Code, Cursor), not a bespoke chat widget or dedicated UI.

This project demonstrates the transition. In Pattern 01, you build a familiar FastAPI endpoint -- `POST /run` -- that triggers a pipeline. Comfortable, recognizable, Software 2.0. By Pattern 05, that same FastAPI server hosts A2A JSON-RPC endpoints. By Pattern 09, agents discover each other dynamically, authenticate via JWT, and deploy as independent cloud services. HTTP is still the transport, but what travels over it has fundamentally changed.

## Why "Design Patterns", Not "Tutorials"

The name is intentional. "Tutorial" implies a one-time learning exercise you discard. "Design Pattern" implies a reusable architectural solution you reference repeatedly -- like the Gang of Four patterns, Cloud Design Patterns, or Microservices Patterns.

Each pattern in this library:

- **Solves a named architectural problem** ("How do agents in different trust zones authenticate?")
- **Has clear applicability criteria** ("Use when agents cross organizational boundaries")
- **Shows trade-offs** ("Simpler than mTLS, but requires a centralized OIDC provider")
- **Builds on previous patterns** (you understand the progression, not just isolated techniques)

When a senior engineer asks "how should our agents communicate across services?", they can point to Pattern 05 (A2A) and Pattern 06 (async/streaming) as reference architectures -- not tutorials to follow, but patterns to adapt.

## The Story: Building a Crypto Intelligence Platform

Abstract architectural patterns are hard to internalize. Concrete stories stick. This project uses a single, evolving domain throughout all nine patterns: **a crypto project intelligence platform**.

The domain was chosen deliberately:

- **Rich data landscape** -- news, prices, social sentiment, on-chain data, GitHub activity. Plenty of distinct data sources for agents to specialize in.
- **Natural team boundaries** -- fundamentals research, technical analysis, and trading signals are genuinely different disciplines with different cadences, data sources, and expertise.
- **Real coordination needs** -- a trading signal is meaningless without both qualitative intelligence and quantitative analysis. Team 3 literally cannot function without Teams 1 and 2.
- **Free APIs available** -- CoinGecko, DuckDuckGo, GitHub all offer free tiers sufficient for the examples.
- **Compelling to developers** -- crypto is a domain where many developers have personal interest, making the examples more engaging than "process invoices" or "manage tickets."

### Act 1: One Team, Growing Capabilities (Patterns 01-04)

You are **Team 1: Intelligence**. Your job is fundamentals research -- given a crypto project name, produce a structured intelligence report covering news, technology, team, community, and roadmap.

**Pattern 01** starts small. Three agents in a single LangGraph pipeline: a Research Planner breaks the task into subtasks, a News Scanner searches the web, and an Intelligence Compiler synthesizes everything into a report. It works. It's simple. It runs in one Docker container.

But the News Scanner's web search is a hardcoded Python function call. What if you want Claude Desktop to use the same search capability? What if another team wants access to the same crypto data tools?

**Pattern 02** introduces MCP -- but not the way you might expect. Instead of wrapping raw APIs as MCP tools, you expose the agent pipeline itself. A `crypto-intelligence` MCP server wraps the full 5-agent research pipeline as a single `research_crypto_project` tool. Claude Desktop calls one MCP tool and gets a complete intelligence report -- the internal orchestration (five agents, CoinGecko data, DuckDuckGo search) is hidden behind the protocol. This is the real Software 3.0 lesson: expose capabilities, not plumbing. The team expands to five agents, the architecture moves to multi-container Docker Compose, and the agent now has two entry points -- REST (`POST /run`) and MCP -- serving the same graph.

Now the team works well, but every request starts from scratch. You researched Arbitrum yesterday -- why are you re-scanning the same news today?

**Pattern 03** adds persistent memory. LangGraph's checkpointer, backed by PostgreSQL, remembers previous research sessions. When you ask about Arbitrum again, the system provides incremental updates, not a full repeat. Each project becomes a "thread" with accumulated knowledge.

Memory grows. After 50 research sessions, the knowledge base is bloated with stale price data, outdated news, and redundant facts.

**Pattern 04** (optional enrichment) introduces memory lifecycle management. A Memory Refiner agent consolidates knowledge, expires stale facts (price data after 1 hour, news after 7 days), and organizes memory into tiers: working memory for the current conversation, episodic memory for past sessions, semantic memory for durable knowledge.

At this point, Team 1 is a mature, memory-backed research engine. But it only knows about fundamentals. For investment decisions, you also need technical analysis -- price trends, indicators, support/resistance levels.

### Act 2: A Second Team Arrives (Patterns 05-06)

**Pattern 05** introduces **Team 2: Technical Analysis** -- a completely separate service with its own agents (Price Collector, Indicator Calculator, Level Analyst, Technical Reporter), its own Docker container, its own codebase. Team 1 can't `import` Team 2's code. They need a protocol.

This is where A2A (Agent-to-Agent protocol) enters. Team 1's Intelligence Compiler submits a task to Team 2 via A2A JSON-RPC: "Give me technical analysis for Arbitrum." Team 2 processes it and returns a structured result. Each service publishes an Agent Card (`.well-known/agent-card.json`) advertising its capabilities.

The architectural problem is real: how do separately deployed agent services exchange structured work? The answer is A2A -- and it mirrors how real engineering organizations operate, where teams build and deploy independently.

**Pattern 06** brings **Team 3: Trading Signals**. This team needs data from *both* Team 1 (qualitative intelligence) and Team 2 (quantitative analysis) to produce buy/sell/hold recommendations. But calling them sequentially is unacceptable -- a full intelligence report takes 30+ seconds, technical analysis takes 20+ seconds. Sequential execution means 50+ seconds before Team 3 can even start.

Team 3 must fire parallel async A2A requests, process partial results as they arrive, and stream trading signals to the caller via SSE. The synchronous A2A model from Pattern 05 becomes the bottleneck that motivates async communication and streaming.

Three teams. Three services. Real distributed systems challenges.

### Act 3: Enterprise Reality (Patterns 07-09)

The three-team system works on a single Docker network, but real organizations don't have that luxury.

**Pattern 07** simulates a real-world scenario: Team 2 (Technical Analysis) is now operated by an **external partner company**. They run on a separate network with no implicit trust. Every A2A request from Team 1 or Team 3 must carry a JWT token issued by Auth0 (OIDC provider). Team 2 validates the token before processing any task.

Separate Docker networks simulate the organizational boundary. Auth0 M2M (machine-to-machine) credentials replace implicit trust. The lesson is zero-trust agent communication -- critical for any production deployment where agents cross organizational boundaries.

**Pattern 08** addresses what happens as the system grows. Team 2 adds a new agent -- **Whale Tracker** -- that monitors large wallet movements. Team 3 wants to use it for better trading signals. But Team 3 doesn't know the agent exists. The URL isn't hardcoded anywhere.

The solution is a shared agent registry: teams register their capabilities, consumers discover agents dynamically by querying "I need an agent that can track whale wallets." Team 3 discovers Whale Tracker without code changes, without redeployment.

Alongside discovery, with 12+ agents across 3 teams, observability becomes critical. Distributed tracing across A2A calls (using OpenTelemetry and LangSmith) lets you follow a single trading signal request as it flows through Team 3 → Team 1 + Team 2 → back to Team 3.

**Pattern 09** takes everything to production on Azure. Each team deploys as an independent Azure Container App. Infrastructure is defined in Bicep templates. Secrets move from `.env` files to Azure Key Vault. Internal auth (Team 1 ↔ Team 3) uses Azure Managed Identity. Cross-org auth (Teams 1/3 ↔ Team 2) keeps Auth0. GitHub Actions provides CI/CD with separate pipelines per team.

The journey is complete: from a single Python file to a cloud-deployed, authenticated, observable, dynamically-discoverable multi-agent system.

## Why Each Pattern Matters

Every pattern exists because the previous one creates a real limitation:

| Transition | The problem that forces the next pattern |
|------------|------------------------------------------|
| P01 → P02 | Hardcoded tools don't scale. You can't share tools with Claude Code or other teams. |
| P02 → P03 | Every request starts fresh. Repeated research wastes tokens and time. |
| P03 → P04 | Memory grows unbounded. Stale facts pollute analysis. |
| P03 → P05 | A second team arrives. You can't import their code. You need a protocol. |
| P05 → P06 | A third team needs data from both others. Sequential calls are too slow. |
| P06 → P07 | Team 2 moves to a partner org. Implicit trust is gone. |
| P07 → P08 | New agents appear. Consumers shouldn't need code changes to use them. |
| P08 → P09 | Docker Compose doesn't work in production. You need cloud infrastructure. |

No pattern is introduced "because it's next on the list." Each one is motivated by a genuine architectural limitation that the reader has experienced firsthand by building the previous pattern.

## Key Architectural Decisions

### FastAPI: The Constant That Evolves

FastAPI is the HTTP server runtime in every pattern, but what it serves changes fundamentally:

- **Pattern 01**: `POST /run` -- a REST trigger endpoint. Familiar, comfortable.
- **Pattern 02**: MCP server endpoints. The contract shifts from REST resources to protocol operations.
- **Pattern 05+**: A2A JSON-RPC endpoints (`/a2a`). No more REST-style routes -- everything is protocol-driven.

HTTP remains the transport. But by Pattern 05, it's carrying A2A protocol messages, not REST API calls. This progression itself demonstrates the Software 2.0 → 3.0 transition.

### No Custom UI

Building a chat interface is Software 2.0 thinking. In Software 3.0:

- Agents expose themselves as **MCP servers** -- any MCP-compatible client (Claude Code, Claude Desktop, Cursor) can connect and interact.
- Agents expose **A2A endpoints** -- other AI agents can discover and invoke them.
- For development and testing: Claude Code connects to your Dockerized agents via MCP config pointing to `localhost`.

The "UI" is Claude Code. This is introduced in Pattern 02 and reinforced throughout.

### Three Teams, Not Two

Two teams would demonstrate A2A, but three teams create richer architectural challenges:

- **Parallel requests**: Team 3 must call Teams 1 and 2 concurrently (motivates async in P06)
- **Asymmetric trust**: Teams 1 and 3 are internal, Team 2 is external (motivates per-network auth in P07)
- **Dynamic discovery**: Team 3 discovers new capabilities from Team 2 without redeployment (motivates registry in P08)
- **Independent deployment**: each team has its own CI/CD pipeline in cloud (motivates IaC in P09)

Two teams would leave half these problems unaddressed.

## What This Project Is Not

- **Not a framework.** It doesn't produce a reusable library you pip-install. It produces reference implementations you study and adapt.
- **Not a product.** The crypto intelligence platform is a vehicle for teaching architecture, not a production trading system.
- **Not an LLM comparison.** The patterns work with any LLM (Azure OpenAI, Anthropic, etc.). The focus is architecture, not model selection.
- **Not a beginner tutorial.** The reader should be comfortable with Python, Docker, and async programming. The patterns teach distributed agent architecture, not programming fundamentals.

## Roadmap

### Current: Foundation Tier

Building Patterns 01-04 -- the single-team foundation with orchestration, MCP tools, and persistent memory.

### Next: Distribution Tier

Patterns 05-07 -- splitting into multiple services with A2A, async communication, and cross-network authentication.

### Future: Enterprise Tier

Patterns 08-09 -- agent discovery, observability, and Azure cloud deployment.

### Beyond Pattern 09

Ideas for potential future patterns (not yet planned):

- **Multi-model orchestration** -- different LLMs for different agents based on cost/capability trade-offs
- **Human-in-the-loop** -- approval workflows for high-stakes trading signals
- **Agent testing patterns** -- property-based testing, simulation environments, adversarial testing
- **Multi-cloud deployment** -- AWS or GCP alternatives to Pattern 09
