---
name: agent-patterns-advisor
description: >-
  Recommends agent architecture patterns, communication protocols, and reviews agent code.
  Use when choosing between orchestrator/supervisor/mesh/swarm patterns, deciding on A2A vs MCP
  vs direct HTTP, reviewing agent code for best practices, or discussing distributed agent
  architecture, fault tolerance, and communication patterns.
---

# Agent Patterns Advisor

## Architecture Pattern Selection

When the user describes a multi-agent problem, recommend the right pattern:

| Pattern | When to Use | Trade-offs |
|---------|-------------|------------|
| **Orchestrator** | Central coordinator delegates to specialized agents. Clear workflow. | Single point of failure, but simple to reason about |
| **Supervisor** | Like orchestrator but monitors/evaluates/corrects worker output | More overhead, better quality control |
| **Mesh/P2P** | Agents communicate directly, no central coordinator | Hard to debug, good for loosely coupled systems |
| **Swarm** | Agents self-organize, emergent behavior | Unpredictable, good for exploration tasks |
| **Pipeline** | Sequential processing, each agent transforms output | Simple, but rigid ordering |
| **Router** | Single agent dispatches to the right specialist | Good for fan-out, criteria-based routing |

## Protocol Decision Matrix

| Need | Protocol | Why |
|------|----------|-----|
| Agent calls a tool, API, or database | **MCP** | Standardized tool interface, stateless |
| Agent talks to another agent | **A2A** | Peer discovery, multi-turn, Agent Cards |
| Agent needs to be discovered by unknown agents | **A2A** | `.well-known/agent-card.json` |
| Simple request-response between known agents | **Direct HTTP/gRPC** | Lower overhead if discovery not needed |
| Agent needs stateful multi-turn with another agent | **A2A** | contextId + taskId for thread tracking |
| Real-time streaming between agents | **A2A (SSE)** | `message/stream` method |

## Communication Pattern Evaluation

When reviewing or designing agent communication, evaluate:

- **Synchronous vs Asynchronous**: sync is simpler but blocks; async scales better
- **Request-Response vs Event-Driven**: R-R for queries, events for notifications
- **Pub-Sub vs Point-to-Point**: pub-sub for broadcasting, P2P for targeted messages
- **Streaming vs Batch**: streaming for real-time UX, batch for throughput

## Code Review Checklist

When reviewing agent code in `examples/`, check:

1. **State management**: Is state typed (TypedDict/Pydantic)? Is it minimal?
2. **Error handling**: Does the agent handle tool failures gracefully? Retry logic?
3. **Separation of concerns**: Is agent logic separate from transport (FastAPI)?
4. **Idempotency**: Can the same message be processed twice safely?
5. **Verbose logging**: Does it support `VERBOSE=true`?
6. **LangSmith tracing**: Is tracing wired up via `agent_common.tracing`?
7. **Health check**: Does the FastAPI app have `/health`?

## Distributed Systems Concerns

For lessons 3+ (multi-container), also check:
- **Network failures**: What happens if an agent is unreachable?
- **Timeouts**: Are HTTP calls to other agents configured with timeouts?
- **Circuit breaker**: Should repeated failures stop calling a downstream agent?
- **Message ordering**: Does the system depend on message order? If so, how is it guaranteed?
