"""Shared execution flow for Pattern 03 REST and MCP entry points."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from agent_common.tracing import verbose_log
from langgraph.types import Command

from src.runtime import PIPELINE_TIMEOUT_SECONDS, PipelineRuntime, build_pipeline_run_config


@dataclass(slots=True)
class CompletedRun:
    thread_id: str
    result: dict[str, Any]
    status: str = "completed"


@dataclass(slots=True)
class InterruptedRun:
    thread_id: str
    payload: dict[str, Any]
    status: str = "interrupted"


@dataclass(slots=True)
class FailedRun:
    thread_id: str
    error_code: str
    detail: str
    http_status: int
    status: str = "failed"


PipelineOutcome = CompletedRun | InterruptedRun | FailedRun


def _new_thread_id() -> str:
    return str(uuid4())


def _extract_interrupt_payload(result: dict[str, Any]) -> dict[str, Any] | None:
    """Return the first interrupt payload if the graph paused."""
    raw_interrupts = result.get("__interrupt__")
    if not isinstance(raw_interrupts, list) or not raw_interrupts:
        return None

    first_interrupt = raw_interrupts[0]
    payload = getattr(first_interrupt, "value", None)
    if isinstance(payload, dict):
        return payload
    if payload is None:
        return None
    return {"message": str(payload)}


async def run_pipeline(
    runtime: PipelineRuntime,
    *,
    input_text: str,
    thread_id: str | None = None,
) -> PipelineOutcome:
    """Start or retry a checkpointed workflow.

    If *thread_id* points to a thread with pending checkpoint work (failed or
    interrupted), the graph resumes from the last checkpoint instead of
    starting fresh.
    """
    resolved_thread_id = thread_id or _new_thread_id()
    config = build_pipeline_run_config(resolved_thread_id)

    graph_input: dict[str, str] | None = {"input": input_text}
    if thread_id:
        try:
            state_snapshot = await runtime.graph.aget_state(config)
            if state_snapshot and state_snapshot.values and state_snapshot.next:
                graph_input = None
                verbose_log("System", f"Retrying thread_id={resolved_thread_id!r} from last checkpoint")
            else:
                verbose_log("System", f"Running thread_id={resolved_thread_id!r}")
        except Exception:
            verbose_log("System", f"Running thread_id={resolved_thread_id!r}")
    else:
        verbose_log("System", f"Running thread_id={resolved_thread_id!r}")

    try:
        result = await asyncio.wait_for(
            runtime.graph.ainvoke(graph_input, config=config),
            timeout=PIPELINE_TIMEOUT_SECONDS,
        )
    except TimeoutError:
        detail = f"Pipeline timed out after {PIPELINE_TIMEOUT_SECONDS:.0f}s"
        return FailedRun(
            thread_id=resolved_thread_id,
            error_code="pipeline_timeout",
            detail=detail,
            http_status=504,
        )
    except Exception as exc:
        detail = str(exc)
        return FailedRun(
            thread_id=resolved_thread_id,
            error_code="pipeline_failed",
            detail=detail,
            http_status=502,
        )

    interrupt_payload = _extract_interrupt_payload(result)
    if interrupt_payload is not None:
        return InterruptedRun(thread_id=resolved_thread_id, payload=interrupt_payload)

    return CompletedRun(thread_id=resolved_thread_id, result=result)


async def resume_pipeline(
    runtime: PipelineRuntime,
    *,
    thread_id: str,
    resume_payload: dict[str, Any],
) -> PipelineOutcome:
    """Resume an interrupted workflow using ``Command(resume=...)``."""
    config = build_pipeline_run_config(thread_id)

    try:
        state_snapshot = await runtime.graph.aget_state(config)
    except Exception:
        state_snapshot = None

    if not state_snapshot or not state_snapshot.values:
        return FailedRun(
            thread_id=thread_id,
            error_code="thread_not_found",
            detail=f"Thread {thread_id!r} was not found",
            http_status=404,
        )

    verbose_log("System", f"Resuming thread_id={thread_id!r}")

    try:
        result = await asyncio.wait_for(
            runtime.graph.ainvoke(Command(resume=resume_payload), config=config),
            timeout=PIPELINE_TIMEOUT_SECONDS,
        )
    except TimeoutError:
        detail = f"Pipeline timed out after {PIPELINE_TIMEOUT_SECONDS:.0f}s"
        return FailedRun(
            thread_id=thread_id,
            error_code="pipeline_timeout",
            detail=detail,
            http_status=504,
        )
    except Exception as exc:
        detail = str(exc)
        return FailedRun(
            thread_id=thread_id,
            error_code="pipeline_failed",
            detail=detail,
            http_status=502,
        )

    interrupt_payload = _extract_interrupt_payload(result)
    if interrupt_payload is not None:
        return InterruptedRun(thread_id=thread_id, payload=interrupt_payload)

    return CompletedRun(thread_id=thread_id, result=result)
