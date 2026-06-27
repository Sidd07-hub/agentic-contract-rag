"""
GitHub Models LLM provider (100% Free Tier, No Paid Fallbacks).

Includes automatic rate-limit handling for GitHub's free tier
(10 requests per 60 seconds).
"""

from __future__ import annotations
import os
import re
import time
from openai import OpenAI, RateLimitError
from app.llm.base import BaseLLM
from app.prompts.extraction_prompt import SYSTEM_PROMPT
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# GitHub free tier: 10 requests per 60 seconds
MAX_RETRIES = 3


class OpenAIProvider(BaseLLM):
    """
    Locked strictly to GitHub's free Azure inference endpoints.
    Automatically handles rate limits with retry + backoff.
    """

    def __init__(self) -> None:
        """
        Initialize the free GitHub client.
        """
        from dotenv import load_dotenv
        load_dotenv()

        # ONLY look for the free GitHub token
        self.api_key = os.environ.get("GITHUB_TOKEN")

        if not self.api_key or not self.api_key.startswith("github_pat_"):
            raise ValueError(
                "CRITICAL ERROR: No valid GITHUB_TOKEN found in .env file. "
                "This pipeline is locked to the free tier and will not accept paid keys."
            )

        # Hardcode the free server URL directly into the client
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://models.inference.ai.azure.com",
        )

        self.model = "gpt-4o-mini"
        logger.info(f"Initialized 100% FREE model: {self.model} via GitHub.")

    def _call_api(self, messages: list[dict], temperature: float) -> str:
        """
        Internal method that calls the API with automatic rate-limit retry.
        """
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    temperature=temperature,
                    response_format={
                        "type": "json_object"
                    },
                    messages=messages,
                )

                content = response.choices[0].message.content

                if content is None:
                    raise RuntimeError("GitHub server returned an empty response.")

                return content.strip()

            except RateLimitError as error:
                # Parse wait time from error message (e.g., "Please wait 51 seconds")
                wait_seconds = self._parse_wait_time(str(error))
                if attempt < MAX_RETRIES:
                    logger.warning(
                        f"Rate limited (attempt {attempt}/{MAX_RETRIES}). "
                        f"Waiting {wait_seconds}s before retry..."
                    )
                    time.sleep(wait_seconds)
                else:
                    logger.exception("Rate limit exceeded after all retries.")
                    raise RuntimeError("Rate limit exceeded after all retries.") from error

            except Exception as error:
                logger.exception("Generation failed on GitHub free tier.")
                raise RuntimeError("Unable to generate LLM response.") from error

        raise RuntimeError("Unexpected: exhausted retries without result.")

    @staticmethod
    def _parse_wait_time(error_message: str) -> int:
        """
        Extract the recommended wait time from a rate limit error message.
        Handles both seconds and milliseconds, and guards against extremely large numbers.
        """
        # Try matching milliseconds first
        match_ms = re.search(r"wait (\d+)\s*(ms|millisecond)", error_message, re.IGNORECASE)
        if match_ms:
            ms = int(match_ms.group(1))
            return max(1, ms // 1000) + 2

        # Try matching seconds
        match_sec = re.search(r"wait (\d+)\s*(s|second)", error_message, re.IGNORECASE)
        if match_sec:
            sec = int(match_sec.group(1))
            # If the API returned milliseconds but labeled them as seconds (GitHub bug)
            # or if the number is unreasonably high:
            if sec > 3600: # More than 1 hour is likely milliseconds or a bug
                return max(1, sec // 1000) + 2
            return sec + 2

        # Generic number matching after "wait"
        match_generic = re.search(r"wait (\d+)", error_message, re.IGNORECASE)
        if match_generic:
            val = int(match_generic.group(1))
            if val > 1000:  # likely milliseconds
                return max(1, val // 1000) + 2
            return val + 2

        return 62  # Safe fallback: slightly over 60s

    def generate(
        self,
        prompt: str,
        temperature: float = 0.0,
    ) -> str:
        """
        Generate a response from GitHub's free endpoint.
        """
        return self._call_api(
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
            temperature=temperature,
        )

    def generate_with_system(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.0,
    ) -> str:
        """
        Generate a response using a custom system prompt.
        Used by the validator agent for contradiction detection.
        """
        return self._call_api(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=temperature,
        )