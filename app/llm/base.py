"""
Base interface for Large Language Model providers.
"""

from abc import ABC, abstractmethod


class BaseLLM(ABC):
    """
    Abstract interface implemented by all LLM providers.
    """

    @abstractmethod
    def generate(
        self,
        prompt: str,
        temperature: float = 0.0,
    ) -> str:
        """
        Generate a response from the language model.

        Args:
            prompt: Prompt sent to the model.
            temperature: Sampling temperature.

        Returns:
            Model response as plain text.
        """
        raise NotImplementedError