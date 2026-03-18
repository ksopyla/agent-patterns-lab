---
name: langgraph-example-implementation
description: >-
  Generates LangChain/LangGraph/FastAPI application code for pattern examples.
  Use when creating or refactoring `examples/*/src` and `examples/*/tests`
  files, especially agent state, agent nodes, graph wiring, FastAPI apps, and
  test structure for LangGraph-based examples.
---

# LangGraph Example Implementation

## When to Use

Trigger this skill when:
- Creating `src/` code for a new example
- Adding or refactoring LangGraph agent nodes
- Wiring `StateGraph` flows
- Building FastAPI wrappers around LangGraph graphs
- Adding tests for example agent pipelines

This skill focuses on code. For example folder layout, Docker files, and README
scaffolding, use [`../example-scaffolder/SKILL.md`](../example-scaffolder/SKILL.md).

## Core Rules

- Use `agent_common.config`, `agent_common.llm`, and `agent_common.tracing` from `libs/common`
- Do not create example-local provider config modules when shared config already exists
- Keep all agent nodes `async def`
- Use typed state via `TypedDict` or Pydantic models
- Use `verbose_log()` in meaningful places
- Use FastAPI `lifespan` instead of startup/shutdown decorators
- Expose `/health` returning `{"status": "ok"}`
- Keep tests split into `unit`, `api`, and `e2e`

## Typical `src/` Layout

```text
src/
├── __init__.py
├── app.py
└── agents/
    ├── __init__.py
    ├── state.py
    ├── graph.py
    ├── [agent_node_1].py
    └── [agent_node_2].py
```

Add extra modules only when the pattern requires them, e.g.:
- `mcp_setup.py` for MCP-backed examples
- `memory.py` for persistence examples
- `a2a_client.py` or `agent_card.py` for distributed examples

## State Template

Prefer a dedicated `state.py` module:

```python
from __future__ import annotations

from typing import Required, TypedDict


class AgentState(TypedDict, total=False):
    input: Required[str]
    plan: str
    findings: str
    report: str
```

Guidance:
- Use `Required[...]` for fields the entrypoint must provide
- Keep field names business-oriented and easy to inspect in traces
- Do not overload state with framework-specific objects unless necessary

## Agent Node Template

```python
from __future__ import annotations

from agent_common.llm import get_chat_model
from agent_common.tracing import verbose_log
from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.state import AgentState

SYSTEM_PROMPT = """\
You are a specialized research agent.
Return concise, structured output.
"""


async def agent_node(state: AgentState) -> dict[str, str]:
    user_input = state["input"]
    verbose_log("AgentName", f"Processing: {user_input[:100]}")

    llm = get_chat_model()
    response = await llm.ainvoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_input),
        ]
    )

    output = str(response.content)
    verbose_log("AgentName", f"Completed ({len(output)} chars)")
    return {"findings": output}
```

Guidance:
- Keep one clear responsibility per node
- Return only the state updates produced by that node
- If the node uses tools, log both the action and a concise outcome
- Catch provider/tool failures only when graceful degradation is part of the example goal

## Graph Template

```python
from __future__ import annotations

from typing import TYPE_CHECKING

from langgraph.graph import END, StateGraph

from src.agents.agent_node import agent_node
from src.agents.state import AgentState

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph


def build_graph() -> CompiledStateGraph:  # type: ignore[type-arg]
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.set_entry_point("agent")
    graph.add_edge("agent", END)
    return graph.compile()
```

Guidance:
- Put graph wiring in one place
- Use stable node names; tests and traces rely on them
- Prefer explicit edges over clever abstractions in learning examples

## FastAPI App Template

```python
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from agent_common.tracing import setup_tracing, verbose_log
from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.agents.graph import build_graph


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncIterator[None]:
    setup_tracing()
    fastapi_app.state.graph = build_graph()
    verbose_log("System", "FastAPI application started")
    yield
    verbose_log("System", "FastAPI application shutting down")


app = FastAPI(title="Pattern NN: [Title]", lifespan=lifespan)


class RunRequest(BaseModel):
    input: str = Field(min_length=3, max_length=500)


class RunResponse(BaseModel):
    report: str


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/run", response_model=RunResponse)
async def run(request: RunRequest) -> RunResponse:
    verbose_log("System", f"Received request: {request.input[:100]}")
    result = await app.state.graph.ainvoke({"input": request.input})
    return RunResponse(report=result.get("report", ""))
```

Guidance:
- Build the graph once in `lifespan` unless the example is explicitly about dynamic graph construction
- Keep request/response schemas explicit
- Add structured error handling when the pattern needs resilience or external dependencies

## Tool and MCP Guidance

- For direct tools, keep the tool setup inside the node that owns it
- For MCP-based tools, isolate connection lifecycle in a dedicated module
- Use compose `command:` overrides to run extra services from the same image when only the entrypoint changes

## Test Strategy

Create all three test layers for changed examples:

### `tests/unit/`
- Test each agent node with mocked LLM/tool behavior
- Assert prompt inputs when useful
- Keep tests deterministic and provider-free

### `tests/api/`
- Test `/health`
- Test request validation
- Mock `build_graph()` or `app.state.graph`
- Assert response schema and payload mapping

### `tests/e2e/`
- Stub node functions and compile the real graph
- Assert node order and state handoff
- Verify final output contains all expected pieces

## Minimal Test Templates

```python
def test_health_endpoint_returns_ok() -> None:
    ...
```

```python
@pytest.mark.asyncio
async def test_graph_executes_nodes_in_order(...) -> None:
    ...
```

## Checklist

- [ ] State lives in a dedicated module
- [ ] Every node is `async def`
- [ ] `verbose_log()` is used in app and nodes
- [ ] FastAPI uses `lifespan`
- [ ] `/health` exists
- [ ] `build_graph()` is easy to test in isolation
- [ ] `unit`, `api`, and `e2e` tests exist
- [ ] No live LLM calls occur in tests
