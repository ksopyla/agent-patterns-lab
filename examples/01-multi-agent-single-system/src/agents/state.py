"""Typed state shared across all agent nodes."""

from __future__ import annotations

from typing import Required, TypedDict


class AgentState(TypedDict, total=False):
    input: Required[str]
    plan: str
    research: str
    output: str
