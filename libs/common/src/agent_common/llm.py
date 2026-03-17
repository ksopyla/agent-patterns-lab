"""Provider-agnostic LLM configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import SecretStr

from agent_common.config import get_settings

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel


def get_chat_model(provider: str | None = None, **kwargs: object) -> BaseChatModel:
    """Get a chat model based on the configured or specified provider.

    Args:
        provider: Override the default provider ("azure_openai" or "anthropic").
        **kwargs: Additional keyword arguments passed to the model constructor.

    Returns:
        A configured chat model instance.
    """
    settings = get_settings()
    provider = provider or settings.llm_provider

    if provider == "azure_openai":
        from langchain_openai import AzureChatOpenAI

        return AzureChatOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=SecretStr(settings.azure_openai_api_key),
            azure_deployment=settings.azure_openai_deployment,
            api_version=settings.azure_openai_api_version,
            **kwargs,  # type: ignore[arg-type]
        )

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            api_key=SecretStr(settings.anthropic_api_key),
            model_name=settings.anthropic_model,
            **kwargs,  # type: ignore[arg-type]
        )

    msg = f"Unknown LLM provider: {provider}. Use 'azure_openai' or 'anthropic'."
    raise ValueError(msg)
