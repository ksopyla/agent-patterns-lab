"""FastAPI application exposing the checkpointed crypto intelligence pipeline."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Literal

from agent_common.tracing import setup_tracing, verbose_log
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.runtime import PipelineRuntime, close_runtime, create_runtime
from src.service import CompletedRun, FailedRun, InterruptedRun, resume_pipeline, run_pipeline


class RunRequest(BaseModel):
    input: str = Field(min_length=3, max_length=500, description="Crypto project query to research")
    thread_id: str | None = Field(default=None, description="Optional thread ID for retries after failure")


class ResumeRequest(BaseModel):
    thread_id: str = Field(min_length=1, description="Interrupted thread ID to resume")
    selected_coin_id: str = Field(min_length=1, description="CoinGecko coin ID selected by the user")


class CoinMatchResponse(BaseModel):
    coin_id: str
    name: str
    symbol: str
    market_cap_rank: int | None = None


class RunCompletedResponse(BaseModel):
    status: Literal["completed"] = "completed"
    thread_id: str
    report: str
    plan: str
    news: str
    profile: str
    community: str
    project_name: str = ""
    coin_ticker: str = ""
    coin_id: str = ""


class RunInterruptedResponse(BaseModel):
    status: Literal["interrupted"] = "interrupted"
    thread_id: str
    interrupt_type: str
    message: str
    project_name: str = ""
    coin_ticker: str = ""
    matches: list[CoinMatchResponse]


class ErrorResponse(BaseModel):
    error: str
    detail: str
    thread_id: str


def _completed_response(outcome: CompletedRun) -> RunCompletedResponse:
    result = outcome.result
    return RunCompletedResponse(
        thread_id=outcome.thread_id,
        report=str(result.get("report", "")),
        plan=str(result.get("plan", "")),
        news=str(result.get("news", "")),
        profile=str(result.get("profile", "")),
        community=str(result.get("community", "")),
        project_name=str(result.get("project_name", "")),
        coin_ticker=str(result.get("coin_ticker", "")),
        coin_id=str(result.get("coin_id", "")),
    )


def _interrupted_response(outcome: InterruptedRun) -> RunInterruptedResponse:
    payload = outcome.payload
    matches = payload.get("matches", [])
    match_models = [CoinMatchResponse.model_validate(match) for match in matches if isinstance(match, dict)]
    return RunInterruptedResponse(
        thread_id=outcome.thread_id,
        interrupt_type=str(payload.get("interrupt_type", "interrupt")),
        message=str(payload.get("message", "Workflow interrupted")),
        project_name=str(payload.get("project_name", "")),
        coin_ticker=str(payload.get("coin_ticker", "")),
        matches=match_models,
    )


def _error_response(outcome: FailedRun) -> JSONResponse:
    return JSONResponse(
        status_code=outcome.http_status,
        content=ErrorResponse(
            error=outcome.error_code,
            detail=outcome.detail,
            thread_id=outcome.thread_id,
        ).model_dump(),
    )


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncIterator[None]:
    setup_tracing()
    runtime = await create_runtime()
    fastapi_app.state.runtime = runtime
    verbose_log("System", "FastAPI application started")
    yield
    await close_runtime(runtime)
    verbose_log("System", "FastAPI application shutting down")


app = FastAPI(
    title="Pattern 03: Checkpoint Recovery and Resilience",
    description=(
        "Checkpoint-capable crypto intelligence pipeline. REST entry points support "
        "retry-after-failure and resume-after-interrupt using stable thread IDs. "
        "Thread inspection is exposed via MCP tools, not REST endpoints."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


def _runtime() -> PipelineRuntime:
    return app.state.runtime  # type: ignore[no-any-return]


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/run", response_model=RunCompletedResponse | RunInterruptedResponse)
async def run(request: RunRequest) -> RunCompletedResponse | RunInterruptedResponse | JSONResponse:
    verbose_log("System", f"Received request: {request.input[:100]}")

    outcome = await run_pipeline(
        _runtime(),
        input_text=request.input,
        thread_id=request.thread_id,
    )

    if isinstance(outcome, CompletedRun):
        return _completed_response(outcome)
    if isinstance(outcome, InterruptedRun):
        return _interrupted_response(outcome)
    return _error_response(outcome)


@app.post("/run/resume", response_model=RunCompletedResponse | RunInterruptedResponse)
async def resume(request: ResumeRequest) -> RunCompletedResponse | RunInterruptedResponse | JSONResponse:
    verbose_log("System", f"Resuming thread {request.thread_id!r} with selected_coin_id={request.selected_coin_id!r}")

    outcome = await resume_pipeline(
        _runtime(),
        thread_id=request.thread_id,
        resume_payload={"selected_coin_id": request.selected_coin_id},
    )

    if isinstance(outcome, CompletedRun):
        return _completed_response(outcome)
    if isinstance(outcome, InterruptedRun):
        return _interrupted_response(outcome)
    return _error_response(outcome)
