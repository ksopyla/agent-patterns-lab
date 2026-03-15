"""FastAPI application exposing the multi-agent pipeline."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from agent_common.tracing import setup_tracing, verbose_log
from fastapi import FastAPI
from pydantic import BaseModel

from src.agents.graph import build_graph


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    setup_tracing()
    verbose_log("System", "FastAPI application started")
    yield
    verbose_log("System", "FastAPI application shutting down")


app = FastAPI(
    title="Lesson 1: Multi-Agent Single System",
    description="Three LangGraph agents (planner, researcher, writer) collaborating in a single pipeline.",
    version="0.1.0",
    lifespan=lifespan,
)


class RunRequest(BaseModel):
    input: str


class RunResponse(BaseModel):
    output: str
    plan: str
    research: str


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/run", response_model=RunResponse)
async def run(request: RunRequest) -> RunResponse:
    verbose_log("System", f"Received request: {request.input[:100]}")

    graph = build_graph()
    result = await graph.ainvoke({"input": request.input})

    verbose_log("System", "Pipeline complete, returning response")

    return RunResponse(
        output=result.get("output", ""),
        plan=result.get("plan", ""),
        research=result.get("research", ""),
    )
