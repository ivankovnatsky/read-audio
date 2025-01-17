from .protocol import AIProvider
from .openai import OpenAIProvider
from .anthropic import AnthropicProvider
from .ollama import OllamaProvider
from video_summarizer.constants import (
    DEFAULT_LLAMA_MODEL,
    DEFAULT_OPENAI_MODEL,
    DEFAULT_ANTRHOPIC_MODEL,
)


def get_provider(provider: str, model: str | None = None) -> AIProvider:
    """Factory function to get the appropriate AI provider"""
    providers = {
        "openai": lambda m: OpenAIProvider(model=m or DEFAULT_OPENAI_MODEL),
        "anthropic": lambda m: AnthropicProvider(model=m or DEFAULT_ANTRHOPIC_MODEL),
        "ollama": lambda m: OllamaProvider(model=m or DEFAULT_LLAMA_MODEL),
    }

    if provider not in providers:
        raise ValueError(
            f"Unknown provider: {provider}. Available providers: {list(providers.keys())}"
        )

    return providers[provider](model)


__all__ = [
    "AIProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "OllamaProvider",
    "get_provider",
]
