"""
LLM providers package.
"""

from app.config import LLM_PROVIDER
from app.llm.base import BaseLLM
from app.llm.openai_provider import OpenAIProvider


def get_llm_provider() -> BaseLLM:
    """
    Factory function to retrieve the configured LLM provider.
    """
    provider = LLM_PROVIDER.lower()

    if provider == "openai":
        return OpenAIProvider()
    else:
        raise ValueError(
            f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}. "
            "Supported providers are: 'openai'."
        )
