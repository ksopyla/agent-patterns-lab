---
name: example-scaffolder
description: >-
  Generates boilerplate for new example folders with consistent structure.
  Use when creating a new example, starting a new lesson, or scaffolding
  a new agent service within an example.
---

# Example Scaffolder

## When to Use

Trigger this skill when:
- Creating a new `examples/NN-name/` folder
- Starting work on a new lesson
- Adding a new agent service to an existing example

## Folder Structure

Every example must have this structure:

```
examples/NN-name/
├── pyproject.toml
├── README.md
├── docker-compose.yml
├── src/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   └── [agent_name].py
│   ├── app.py              # FastAPI application
│   └── config.py           # Settings and env var loading
└── tests/
    ├── unit/
    │   └── test_*.py
    ├── api/
    │   └── test_*.py
    └── e2e/
        └── test_*.py
```

## pyproject.toml Template

```toml
[project]
name = "example-NN-name"
version = "0.1.0"
description = "Lesson N: [Title]"
requires-python = ">=3.12"
dependencies = [
    "langgraph>=0.4",
    "langchain-openai>=0.3",
    "langchain-anthropic>=0.3",
    "langsmith>=0.3",
    "fastapi>=0.115",
    "uvicorn>=0.34",
    "pydantic>=2.0",
    "httpx>=0.28",
    "agent-common",
]

[tool.uv.sources]
agent-common = { workspace = true }
```

Add additional dependencies as needed per lesson (e.g., `supabase` for Lesson 2, `python-jose` for Lesson 4).

## docker-compose.yml Template

```yaml
services:
  agent:
    build:
      context: ../..
      dockerfile: infra/docker/base/Dockerfile.agent
      args:
        EXAMPLE_DIR: examples/NN-name
    ports:
      - "8000:8000"
    env_file:
      - ../../.env
    environment:
      - VERBOSE=${VERBOSE:-true}
```

Add additional services as needed (Supabase for Lesson 2, multiple agent containers for Lesson 3+).

## Agent Module Template

```python
from typing import TypedDict
from langgraph.graph import StateGraph, END
from agent_common.tracing import setup_tracing, verbose_log
from agent_common.llm import get_chat_model


class AgentState(TypedDict):
    messages: list
    # Add task-specific state fields


async def agent_node(state: AgentState) -> dict:
    llm = get_chat_model()
    verbose_log("AgentName", f"Processing {len(state['messages'])} messages")
    # Agent logic here
    return {"messages": state["messages"]}


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.set_entry_point("agent")
    graph.add_edge("agent", END)
    return graph.compile()
```

## FastAPI App Template

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from agent_common.tracing import setup_tracing


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_tracing()
    yield


app = FastAPI(title="Lesson N: [Title]", lifespan=lifespan)


class RunRequest(BaseModel):
    input: str


class RunResponse(BaseModel):
    output: str
    trace_id: str | None = None


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/run", response_model=RunResponse)
async def run(request: RunRequest):
    from .agents import build_graph
    graph = build_graph()
    result = await graph.ainvoke({"messages": [request.input]})
    return RunResponse(output=str(result))
```

## Checklist

After scaffolding, verify:
- [ ] `pyproject.toml` lists `agent-common` as workspace dependency
- [ ] `docker-compose.yml` passes `.env` file and `VERBOSE` var
- [ ] `src/app.py` has `/health` endpoint
- [ ] `src/app.py` calls `setup_tracing()` in lifespan
- [ ] Agent nodes use `verbose_log()` for debug output
- [ ] `tests/unit`, `tests/api`, and `tests/e2e` all exist
- [ ] `README.md` follows the documentation-writer template
