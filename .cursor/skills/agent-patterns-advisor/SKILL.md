---
name: agent-patterns-advisor
description: >-
  Chooses agent architecture, service boundaries, and communication protocols.
  Use when planning or reviewing LangGraph/FastAPI systems, selecting between
  single-graph, pipeline, orchestrator, router, supervisor, mesh, or swarm
  patterns, deciding between A2A, MCP, and direct HTTP, or evaluating async,
  streaming, and background-work trade-offs.
---

# Agent Patterns Advisor

## Responsibility

This skill owns architecture decisions and architectural reviews.

Use it to:
- choose the simplest viable agent pattern
- define service boundaries and agent responsibilities
- decide between A2A, MCP, direct HTTP, and workers or queues
- review distributed designs for protocol fit, resilience, and operability

Do not use it to:
- scaffold folders, Docker files, or READMEs; use [`../example-scaffolder/SKILL.md`](../example-scaffolder/SKILL.md)
- write most `examples/*/src` implementation code; use [`../langgraph-example-implementation/SKILL.md`](../langgraph-example-implementation/SKILL.md)
- own the test plan or detailed test implementation; use [`../tester/SKILL.md`](../tester/SKILL.md)

## Operating Principles

- Prefer the simplest architecture that satisfies the requirement.
- Keep each agent focused on one responsibility with minimal state.
- Keep transport layers thin; business logic belongs in LangGraph or domain modules.
- Optimize for debuggability, testability, and failure isolation before sophistication.

## Default Escalation Path

Start here unless the user gives a strong reason not to:
1. Single graph or pipeline in one service.
2. Router or orchestrator with specialist agents in one service.
3. Supervisor only when explicit review or correction is required.
4. Distributed agents with A2A only when services must be independently deployed, discovered, or owned by different teams.
5. Queue or worker only when work must outlive an HTTP request or needs retries, throttling, or backpressure.

## Pattern Selection

| Pattern | Use when | Main trade-off |
|---------|----------|----------------|
| **Single graph** | One workflow can stay in one codebase and one runtime | Least flexible, but the best default |
| **Pipeline** | Steps are sequential and deterministic | Simple, but rigid ordering |
| **Router** | One entry point dispatches to the right specialist | Good for fan-out, but routing quality matters |
| **Orchestrator** | A coordinator plans and delegates to focused workers | Easy to reason about, but centralized |
| **Supervisor** | A coordinator must also evaluate or correct worker output | Better quality control, more latency and complexity |
| **Mesh / P2P** | Agents are loosely coupled peers that must talk directly | Harder to debug and govern |
| **Swarm** | Exploration and emergent collaboration matter more than predictability | Highest uncertainty and operational risk |

## Protocol Selection

- **MCP**: Use for tool, data, and resource access from an agent. This is the right boundary for databases, search, GitHub, filesystem, or exposing a typed workflow as a tool. In LangGraph Agent Server, MCP is exposed at `/mcp` and each request is stateless.
- **A2A**: Use for agent-to-agent collaboration when agents are independently addressable, discoverable, or need multi-turn task coordination. In LangGraph Agent Server, A2A is exposed at `/a2a/{assistant_id}` and supports `message/send`, `message/stream`, and `tasks/get`.
- **Direct HTTP/gRPC**: Use for simple request-response between known services. Prefer this over A2A for tightly coupled internal helpers because it is simpler to debug, test, and operate.
- **Use both when needed**: A2A is the agent boundary; MCP is the tool boundary inside or behind an agent.
- **Do not use A2A** just to wrap a normal CRUD call or a simple internal helper.
- **Do not use MCP** as a substitute for long-lived workflow state or cross-request conversation state.

## A2A Rules

- A2A is for peer agents, not generic tools.
- Preserve `contextId` and `taskId` across turns when a conversation continues.
- For LangGraph A2A compatibility, keep a message-based state with a `messages` key.
- Use Agent Cards for discovery through `/.well-known/agent-card.json`.
- Prefer `message/send` for normal request-response and `message/stream` only when streaming materially improves the UX or coordination flow.

## MCP Rules

- Treat MCP as a typed, stateless tool interface.
- When exposing a LangGraph workflow as an MCP tool, prefer explicit input and output schemas instead of generic `MessagesState`.
- Keep the tool surface small and purposeful; do not leak internal graph state shape unless it is part of the public contract.
- Use MCP when the caller should think "call a capability" rather than "start a conversation with another agent."

## Design Guardrails

- For Python LangGraph apps, prefer a small explicit layout with `pyproject.toml`, `langgraph.json`, `.env`, and focused modules such as `state.py`, `nodes.py`, `tools.py`, and `graph.py` or `agent.py`.
- Check that every deployed graph is registered in `langgraph.json` with clear dependencies and environment configuration.
- Prefer one public graph per clear capability with explicit names and purpose.
- Keep FastAPI, MCP, and A2A as thin boundaries around reusable graph logic.

## Async, Streaming, And Background Work

- Use synchronous request-response only when the example is intentionally simple and the concept is easier to teach that way.
- Prefer async I/O for production-ready, network-bound, or distributed patterns.
- Use streaming intentionally:
  - `updates` for progress and state transitions
  - `messages-tuple` for token streaming from LLM calls
  - `debug` for troubleshooting
- Use a LangGraph or LangSmith thread when the run must persist state. Use stateless streaming only when persistence is not required.
- Use `BackgroundTasks` only for small same-process work after the response.
- If work is heavy, long-running, retryable, or must survive restarts, recommend a real queue or worker instead of `BackgroundTasks`.
- Return `202 Accepted` when work continues asynchronously and the caller does not need the final result immediately.

## Review Checklist

When reviewing or designing an agent system, check:
1. **Pattern fit**: the chosen pattern is the simplest one that meets the requirement.
2. **Service boundaries**: each agent or service has one clear responsibility.
3. **Protocol fit**: A2A, MCP, direct HTTP, and queues are used for the right jobs.
4. **State shape**: public and internal state are typed and minimal.
5. **Failure handling**: timeouts, retries, fallbacks, and idempotency are considered.
6. **Async model**: the design does not block the event loop with heavy work.
7. **Observability**: tracing, verbose logs, and health checks are part of the design.

## Recommendation Format

When advising the user, answer in this order:
1. Recommended pattern and protocol.
2. Why it is the simplest acceptable choice.
3. The main trade-off or operational risk.
4. What would justify moving to a more complex pattern later.

## Resources

- [LangGraph application structure](https://docs.langchain.com/oss/python/langgraph/application-structure)
- [LangSmith A2A endpoint](https://docs.langchain.com/langsmith/server-a2a#a2a-endpoint-in-agent-server)
- [LangSmith MCP endpoint](https://docs.langchain.com/langsmith/server-mcp)
- [LangSmith streaming](https://docs.langchain.com/langsmith/streaming)
- [A2A tutorials](https://a2a-protocol.org/latest/tutorials/)
- [Model Context Protocol intro](https://modelcontextprotocol.io/docs/getting-started/intro)
- [FastAPI background tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
