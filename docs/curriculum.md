# Agent Patterns Lab -- Curriculum

## Overview

A progressive learning path from single-agent basics to fully distributed, authenticated, cloud-deployed multi-agent systems. Every lesson builds on the previous one, with working code, Docker Compose for local execution, LangSmith tracing, and verbose debug output.

## Phase 1: Learning Agent Patterns (8 Lessons)

### Core Patterns (Lessons 1-3): Single Docker Network, No Auth

These lessons focus on multi-agent fundamentals. All agents run on a single Docker network. No authentication overhead -- pure focus on agent logic, communication, and patterns.

---

### Lesson 1: Multi-Agent System as a Single System

**Folder:** `examples/01-multi-agent-single-system/`

**Goal:** Build a multi-agent system where 3 agents (planner, researcher, writer) collaborate within a single LangGraph StateGraph, exposed via FastAPI, with LangSmith tracing and verbose debug output.

**Key concepts:**
- LangGraph StateGraph with typed state
- Orchestrator pattern (single graph coordinates multiple agent nodes)
- LangSmith tracing setup and trace inspection
- Verbose mode for learning/debugging
- Docker Compose for local execution

**Prerequisites:** Python 3.12+, Docker, uv, API keys (Azure OpenAI or Anthropic), LangSmith account

---

### Lesson 2: Memory and External Services via MCP

**Folder:** `examples/02-memory-and-external-services/`

**Goal:** Add persistent memory and external service integration using MCP (Model Context Protocol). Agent reads/writes structured data through an MCP server backed by a database.

**Key concepts:**
- MCP server and client architecture
- Persistent conversation history and state checkpointing
- Tool abstraction (agent doesn't know/care about the underlying database)
- Supabase as a local Docker-based database
- Multi-container Docker Compose

**Builds on:** Lesson 1

---

### Lesson 3: Distributed Agents in Separate Containers

**Folder:** `examples/03-distributed-agents-communication/`

**Goal:** Split agents into separate Docker containers (simulating different teams), communicate via A2A protocol. Compare direct HTTP vs A2A.

**Key concepts:**
- A2A (Agent-to-Agent) protocol basics
- Agent Cards for capability advertisement
- Separate FastAPI services per agent
- Docker networking (same network, no auth)
- Communication pattern comparison: direct HTTP vs A2A

**Builds on:** Lessons 1-2

---

### Security + Discovery (Lessons 4-5): Cross-Network

These lessons introduce authentication and discovery for agents that cross trust boundaries.

---

### Lesson 4: Cross-Network Authentication with Auth0

**Folder:** `examples/04-cross-network-authentication/`

**Goal:** Secure agent-to-agent communication across separate Docker networks using Auth0 as a shared OIDC provider.

**Key concepts:**
- OIDC / OAuth 2.0 fundamentals for M2M communication
- Auth0 configuration (free tier)
- JWT token flow: request, pass, validate
- FastAPI JWT validation middleware
- Separate Docker networks simulating different clusters

**Builds on:** Lesson 3

---

### Lesson 5: Agent Discovery in Enterprise Environments

**Folder:** `examples/05-agent-discovery/`

**Goal:** Implement and compare three agent discovery patterns for enterprise environments.

**Key concepts:**
- Explicit/static discovery (hardcoded URLs)
- Shared registry (central catalog service)
- A2A Agent Cards (`.well-known/agent-card.json` + registry scan)
- Enterprise trade-offs: governance, versioning, deprecation
- Building a simple agent registry service

**Builds on:** Lessons 3-4

---

### Production (Lessons 6-8): Cloud + UI

These lessons take the local Docker setup to production with Azure, add a UI, and combine everything.

---

### Lesson 6: Azure Deployment and Infrastructure as Code

**Folder:** `examples/06-azure-deployment/`

**Goal:** Deploy distributed agents to Azure using Infrastructure as Code (Bicep) with automated CI/CD.

**Key concepts:**
- Infrastructure as Code (IaC) introduction with Azure Bicep
- Azure services: Container Registry, Container Apps, Key Vault, Log Analytics
- Bicep templates from scratch
- GitHub Actions deployment workflow
- Deploying the Lesson 3 distributed agents to Azure

**Builds on:** Lesson 5

---

### Lesson 7: Chat UI and Full Observability

**Folder:** `examples/07-ui-and-observability/`

**Goal:** Build a simple chat UI and integrate comprehensive observability with LangSmith and OpenTelemetry.

**Key concepts:**
- Simple chat interface (text input, streamed responses)
- LangSmith dashboard: trace viewer, latency, error rates
- OpenTelemetry for infrastructure metrics
- Vercel deployment for the frontend
- Azure backend + Vercel frontend architecture

**Builds on:** Lesson 6

---

### Lesson 8: Full Stack Integration

**Folder:** `examples/08-full-stack-integration/`

**Goal:** Combine all patterns into a production-ready reference architecture.

**Key concepts:**
- End-to-end flow: UI -> orchestrator -> specialized agents -> auth -> results
- All protocols working together: MCP for tools, A2A for agent communication
- Auth0 for cross-service authentication
- Full Azure deployment with monitoring
- Production checklist and best practices

**Builds on:** All previous lessons

---

## Phase 2: Conversational Tutoring System (Planned)

See [phase2/README.md](phase2/README.md) for the detailed plan. Phase 2 applies all Phase 1 patterns to a real-world distributed system for conversational tutoring with multi-team agent collaboration.

---

## Deliverables Per Lesson

1. Working code example (`docker compose up` to run)
2. Lesson document in `docs/lessons/` (PDF-printable)
3. LinkedIn post draft
4. Blog post outline for ai.ksopyla.com
5. CHANGELOG entry
