---
name: tester
description: >-
  Owns test strategy and test implementation for `examples/` and `libs/`.
  Use whenever code changes affect behavior, graph wiring, APIs, persistence,
  or regressions; update `unit`, `api`, and `e2e` tests and run canonical
  commands until green.
---

# Tester

## Responsibility

This skill owns test planning, test authoring, and test maintenance.

Use it to:
- decide which test layers must change
- implement or update `unit`, `api`, and `e2e` tests
- investigate regressions and confidence gaps

Do not use it to:
- choose architecture or protocol boundaries; use [`../agent-patterns-advisor/SKILL.md`](../agent-patterns-advisor/SKILL.md)
- implement production code under `examples/*/src`; use [`../langgraph-example-implementation/SKILL.md`](../langgraph-example-implementation/SKILL.md)
- own live Docker runs, smoke tests, or LangSmith trace checks; use [`../runtime-verifier/SKILL.md`](../runtime-verifier/SKILL.md)

## Trigger Conditions

- adding or changing code in `examples/*/src/` or `libs/*/src/`
- creating a new example or public API surface
- investigating regressions in graph flow, API behavior, or persistence
- questions about test coverage, fixtures, mocks, or pytest structure

## Non-Negotiable Rules

- Use pytest. Follow the LangGraph testing strategy: https://docs.langchain.com/oss/python/langgraph/test
- Build the graph definition separately and create a fresh compiled graph with a new
  `MemorySaver()` checkpointer inside each test. Do not share compiled graphs across tests.
- Use a stable `thread_id` whenever persistence, resume, interrupts, or `update_state()` are involved.
- Focus on one example at a time. Do not change unrelated examples or tests.
- Do not rely on live LLM providers. Prefer deterministic tests with mocks/stubs.
- Keep API and e2e tests CI-safe (no external services unless explicitly marked).
- In each example `tests/conftest.py`, add an autouse fixture that sets
  `LANGSMITH_TRACING=false`, `LANGCHAIN_TRACING_V2=false`, clears LangSmith API keys,
  and clears any cached settings objects.
- When mocking LangChain/MCP tool objects, configure `.ainvoke` explicitly:
  `mock_tool.ainvoke = AsyncMock(return_value='...')`.
  Do NOT use `AsyncMock(return_value='...')` alone -- agent code calls `tool.ainvoke(...)`,
  which creates an unconfigured child mock returning a MagicMock instead of the expected value.

## Test Architecture

```text
examples/NN-name/tests/
├── unit/       # isolate pure logic and individual agent nodes with mocks
├── api/        # validate FastAPI endpoints (/health, request validation, response model)
└── e2e/        # validate graph orchestration and cross-node state flow
```

## LangGraph Test Patterns

Use these patterns from the official LangGraph testing guide:

- **Full graph**: compile with `MemorySaver()`, call `invoke()` / `ainvoke()` with explicit
  initial state and `config={"configurable": {"thread_id": "..."}}`.
- **Single node**: access via `compiled_graph.nodes["node_name"].invoke(state)` for
  focused unit coverage that bypasses the checkpointer.
- **Partial execution**: seed prior state with `update_state(values=..., as_node="prev_node")`,
  then `invoke(None, ..., interrupt_after="target_node")` to test a middle section.
- If a subsection has a clear boundary, consider extracting it as a subgraph for direct testing.
- Assert on state updates, routing decisions, and tool-call inputs/outputs -- not on verbose model phrasing.

## Testing Workflow

1. **Discover scope** -- check changed files under `examples/` and `libs/`.
2. **Map to layers** -- behavior logic → `unit/`, endpoint schema → `api/`, graph wiring → `e2e/`.
3. **Write or update tests.**
4. **Run canonical commands** (see `project` rule) and iterate until all pass.
5. **Review** -- check for misconfigured `.ainvoke` mocks, wrong assertion types,
   stale imports, and tests that depend on execution order or shared state.

## Quality Checklist

- [ ] Each changed example has `unit`, `api`, and `e2e` tests when applicable
- [ ] No test performs real LLM API calls (use mocks/stubs)
- [ ] API tests validate both success and failure paths
- [ ] E2E tests verify orchestration order and state handoff
- [ ] All canonical commands pass (see `project` rule)
- [ ] Review step completed -- no type issues, mock misconfigurations, or stale imports
