"""FastAPI application exposing the crypto intelligence pipeline."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from agent_common.tracing import setup_tracing, verbose_log
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.agents.graph import build_graph


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncIterator[None]:
    setup_tracing()
    fastapi_app.state.graph = build_graph()
    verbose_log("System", "FastAPI application started")
    yield
    verbose_log("System", "FastAPI application shutting down")


app = FastAPI(
    title="Pattern 01: Orchestrator Pipeline",
    description="Three-agent crypto intelligence pipeline (Research Planner, News Scanner, Intelligence Compiler).",
    version="0.1.0",
    lifespan=lifespan,
)


class RunRequest(BaseModel):
    input: str = Field(min_length=3, max_length=500, description="Crypto project query to research")


class RunResponse(BaseModel):
    report: str
    plan: str
    news: str


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/run", response_model=RunResponse)
async def run(request: RunRequest) -> RunResponse | JSONResponse:
    verbose_log("System", f"Received request: {request.input[:100]}")

    try:
        result = await app.state.graph.ainvoke({"input": request.input})
    except Exception as exc:
        verbose_log("System", f"Pipeline failed: {exc}")
        return JSONResponse(
            status_code=502,
            content={"error": "pipeline_failed", "detail": str(exc)},
        )

    verbose_log("System", "Pipeline complete, returning response")

    return RunResponse(
        report=result.get("report", ""),
        plan=result.get("plan", ""),
        news=result.get("news", ""),
    )
