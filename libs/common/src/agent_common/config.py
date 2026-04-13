"""Application settings loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM provider selection
    llm_provider: Literal["azure_openai", "anthropic"] = "azure_openai"

    # Azure OpenAI
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = ""
    azure_openai_api_version: str = "2025-01-01-preview"

    # Anthropic
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"

    # LangSmith
    langsmith_api_key: str = ""
    langsmith_project: str = "agent-patterns-lab"
    langsmith_tracing: bool = True

    # PostgreSQL persistence (Pattern 03+)
    postgres_uri: str = ""

    # Auth0 (Pattern 07+)
    auth0_domain: str = ""
    auth0_client_id: str = ""
    auth0_client_secret: str = ""
    auth0_audience: str = ""

    # Debug
    verbose: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
