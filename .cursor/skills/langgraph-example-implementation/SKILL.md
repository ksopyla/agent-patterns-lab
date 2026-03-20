---
name: langgraph-example-implementation
description: >-
  Implements LangGraph/FastAPI example application code under `examples/*/src`.
  Use when creating or refactoring typed state, nodes, graph wiring, FastAPI
  entrypoints, or MCP/A2A integration modules after the architecture is chosen.
  Use `agent-patterns-advisor` for architecture decisions, `tester` for tests,
  and `example-scaffolder` for folder, Docker, and README scaffolding.
---

# LangGraph Example Implementation

## Responsibility

This skill owns runnable example application code.

Use it to:
- implement or refactor `examples/*/src`
- define typed state, nodes, tools, graph wiring, and transport adapters
- build FastAPI apps, request or response schemas, and runtime setup
- update `langgraph.json` when the public graph surface changes

Do not use it to:
- choose architecture or service boundaries from scratch; use [`../agent-patterns-advisor/SKILL.md`](../agent-patterns-advisor/SKILL.md)
- scaffold new example folders, Docker files, or READMEs; use [`../example-scaffolder/SKILL.md`](../example-scaffolder/SKILL.md)
- own the test plan or detailed test implementation; use [`../tester/SKILL.md`](../tester/SKILL.md)

## Implementation Workflow

1. Confirm the chosen pattern and protocol.
2. Define minimal typed state and explicit public schemas.
3. Implement focused nodes or tools.
4. Wire the graph in one module.
5. Add the FastAPI or transport boundary.
6. Register or update deployed graphs in `langgraph.json` if needed.
7. Hand off to [`../tester/SKILL.md`](../tester/SKILL.md) for test updates and verification.

## Core Rules

- Use `agent_common.config`, `agent_common.llm`, and `agent_common.tracing` from `libs/common`
- Do not create example-local provider config modules when shared config already exists
- Keep all agent nodes `async def`
- Use typed state via `TypedDict` or Pydantic models
- Keep public request and response schemas explicit
- Use `verbose_log()` in meaningful places
- Keep one shared `LANGSMITH_PROJECT` across the repo and differentiate examples with run tags and metadata, not extra per-example env vars
- For public graph entrypoints, pass a `build_langsmith_run_config(...)` result into `invoke()` or `ainvoke()`
- Use FastAPI `lifespan` instead of startup/shutdown decorators
- Expose `/health` returning `{"status": "ok"}`
- Keep modules focused and easy to test in isolation

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
- `schemas.py` for shared request or response models when they grow beyond one file

Add root runtime files only when the example needs them:
- `langgraph.json` to register graphs, dependencies, and env
- `.env.example` for required local configuration
- `pyproject.toml` updates when the example runtime surface changes

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
- Keep internal graph state separate from public API schemas when those concerns differ

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
- Keep prompts, parsing, and tool orchestration inside the node or its helper module, not in FastAPI handlers

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
- Prefer `build_graph()` or `create_graph()` helpers that can be compiled cleanly in tests

## FastAPI App Template

```python
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from agent_common.tracing import build_langsmith_run_config, setup_tracing, verbose_log
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


def _run_config() -> dict[str, object]:
    return build_langsmith_run_config(
        example_name="NN-name",
        pattern_slug="pattern-slug",
        run_name="pattern-nn-run",
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/run", response_model=RunResponse)
async def run(request: RunRequest) -> RunResponse:
    verbose_log("System", f"Received request: {request.input[:100]}")
    result = await app.state.graph.ainvoke(
        {"input": request.input},
        config=_run_config(),
    )
    return RunResponse(report=result.get("report", ""))
```

Guidance:
- Build the graph once in `lifespan` unless the example is explicitly about dynamic graph construction
- Keep request/response schemas explicit
- Keep LangSmith project selection simple: reuse the repo-wide `LANGSMITH_PROJECT` and rely on tags plus metadata for per-example filtering
- Include stable tags such as `example:...`, `pattern:...`, `env:...`, `runtime:...`, and `provider:...`
- Add structured error handling when the pattern needs resilience or external dependencies
- Keep endpoint handlers thin; they should validate, call the graph or service layer, and map output

## Protocol-Specific Notes

- For direct tools, keep setup inside the node or helper module that owns the capability.
- For MCP-based tools, isolate client or connection lifecycle in a dedicated module and prefer explicit typed schemas for exposed workflows.
- For A2A-compatible agents, keep message-based state with a `messages` key and isolate transport-specific request or response handling at the boundary.
- Add streaming only when the example is explicitly about streaming or the UX needs incremental progress.
- Use compose `command:` overrides to run extra services from the same image when only the entrypoint changes.

## Testing Handoff

Whenever code changes under `examples/` or `libs/`, invoke [`../tester/SKILL.md`](../tester/SKILL.md).

This skill should keep the implementation testable by:
- keeping `build_graph()` or `create_graph()` isolated from FastAPI setup
- using stable node names
- avoiding heavy module-level side effects at import time
- keeping dependency seams easy to mock
- not embedding test strategy details here; the `tester` skill owns them

## Checklist

- [ ] Architecture choice is already clear before implementation starts
- [ ] State lives in a dedicated module
- [ ] Public schemas are explicit
- [ ] Every node is `async def`
- [ ] `verbose_log()` is used in app and nodes
- [ ] FastAPI uses `lifespan`
- [ ] `/health` exists
- [ ] `build_graph()` is easy to test in isolation
- [ ] `langgraph.json` is updated when the exposed graph surface changes
- [ ] Testing work has been handed off to `tester`
