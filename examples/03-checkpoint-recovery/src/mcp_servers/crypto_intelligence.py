"""MCP server exposing the checkpointed crypto intelligence pipeline as tools.

The tool surface is the agentic interface to Pattern 03.  An AI client
(Claude Code, Cursor, ...) discovers these tools via MCP and can:

- run or resume a crypto research pipeline,
- inspect checkpoint status of any thread, and
- list / delete threads.

Thread status is derived from LangGraph checkpoint state -- there is no
separate status table.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from agent_common.tracing import setup_tracing, verbose_log
from mcp.server.fastmcp import FastMCP

from src.runtime import PipelineRuntime, close_runtime, create_runtime
from src.service import CompletedRun, InterruptedRun, resume_pipeline, run_pipeline

mcp = FastMCP(
    "crypto-intelligence",
    host="0.0.0.0",
    port=8000,
)
_runtime: PipelineRuntime | None = None


# ---------------------------------------------------------------------------
# Helpers for deriving thread status from LangGraph checkpoint state
# ---------------------------------------------------------------------------


def _extract_interrupt_info(state: Any) -> dict[str, Any] | None:
    """Pull the first interrupt payload out of a state snapshot's tasks."""
    tasks = getattr(state, "tasks", None)
    if not tasks:
        return None
    for task in tasks:
        for intr in getattr(task, "interrupts", []):
            value = getattr(intr, "value", None)
            if isinstance(value, dict):
                return value
    return None


def _format_completed_status(thread_id: str, values: dict[str, Any]) -> str:
    project_name = values.get("project_name", "")
    coin_ticker = values.get("coin_ticker", "")
    coin_id = values.get("coin_id", "")
    report = str(values.get("report", ""))

    identity = project_name
    if coin_ticker:
        identity += f" ({coin_ticker})"
    if coin_id:
        identity += f" [coin_id={coin_id}]"

    lines = [
        f'Research thread "{thread_id}" — COMPLETED',
        f"Project: {identity}" if identity else "",
    ]
    if report:
        preview = report[:300]
        if len(report) > 300:
            preview += "…"
        lines.append(f"\nReport preview:\n{preview}")
    return "\n".join(line for line in lines if line)


def _format_interrupted_status(thread_id: str, values: dict[str, Any], interrupt: dict[str, Any]) -> str:
    project_name = values.get("project_name", "")
    message = interrupt.get("message", "Workflow interrupted")
    matches = interrupt.get("matches", [])

    lines = [
        f'Research thread "{thread_id}" — INTERRUPTED',
        f"Project: {project_name}" if project_name else "",
        f"Waiting for human input: {message}",
    ]
    if isinstance(matches, list) and matches:
        lines.append(
            "\nChoose one of these CoinGecko IDs and call "
            "research_crypto_project with the same thread_id and "
            "selected_coin_id:"
        )
        for match in matches:
            if isinstance(match, dict):
                rank = match.get("market_cap_rank")
                lines.append(f"  - {match.get('coin_id')}: {match.get('name')} ({match.get('symbol')}) rank={rank}")
    return "\n".join(line for line in lines if line)


def _format_resumable_status(thread_id: str, values: dict[str, Any], next_nodes: tuple[str, ...]) -> str:
    project_name = values.get("project_name", "")
    lines = [
        f'Research thread "{thread_id}" — RESUMABLE',
        f"Project: {project_name}" if project_name else "",
        f"Pipeline stopped before: {', '.join(next_nodes)}",
        (f'\nResume by calling research_crypto_project with thread_id="{thread_id}".'),
    ]
    return "\n".join(line for line in lines if line)


def _format_thread_summary(thread_id: str, state: Any) -> str:
    """One-line summary of a thread for the listing tool."""
    values = state.values if state and state.values else {}
    input_text = str(values.get("input", ""))[:80]

    interrupt = _extract_interrupt_info(state)
    if interrupt:
        return f"  {thread_id}  INTERRUPTED  {input_text!r}"
    if not state.next:
        return f"  {thread_id}  COMPLETED    {input_text!r}"
    return f"  {thread_id}  RESUMABLE    {input_text!r}"


async def _list_thread_ids(pool: Any, *, limit: int = 50) -> list[str]:
    """Query distinct thread IDs from the LangGraph checkpoint table."""
    try:
        async with pool.connection() as conn, conn.cursor() as cur:
            await cur.execute(
                "SELECT DISTINCT thread_id FROM checkpoints WHERE checkpoint_ns = '' ORDER BY thread_id LIMIT %s",
                (limit,),
            )
            rows = await cur.fetchall()
            return [str(row["thread_id"]) for row in rows]
    except Exception as exc:
        verbose_log("MCP", f"Unable to list threads: {exc}")
        return []


# ---------------------------------------------------------------------------
# MCP lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def mcp_lifespan(_: object) -> AsyncIterator[None]:
    global _runtime
    setup_tracing()
    _runtime = await create_runtime()
    verbose_log("MCP", "MCP server started")
    yield
    if _runtime is not None:
        await close_runtime(_runtime)
        _runtime = None
    verbose_log("MCP", "MCP server shutting down")


app = mcp.sse_app()
app.router.lifespan_context = mcp_lifespan


# ---------------------------------------------------------------------------
# MCP tools
# ---------------------------------------------------------------------------


def _format_interrupt_message(outcome: InterruptedRun) -> str:
    payload = outcome.payload
    lines = [
        f"[Workflow interrupted] thread_id={outcome.thread_id}",
        str(payload.get("message", "Workflow interrupted")),
    ]
    matches = payload.get("matches", [])
    if isinstance(matches, list) and matches:
        lines.append(
            "Choose one of these CoinGecko IDs and call the tool again with the same thread_id and selected_coin_id:"
        )
        for match in matches:
            if isinstance(match, dict):
                rank = match.get("market_cap_rank")
                lines.append(f"- {match.get('coin_id')}: {match.get('name')} ({match.get('symbol')}) rank={rank}")
    return "\n".join(lines)


@mcp.tool()
async def research_crypto_project(
    query: str,
    thread_id: str | None = None,
    selected_coin_id: str | None = None,
) -> str:
    """Research a cryptocurrency project with checkpoint recovery.

    Args:
        query: Natural-language research request about a crypto project.
        thread_id: Optional stable thread ID. Reuse this to retry failed runs or
            resume an interrupted workflow.
        selected_coin_id: Optional CoinGecko coin ID used to resume an interrupted
            workflow after the planner asked the user to disambiguate a project.

    Returns:
        The final intelligence report on success, or a human-readable interrupt /
        error message that includes the resumable thread ID.
    """
    if _runtime is None:
        raise RuntimeError("MCP runtime is not initialized")

    preview = repr(query[:80])
    verbose_log("MCP", f"research_crypto_project({preview})")

    if selected_coin_id and thread_id:
        outcome = await resume_pipeline(
            _runtime,
            thread_id=thread_id,
            resume_payload={"selected_coin_id": selected_coin_id},
        )
    else:
        outcome = await run_pipeline(
            _runtime,
            input_text=query,
            thread_id=thread_id,
        )

    if isinstance(outcome, CompletedRun):
        report = str(outcome.result.get("report", ""))
        verbose_log("MCP", f"research_crypto_project -- complete ({len(report)} chars)")
        return report

    if isinstance(outcome, InterruptedRun):
        message = _format_interrupt_message(outcome)
        verbose_log("MCP", message)
        return message

    verbose_log("MCP", f"research_crypto_project failed: {outcome.detail}")
    return f"[{outcome.error_code}] thread_id={outcome.thread_id} {outcome.detail}"


@mcp.tool()
async def get_research_status(thread_id: str) -> str:
    """Check the current status of a crypto research thread.

    Use this to see whether a research run completed, was interrupted
    (waiting for your input), or can be resumed after a failure.

    Args:
        thread_id: The thread ID returned by research_crypto_project.
    """
    if _runtime is None:
        raise RuntimeError("MCP runtime is not initialized")

    config = {"configurable": {"thread_id": thread_id}}
    try:
        state = await _runtime.graph.aget_state(config)
    except Exception as exc:
        return f"Unable to load state for thread {thread_id!r}: {exc}"

    if not state or not state.values:
        return f"No research found for thread {thread_id!r}."

    values: dict[str, Any] = dict(state.values) if isinstance(state.values, dict) else {}

    interrupt = _extract_interrupt_info(state)
    if interrupt:
        return _format_interrupted_status(thread_id, values, interrupt)

    if not state.next:
        return _format_completed_status(thread_id, values)

    return _format_resumable_status(thread_id, values, state.next)


@mcp.tool()
async def list_research_threads() -> str:
    """List all known crypto research threads and their status.

    Returns a summary of each thread including its current state
    (completed, interrupted, or resumable).
    """
    if _runtime is None:
        raise RuntimeError("MCP runtime is not initialized")

    thread_ids = await _list_thread_ids(_runtime.pool)
    if not thread_ids:
        return "No research threads found."

    summaries: list[str] = []
    for tid in thread_ids:
        config = {"configurable": {"thread_id": tid}}
        try:
            state = await _runtime.graph.aget_state(config)
            if state and state.values:
                summaries.append(_format_thread_summary(tid, state))
            else:
                summaries.append(f"  {tid}  UNKNOWN")
        except Exception:
            summaries.append(f"  {tid}  ERROR (unable to load state)")

    header = f"Found {len(summaries)} research thread(s):\n"
    return header + "\n".join(summaries)


@mcp.tool()
async def delete_research_thread(thread_id: str) -> str:
    """Delete a research thread and all its checkpoint data.

    Args:
        thread_id: The thread ID to delete.
    """
    if _runtime is None:
        raise RuntimeError("MCP runtime is not initialized")

    config = {"configurable": {"thread_id": thread_id}}
    try:
        state = await _runtime.graph.aget_state(config)
    except Exception:
        state = None

    if not state or not state.values:
        return f"No research found for thread {thread_id!r}."

    try:
        await _runtime.checkpointer.adelete_thread(thread_id)
    except Exception as exc:
        return f"Failed to delete thread {thread_id!r}: {exc}"

    verbose_log("MCP", f"Deleted thread {thread_id!r}")
    return f"Thread {thread_id!r} and its checkpoints have been deleted."


if __name__ == "__main__":
    mcp.run(transport="sse")
