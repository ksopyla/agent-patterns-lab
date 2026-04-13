"""Shared runtime configuration and startup for Pattern 03 entry points."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from agent_common.persistence import close_checkpointer, create_postgres_pool, setup_checkpointer
from agent_common.tracing import build_langsmith_run_config, verbose_log
from langchain_core.runnables import RunnableConfig

from src.agents.graph import build_graph

PIPELINE_TIMEOUT_SECONDS = 120.0


@dataclass(slots=True)
class PipelineRuntime:
    graph: Any
    checkpointer: Any
    pool: Any


def build_pipeline_run_config(thread_id: str) -> RunnableConfig:
    """Build trace metadata and a stable thread config for public invocations."""
    config = build_langsmith_run_config(
        example_name="03-checkpoint-recovery",
        pattern_slug="checkpoint-recovery",
        run_name="pattern-03-checkpoint-recovery",
        extra_tags=["checkpointed"],
        metadata={"thread_id": thread_id},
    )
    config["configurable"] = {"thread_id": thread_id}
    return cast(RunnableConfig, config)


async def create_runtime() -> PipelineRuntime:
    """Create shared runtime resources for FastAPI and MCP entry points."""
    pool = await create_postgres_pool()
    checkpointer = await setup_checkpointer()
    graph = build_graph(checkpointer=checkpointer)

    verbose_log("System", "Pattern 03 runtime initialized")
    return PipelineRuntime(graph=graph, checkpointer=checkpointer, pool=pool)


async def close_runtime(runtime: PipelineRuntime) -> None:
    """Close shared runtime resources."""
    await close_checkpointer(runtime.checkpointer)
    await runtime.pool.close()
    verbose_log("System", "Pattern 03 runtime closed")
