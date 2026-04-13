"""PostgreSQL helpers for LangGraph persistence patterns."""

from __future__ import annotations

from typing import Any

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from agent_common.config import get_settings
from agent_common.tracing import verbose_log

_CHECKPOINTER_CONTEXTS: dict[int, Any] = {}


async def create_postgres_pool(postgres_uri: str | None = None) -> AsyncConnectionPool[Any]:
    """Create and open a PostgreSQL connection pool with dict rows."""
    resolved_uri = postgres_uri or get_settings().postgres_uri
    if not resolved_uri:
        raise ValueError("POSTGRES_URI is required for PostgreSQL-backed persistence")

    pool: AsyncConnectionPool[Any] = AsyncConnectionPool(
        conninfo=resolved_uri,
        kwargs={"autocommit": True, "row_factory": dict_row},
        open=False,
    )
    await pool.open()
    verbose_log("System", "PostgreSQL connection pool opened")
    return pool


async def setup_checkpointer(postgres_uri: str | None = None) -> AsyncPostgresSaver:
    """Create and initialize the LangGraph PostgreSQL checkpointer."""
    resolved_uri = postgres_uri or get_settings().postgres_uri
    if not resolved_uri:
        raise ValueError("POSTGRES_URI is required for PostgreSQL-backed persistence")

    context_manager = AsyncPostgresSaver.from_conn_string(resolved_uri)
    checkpointer = await context_manager.__aenter__()
    _CHECKPOINTER_CONTEXTS[id(checkpointer)] = context_manager
    await checkpointer.setup()
    verbose_log("System", "LangGraph PostgreSQL checkpointer initialized")
    return checkpointer


async def close_checkpointer(checkpointer: AsyncPostgresSaver | None) -> None:
    """Close a checkpointer created by `setup_checkpointer`."""
    if checkpointer is None:
        return

    context_manager = _CHECKPOINTER_CONTEXTS.pop(id(checkpointer), None)
    if context_manager is not None:
        await context_manager.__aexit__(None, None, None)
        verbose_log("System", "LangGraph PostgreSQL checkpointer closed")
