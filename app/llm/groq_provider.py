"""
Groq LLM provider.
"""

from groq import Groq

from app.config import GROQ_API_KEY, GROQ_MODEL
from app.llm.base import BaseLLM
from app.prompts.extraction_prompt import SYSTEM_PROMPT
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class GroqProvider(BaseLLM):
    """
    Groq implementation of the BaseLLM interface.
    """

    def __init__(self) -> None:
        """
        Initialize the Groq client.
        """

        if not GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY not found in environment variables."
            )

        self.client = Groq(
            api_key=GROQ_API_KEY,
        )

        self.model = GROQ_MODEL

        logger.info(
            f"Initialized Groq model: {self.model}"
        )

    def generate(
        self,
        prompt: str,
        temperature: float = 0.0,
    ) -> str:
        """
        Generate a response from Groq.

        Args:
            prompt:
                User prompt.

            temperature:
                Sampling temperature.

        Returns:
            Model response text.
        """

        try:

            response = self.client.chat.completions.create(

                model=self.model,

                temperature=temperature,

                response_format={
                    "type": "json_object"
                },

                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            )

            content = response.choices[0].message.content

            if content is None:
                raise RuntimeError(
                    "Groq returned an empty response."
                )

            return content.strip()

        except Exception as error:

            logger.exception(
                "Groq generation failed."
            )

            raise RuntimeError(
                "Unable to generate LLM response."
            ) from error