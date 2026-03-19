---
name: tester
description: >-
  Owns test strategy, test implementation, and verification for `examples/`
  and `libs/`. Use whenever code changes affect behavior, graph wiring, APIs,
  persistence, or regressions; update `unit`, `api`, and `e2e` tests and run
  the repository test, lint, and type-check workflow before finishing.
---

# Tester

## Responsibility

This skill owns test planning, test authoring, test maintenance, and verification.

Use it to:
- decide which test layers must change
- implement or update `unit`, `api`, and `e2e` tests
- run the required test, lint, and type-check commands
- investigate regressions and confidence gaps

Do not use it to:
- choose architecture or protocol boundaries; use [`../agent-patterns-advisor/SKILL.md`](../agent-patterns-advisor/SKILL.md)
- implement most production code under `examples/*/src`; use [`../langgraph-example-implementation/SKILL.md`](../langgraph-example-implementation/SKILL.md)
- scaffold example directories or Docker/README files; use [`../example-scaffolder/SKILL.md`](../example-scaffolder/SKILL.md)

## Trigger Conditions

Trigger this skill when:
- adding or changing code in `examples/*/src/` or `libs/*/src/`
- creating a new example folder or a new public API surface
- improving confidence before commit or pull request
- investigating regressions in graph flow, API behavior, or persistence
- reviewing whether coverage still matches the changed behavior

## Non-Negotiable Rules

- Use pytest for testing.
- Follow the LangGraph testing strategy: https://docs.langchain.com/oss/python/langgraph/test
- For LangGraph agents, build the graph definition separately and create a fresh
  compiled graph inside each test with a new in-memory checkpointer.
- Use a stable `thread_id` in graph tests whenever persistence, resume behavior,
  interrupts, or `update_state()` are involved.
- Focus on one example at a time and do not change unrelated examples or tests.
- Do not rely on live LLM providers in tests.
- Prefer deterministic tests with mocks/stubs.
- Keep API and e2e tests in CI-safe form (no external services required unless explicitly marked and isolated).
- When mocking LangChain/MCP tool objects, configure `.ainvoke` explicitly:
  `mock_tool.ainvoke = AsyncMock(return_value='...')`.
  Do NOT use `AsyncMock(return_value='...')` alone -- that configures the mock
  as a callable, but agent code calls `tool.ainvoke(...)`, which creates an
  unconfigured child mock returning a MagicMock instead of the expected value.

## Test Architecture Standard

For every example, keep tests in:

```text
examples/NN-name/tests/
├── unit/
│   └── test_*.py
├── api/
│   └── test_*.py
└── e2e/
    └── test_*.py
```

Coverage intent:
- **unit**: isolate pure logic and individual agent nodes with mocks/stubs
- **api**: validate FastAPI endpoints (`/health`, request validation, response model)
- **e2e**: validate graph orchestration and cross-node state flow

## LangGraph Agent Test Strategy

When testing LangGraph-based agents, prefer these patterns from the official
LangGraph testing guide:

- Create the graph in a helper such as `create_graph()` and compile it inside
  each test with a fresh `MemorySaver()` checkpointer. Do not share a compiled
  graph across tests because stateful checkpoints can leak between test cases.
- Test the full graph with `invoke()` or `ainvoke()` using explicit initial
  state and `config={"configurable": {"thread_id": "test-id"}}`.
- Test individual nodes directly through `compiled_graph.nodes["node_name"]`
  when you want focused unit coverage for one agent step. This bypasses
  checkpointer behavior, which is useful for isolated node assertions.
- Test middle sections of a graph with partial execution instead of forcing
  every test through the full workflow:
  - seed prior state with `compiled_graph.update_state(...)`
  - set `as_node="previous_node"` so execution resumes at the next node
  - call `invoke(None, ..., interrupt_after="target_node")` to stop at the end
    of the section under test
- If a subsection of the workflow has a clear boundary, consider extracting it
  as a subgraph so it can be tested directly.
- Prefer asserting on state updates, routing decisions, and tool-call inputs or
  outputs, not on verbose model phrasing.

Reference patterns:

```python
from langgraph.checkpoint.memory import MemorySaver

def test_graph_execution() -> None:
    graph = create_graph()
    compiled_graph = graph.compile(checkpointer=MemorySaver())

    result = compiled_graph.invoke(
        {"messages": [], "query": "btc"},
        config={"configurable": {"thread_id": "test-thread"}},
    )

    assert result["report"]
```

```python
def test_single_node() -> None:
    graph = create_graph()
    compiled_graph = graph.compile(checkpointer=MemorySaver())

    result = compiled_graph.nodes["research_planner"].invoke(
        {"messages": [], "query": "btc"}
    )

    assert result["plan"]
```

```python
def test_partial_execution() -> None:
    graph = create_graph()
    compiled_graph = graph.compile(checkpointer=MemorySaver())

    compiled_graph.update_state(
        config={"configurable": {"thread_id": "test-thread"}},
        values={"messages": [], "query": "btc", "plan": ["news"]},
        as_node="research_planner",
    )

    result = compiled_graph.invoke(
        None,
        config={"configurable": {"thread_id": "test-thread"}},
        interrupt_after="news_scanner",
    )

    assert result["news_findings"]
```

Apply those patterns to the repository test layers:
- `tests/unit/`: node-level tests and routing logic
- `tests/api/`: endpoint-to-graph integration with mocked dependencies
- `tests/e2e/`: compiled graph execution, persistence, interrupts, and state
  handoff across multiple nodes

## Testing Workflow

1. **Discover impacted scope**
   - Check changed files under `examples/` and `libs/`.
2. **Update tests by layer**
   - Behavior logic changed -> update `tests/unit/`
   - Endpoint schema/flow changed -> update `tests/api/`
   - Graph wiring/agent sequence changed -> update `tests/e2e/`
3. **Run the repository test suite**
   - `uv run python scripts/testing/run_test_suite.py`
4. **Fix failures and re-run**
   - Repeat until green.
5. **Run full CI checks locally**
   - After all tests pass, run the same checks that CI enforces.
     Most mypy and lint errors surface here, not during pytest.
   - `uv run ruff check .`
   - `uv run ruff format --check .`
   - `uv run python scripts/linting/run_mypy.py`
   - Fix every error before proceeding -- CI will reject the same issues.
6. **Review the changed tests**
   - Re-read the new/changed test files and look for:
     - Missing or incorrect type annotations (mypy will flag these)
     - Imports of modules that don't exist or have moved
     - Mock objects with misconfigured `.ainvoke` (see Non-Negotiable Rules)
     - Assertions that compare wrong types (e.g. `str` vs `dict`)
     - Leftover `# type: ignore` comments that hide real errors
     - Tests that accidentally depend on execution order or shared state
   - Fix every issue found, then re-run steps 3-5 until clean.

## Commands

- Full test suite with coverage:
  - `uv run python scripts/testing/run_test_suite.py`
- Faster local run without coverage:
  - `uv run python scripts/testing/run_test_suite.py --no-coverage`
- Direct pytest fallback:
  - `uv run pytest`
- Lint:
  - `uv run ruff check .`
- Format check:
  - `uv run ruff format --check .`
- Type check (per-directory, avoids duplicate module errors):
  - `uv run python scripts/linting/run_mypy.py`


## Quality Checklist

Before marking testing work complete:
- [ ] Each changed example has `unit`, `api`, and `e2e` tests when applicable
- [ ] No test performs real LLM API calls (use mocks/stubs)
- [ ] API tests validate both success and failure paths
- [ ] E2E tests verify orchestration order and state handoff
- [ ] `uv run python scripts/testing/run_test_suite.py` passes locally
- [ ] `uv run ruff check .` reports no errors
- [ ] `uv run ruff format --check .` reports no reformatting needed
- [ ] `uv run python scripts/linting/run_mypy.py` passes with zero errors
- [ ] Review the changed tests step completed -- no type issues, mock misconfigurations, or stale imports remain
