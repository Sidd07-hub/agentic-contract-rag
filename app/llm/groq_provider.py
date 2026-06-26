"""
Groq LLM provider.
"""

from groq import Groq

from app.config import settings
from app.llm.base import BaseLLM
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class GroqProvider(BaseLLM):
    """
    Groq implementation of the BaseLLM interface.
    """

    def __init__(self) -> None:

        self.client = Groq(
            api_key=settings.GROQ_API_KEY
        )

        self.model = settings.GROQ_MODEL

        logger.info(
            f"Loaded Groq model: {self.model}"
        )

    def generate(
        self,
        prompt: str,
        temperature: float = 0.0,
    ) -> str:

        try:

            response = self.client.chat.completions.create(

                model=self.model,

                temperature=temperature,

                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert legal AI assistant. "
                            "Return only accurate information extracted "
                            "from the supplied contract."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            )

            return response.choices[0].message.content.strip()

        except Exception as error:

            logger.exception("Groq request failed.")

            raise RuntimeError(
                "Failed to generate response from Groq."
            ) from error