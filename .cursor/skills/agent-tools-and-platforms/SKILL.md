---
name: agent-tools-and-platforms
description: >-
  Expert on agentic platforms, libraries, and reference materials.
  Use when comparing orchestration frameworks (LangGraph, CrewAI, AutoGen,
  Strands SDK), agent runtimes (OpenClaw, NemoClaw, Hermes Agent, AWS AgentCore),
  memory libraries (Honcho, Mem0, Zep, Letta), voice frameworks (Pipecat,
  LiveKit Agents), durable execution engines (Temporal, Inngest), sandboxing
  (E2B, gVisor), or protocol standards (A2A, MCP, ACP, ANP).
  Also use when looking for research papers, reference implementations,
  or the latest developments in the agentic ecosystem.
---

# Agent Tools and Platforms

## Responsibility

This skill is the **librarian** of the agent ecosystem. It owns knowledge of platforms, libraries, tools, and reference materials.

Use it to:
- compare and recommend orchestration frameworks and agent runtimes
- evaluate memory libraries for specific use cases
- recommend voice/conversation frameworks
- identify the right sandboxing and isolation solution
- find research papers, surveys, and reference implementations
- stay current on the agentic ecosystem
- provide library-specific API guidance and integration advice

Do not use it to:
- make architecture or pattern decisions; use [`../agent-patterns-advisor/SKILL.md`](../agent-patterns-advisor/SKILL.md)
- write code templates or module layouts; use [`../langgraph-example-implementation/SKILL.md`](../langgraph-example-implementation/SKILL.md)
- scaffold folders or Docker files; use [`../example-scaffolder/SKILL.md`](../example-scaffolder/SKILL.md)

---

## Orchestration Frameworks

### LangGraph (LangChain)

The primary framework for this repository. Graph-based agent orchestration with typed state, checkpointing, streaming, human-in-the-loop, and both StateGraph and Functional APIs.

- **Strengths**: most mature graph-based agent framework; first-class persistence, streaming, and interrupts; dual API (StateGraph for visual workflows, Functional for Python-native); LangSmith integration for tracing; A2A and MCP support in Agent Server.
- **Weaknesses**: tied to LangChain ecosystem; learning curve for advanced patterns; checkpointer choice matters for production (MemorySaver is not durable).
- **When to use**: default choice for this repo. Use for all graph-based agent workflows.
- **Version note**: LangGraph 2.0 released February 2026 with Functional API (`@entrypoint`, `@task`), improved persistence, and production-hardened patterns.
- **Docs**: [LangGraph Python docs](https://docs.langchain.com/oss/python/langgraph/), [LangGraph API reference](https://reference.langchain.com/python/langgraph/)
- **Use Context7 MCP** to fetch latest LangGraph documentation during implementation.

### CrewAI

Role-based multi-agent framework with a focus on team collaboration metaphors.

- **Strengths**: intuitive crew/agent/task mental model; built-in delegation and collaboration; easier onboarding for non-graph thinkers.
- **Weaknesses**: less control over execution flow than LangGraph; opinionated about agent roles; limited checkpoint/resume support.
- **When to use**: rapid prototyping of role-based teams; when the "crew" metaphor matches the domain.
- **Docs**: [CrewAI docs](https://docs.crewai.com/)

### AutoGen (Microsoft)

Multi-agent conversation framework with code execution capabilities.

- **Strengths**: strong code execution support; GroupChat for multi-agent conversations; nested conversations; human proxy agent.
- **Weaknesses**: conversation-centric (not graph-centric); limited streaming; complex configuration for production.
- **When to use**: code generation and execution workflows; research prototyping.
- **Docs**: [AutoGen docs](https://microsoft.github.io/autogen/)

### Strands Agents SDK (AWS)

Lightweight agent SDK designed for AWS AgentCore integration.

- **Strengths**: simple Python decorator-based API; native AWS integration; designed for serverless deployment.
- **Weaknesses**: AWS-centric; less community adoption; fewer advanced patterns than LangGraph.
- **When to use**: AWS-native deployments; when AgentCore is the target runtime.
- **Docs**: [Strands SDK on GitHub](https://github.com/strands-agents/sdk-python)

---

## Agent Runtimes and Platforms

### AWS Bedrock AgentCore

Fully managed serverless agent runtime. VM-level session isolation, managed memory, MCP tool integration.

- **Key features**: microVM per session for isolation; scales to thousands of sessions; Cognito auth integration; OpenTelemetry observability; SOC 2 compliant.
- **Orchestration patterns**: Supervisor, Native Collaboration, Agent Squad, LangGraph integration.
- **Cost model**: pay-per-session with managed infrastructure.
- **When to use**: enterprise deployments on AWS requiring managed scaling, isolation, and compliance.
- **Docs**: [AgentCore docs](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-core.html)
- **Reference**: [Multi-agent orchestration guide on AWS](https://aws.amazon.com/solutions/guidance/multi-agent-orchestration-on-aws)

### OpenClaw

Open-source agent framework with 332K+ GitHub stars (as of 2025). Runs agents with broad system-level capabilities.

- **Key features**: persistent agents; cron-based scheduled tasks; multi-channel messaging (Telegram, Slack, Discord); file-based identity (MEMORY.md, SOUL.md); 40+ built-in tools.
- **Long-running**: supports always-on deployment with isolated sessions; 5-20 daily cron jobs; $3-15/day operational cost.
- **Security posture**: runs with unrestricted permissions by default. Not suitable for untrusted environments without additional sandboxing.
- **When to use**: personal/developer agents; rapid prototyping of autonomous agents; when broad system access is acceptable.
- **Docs**: [OpenClaw GitHub](https://github.com/OpenClaw)

### NemoClaw (NVIDIA)

NVIDIA's enterprise wrapper around OpenClaw, announced at GTC 2026.

- **Key features**: runs OpenClaw inside NVIDIA's OpenShell sandbox; resource limits (CPU, memory, time); controlled network egress; audit logging; operator-approved tool access.
- **Long-running**: designed for "always-on assistants" with enterprise security controls.
- **Hardware**: requires NVIDIA hardware ($2K-$50K investment); software is free.
- **When to use**: enterprise deployments requiring sandboxed autonomous agents with NVIDIA hardware.
- **Docs**: [NemoClaw overview](https://docs.nvidia.com/nemoclaw/latest/about/overview.html)

### Hermes Agent (Nous Research)

Autonomous agent that persists on servers and grows more capable over time.

- **Architecture**: Agent Loop (synchronous orchestration), Prompt System (builder, caching, context compression), Session Persistence (SQLite with lineage), Gateway (multi-platform messaging), Tooling Runtime (40+ tools).
- **Long-running**: scheduled automations via natural language cron; multi-platform deployment (Docker, SSH, Modal); learning loop with autonomous skill creation; subagent delegation with isolated conversations.
- **Evolving**: multi-agent architecture in development (coordinator, researcher, developer, reviewer roles with dependency-aware DAGs).
- **When to use**: personal autonomous agents that learn and grow; when agent identity persistence matters.
- **Docs**: [Hermes Agent docs](https://hermes-agent.nousresearch.com/docs/)

### LangGraph Platform / Agent Server

LangGraph's hosted runtime with built-in A2A and MCP endpoints.

- **Key features**: `/a2a/{assistant_id}` for A2A communication; `/mcp` for MCP tool exposure; managed checkpointing and streaming; cron-based background runs.
- **When to use**: when deploying LangGraph agents as discoverable services with standard protocol support.
- **Docs**: [LangGraph Platform](https://docs.langchain.com/langsmith/server-overview)

---

## Memory Libraries

### Decision Matrix

| Library | Architecture | Best for | Benchmark (LoCoMo) | Cost model |
|---------|-------------|----------|--------------------|----|
| **Honcho** | Peer-centric with reasoning-triggered representations | Multi-agent shared state, cross-session context | 90.4% | Open-source + managed service |
| **Mem0** | Extraction-update pipeline with vector + optional graph | Bolt-on memory for existing agents, fast integration | ~66% (independent) | Free tier + Pro ($249/mo) |
| **Zep (Graphiti)** | Temporal knowledge graph | Fact changes over time, temporal reasoning | ~85% | Open-source + Cloud |
| **Letta (MemGPT)** | Three-tier OS (core/recall/archival) | Full agent runtime with built-in memory management | ~83% | Open-source + Cloud |



### Honcho

- **Architecture**: Workspaces → Peers → Sessions → Messages. Background reasoning generates "representations" (conclusions about each peer). Supports many-to-many peer relationships.
- **Unique strength**: treats humans and agents as equal peers; local and global representations; multi-agent group scenarios.
- **Integration**: REST API, Python SDK. Store session data, query representations for context.
- **Docs**: [Honcho docs](https://docs.honcho.dev/)

### Mem0

- **Architecture**: two-phase pipeline (extraction → update). Combines vector database with optional knowledge graph (Pro tier).
- **Unique strength**: easiest integration path; managed infrastructure; 91% faster responses than full-context loading.
- **Caveat**: knowledge graph features gated behind Pro tier ($249/month). Independent benchmarks show lower accuracy than self-reported.
- **Docs**: [Mem0 docs](https://docs.mem0.ai/)

### Zep (Graphiti)

- **Architecture**: temporal knowledge graph where every fact carries explicit time metadata with validity windows.
- **Unique strength**: temporal reasoning. "X was true from January to March, then Y became true." Best for domains where facts change over time.
- **Integration**: Python SDK, REST API. Built on Neo4j graph database.
- **Docs**: [Zep docs](https://help.getzep.com/)

### Letta (formerly MemGPT)

- **Architecture**: agent runtime with three memory tiers inspired by OS design. Core memory (context window), recall memory (searchable conversation history), archival memory (vector DB).
- **Unique strength**: the agent itself manages its memory (decides what to store, retrieve, and forget). Not a bolt-on service but a complete runtime.
- **Caveat**: adopting Letta means adopting its runtime. Less flexible if you already have a LangGraph agent.
- **Docs**: [Letta docs](https://docs.letta.com/)

### LangGraph Built-in (BaseStore + Checkpointer)

- **Architecture**: `BaseStore` for cross-thread key-value storage with namespaces and vector search. Checkpointer for thread-level persistence.
- **Unique strength**: zero additional dependencies; native integration with graph execution; namespace-based scoping.
- **When to prefer**: when memory needs are straightforward (store facts, retrieve by key or similarity) and you do not need temporal reasoning or automatic fact extraction.
- **Docs**: [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence)

### Other Notable Libraries

- **EverMemOS**: highest LoCoMo score (92.3%) but limited production adoption.
- **Hindsight**: strong benchmark performance (89.6%), replay-based memory.
- **Memvid**: video-centric memory for multimodal agents.

---

## Voice and Conversation Frameworks

### Pipecat (Daily.co)

Open-source Python framework for real-time voice and multimodal agents. 8,900+ GitHub stars.

- **Architecture**: frame-based pipeline (AudioFrame, TextFrame, control signals flow through processors). VAD → STT → LLM → TTS pipeline with automatic interruption handling.
- **Key features**: 40+ provider integrations; transport-agnostic (WebRTC via Daily/LiveKit, WebSocket); modular processor swapping.
- **When to use**: building custom voice agent pipelines with maximum control over the audio processing chain.
- **Docs**: [Pipecat docs](https://docs.pipecat.ai/)

### LiveKit Agents

Real-time communication platform with agent framework built on WebRTC.

- **Architecture**: agents join rooms as headless participants; subscribe to human tracks; publish audio responses.
- **Key features**: multi-participant support; data channels; room management; built-in STT/TTS integrations.
- **When to use**: when you need robust WebRTC infrastructure and multi-participant voice scenarios.
- **Docs**: [LiveKit Agents docs](https://docs.livekit.io/agents/)

### Deepgram

Speech AI platform with Nova-3 STT (~90ms latency) and Flux for ultra-low-latency turn detection.

- **Key features**: streaming STT; model-integrated end-of-turn detection; voice agent API.
- **When to use**: as a component in Pipecat or custom pipelines when you need the fastest STT.
- **Docs**: [Deepgram docs](https://developers.deepgram.com/docs/)

### OpenAI Realtime API

Speech-to-speech model (gpt-4o-realtime-preview) with native audio understanding.

- **Key features**: direct audio-in/audio-out; emotional awareness; function calling from voice.
- **Caveat**: cloud-only; higher cost; limited model selection.
- **When to use**: when emotional nuance and native audio understanding matter more than cost or self-hosting.
- **Docs**: [OpenAI voice agents guide](https://platform.openai.com/docs/guides/voice-agents)

### Integration with Agent Systems

The typical integration pattern for voice + agents:

1. Voice pipeline (Pipecat/LiveKit) handles real-time audio processing.
2. Complex tasks are delegated to LangGraph agent services via HTTP or A2A.
3. Agent returns structured result; voice pipeline synthesizes spoken response.
4. Use SSE or polling for async result retrieval.

For architecture patterns, see the Voice-to-Agent Delegation section in [`../agent-patterns-advisor/SKILL.md`](../agent-patterns-advisor/SKILL.md).

---

## Durable Execution Engines

### Temporal

Durable workflow execution platform. Workflows survive process crashes, restarts, and infrastructure failures.

- **Key concept**: workflows and activities. Workflows define the orchestration logic; activities perform the actual work (API calls, LLM invocations). Activities are retried automatically on failure.
- **Agent relevance**: "AI agents are distributed systems on steroids." Temporal handles retries, timeouts, cancellation, and human pauses natively.
- **When to use over LangGraph checkpointer**: when you need guaranteed execution across multi-service workflows; when retry and timeout policies must be configurable per-activity; when work must survive multi-day human pauses.
- **Docs**: [Temporal docs](https://docs.temporal.io/), [Durable Execution meets AI](https://temporal.io/blog/durable-execution-meets-ai-why-temporal-is-the-perfect-foundation-for-ai)

### Inngest

Event-driven durable execution. Functions are triggered by events and automatically retried.

- **Key concept**: step functions with automatic checkpointing. Each step is individually retried on failure.
- **When to use**: serverless deployments; event-driven agent coordination; when you want durable execution without managing Temporal infrastructure.
- **Docs**: [Inngest docs](https://www.inngest.com/docs)

---

## Sandboxing and Isolation Solutions

### E2B

Cloud sandbox platform for AI agent code execution. Ephemeral Linux VMs with pre-installed runtimes.

- **Key features**: sub-second VM startup; pre-built templates for Python, Node.js; filesystem and network isolation; programmatic API.
- **When to use**: model-generated code execution; notebook-style agent workflows; when you need isolated environments per execution.
- **Docs**: [E2B docs](https://e2b.dev/docs)

### gVisor (Google)

Application kernel that intercepts and implements Linux syscalls, reducing the attack surface for containerized workloads.

- **Key features**: syscall-level isolation without full VM overhead; compatible with Docker and Kubernetes (runsc runtime).
- **When to use**: medium-to-high risk tool execution where container isolation is not sufficient but microVMs are overkill.
- **Docs**: [gVisor docs](https://gvisor.dev/docs/)

### Firecracker (AWS)

Lightweight microVM technology. Sub-second boot times with hardware-level isolation.

- **Key features**: minimal attack surface; used by AWS Lambda and Fargate; ~5ms boot time.
- **When to use**: high-risk agent execution requiring VM-level isolation with container-like performance.
- **Reference**: [Firecracker paper](https://arxiv.org/abs/2005.12821)

### WASM Sandboxing

WebAssembly-based sandboxing for agent workflows. Runs untrusted code in a browser-like sandbox.

- **When to use**: generated-code execution; artifact rendering; when you need sandboxing without VMs.
- **Reference**: [NVIDIA WASM sandboxing blog](https://developer.nvidia.com/blog/sandboxing-agentic-ai-workflows-with-webassembly/)

---

## Protocol Standards

### MCP (Model Context Protocol) -- Anthropic

Standard for agent-to-tool and agent-to-data communication. 97M+ monthly SDK downloads as of Feb 2026.

- **Use for**: tool execution, data access, resource queries. Stateless, typed, JSON-RPC 2.0.
- **Enterprise extensions**: OAuth Client Credentials, Enterprise-Managed Authorization.
- **Docs**: [MCP spec](https://modelcontextprotocol.io/), [MCP auth extensions](https://modelcontextprotocol.io/extensions/auth/)

### A2A (Agent-to-Agent) -- Google / Linux Foundation

Standard for agent-to-agent collaboration. Backed by 100+ companies including AWS, Microsoft, Salesforce.

- **Use for**: agent delegation, task coordination, artifact exchange, capability discovery.
- **Key concepts**: Agent Cards, Tasks, Artifacts, SSE streaming, push notifications.
- **Docs**: [A2A spec](https://a2a-protocol.org/), [A2A tutorials](https://a2a-protocol.org/latest/tutorials/)

### ACP (Agent Communication Protocol)

Alternative agent communication protocol with broader message types.

- **Status**: less adoption than A2A. Monitor but do not build on it yet.
- **Docs**: [BeeAI ACP](https://docs.beeai.dev/)

### ANP (Agent Networking Protocol)

Protocol focused on agent networking and discovery at internet scale.

- **Status**: early stage. Relevant for future distributed directory designs.

---

## Research Papers and Surveys

### Must-Read Papers

| Paper | Why it matters |
|-------|---------------|
| [A Survey of Agent Interoperability Protocols](https://huggingface.co/papers/2505.02279) | Comprehensive comparison of MCP, A2A, ACP, ANP across interaction modes |
| [Survey of LLM-Driven Agent Communication](https://huggingface.co/papers/2506.19676) | Security risks and defense strategies for agent communication |
| [Evolution of AI Agent Registry Solutions](https://arxiv.org/html/2508.03095v2) | Compares MCP Registry, A2A Agent Cards, AGNTCY ADS, Microsoft Entra Agent ID, NANDA |
| [VoiceAgentRAG: Dual-Agent Architecture](https://arxiv.org/abs/2603.02206v2) | Solves RAG latency in voice agents with fast/slow agent separation |
| [Building Enterprise Realtime Voice Agents](https://arxiv.org/abs/2603.05413) | End-to-end tutorial for self-hosted voice agent pipelines |
| [OAuth for AI Agents IETF Draft](https://datatracker.ietf.org/doc/html/draft-oauth-ai-agents-on-behalf-of-user-01) | Emerging standard for agent delegation and user consent |

### Engineering Blogs

| Source | Topic |
|--------|-------|
| [Microsoft Zero-Trust Agents](https://techcommunity.microsoft.com/blog/azure-ai-services-blog/zero-trust-agents-adding-identity-and-access-to-multi-agent-workflows/4427790) | Agent identity and access control in multi-agent workflows |
| [Auth0 Token Vault for AI Agents](https://auth0.com/blog/auth0-token-vault-secure-token-exchange-for-ai-agents/) | Secure token exchange and delegation for agents |
| [OpenAI: Resisting Prompt Injection](https://openai.com/index/designing-agents-to-resist-prompt-injection) | Defense patterns for agent security |
| [Temporal: Durable Execution meets AI](https://temporal.io/blog/durable-execution-meets-ai-why-temporal-is-the-perfect-foundation-for-ai) | Why agents need durable execution |
| [A2A + MCP Hybrid Architecture](https://jangwook.net/en/blog/en/a2a-mcp-hybrid-architecture-production-guide/) | Production deployment of both protocols together |
| [AGNTCY Agent Directory Service](https://docs.agntcy.org/dir/overview/) | Distributed agent discovery with capability search |

---

## Staying Current

### Where to Find the Latest

| Source | What you get | URL |
|--------|-------------|-----|
| LangGraph changelog | Framework updates, new APIs, breaking changes | [GitHub releases](https://github.com/langchain-ai/langgraph/releases) |
| LangChain blog | New patterns, integrations, tutorials | [blog.langchain.dev](https://blog.langchain.dev/) |
| Hugging Face Papers | Latest research on agent interoperability and communication | [huggingface.co/papers](https://huggingface.co/papers) |
| A2A protocol repo | Spec changes, new tutorials, community examples | [a2a-protocol.org](https://a2a-protocol.org/) |
| MCP spec repo | Protocol updates, new auth extensions | [modelcontextprotocol.io](https://modelcontextprotocol.io/) |
| ArXiv cs.AI | Research papers on agent architectures | [arxiv.org/list/cs.AI](https://arxiv.org/list/cs.AI/recent) |
| Context7 MCP | Fetch up-to-date library documentation within this workspace | Use the `context7` MCP server |

### How to Verify Information

This skill contains knowledge compiled as of March 2026. The agentic ecosystem moves fast. When advising:

1. **Check versions**: always verify the LangGraph version and available APIs before recommending specific primitives.
2. **Use Context7**: fetch latest library docs via the Context7 MCP server for current API details.
3. **Search when uncertain**: use web search for platforms or libraries with rapid release cycles.
4. **Flag staleness**: if a recommendation is based on a version older than 6 months, flag it and suggest the user verify.

---

## Library Selection Quick Guide

| Need | Recommended | Runner-up |
|------|-------------|-----------|
| Agent orchestration (this repo) | **LangGraph** | Temporal (for durable execution) |
| Agent memory (simple) | **LangGraph BaseStore** | Mem0 (bolt-on) |
| Agent memory (temporal reasoning) | **Zep / Graphiti** | Honcho |
| Agent memory (multi-agent shared) | **Honcho** | LangGraph BaseStore |
| Agent memory (full runtime) | **Letta** | Hermes Agent |
| Voice pipeline | **Pipecat** | LiveKit Agents |
| Speech-to-text | **Deepgram Nova-3** | OpenAI Whisper |
| Code execution sandbox | **E2B** | gVisor |
| Durable execution | **Temporal** | Inngest |
| Agent-to-agent protocol | **A2A** | Direct HTTP (internal) |
| Agent-to-tool protocol | **MCP** | Direct function calls |
| Long-running autonomous agent | **Hermes Agent** | OpenClaw + NemoClaw |
| Enterprise managed runtime | **AWS AgentCore** | LangGraph Platform |
