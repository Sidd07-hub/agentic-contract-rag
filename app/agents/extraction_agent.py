"""
Schema-driven extraction agent.

Extracts structured information from a contract by combining:

Schema
↓
Retriever
↓
Context Builder
↓
Prompt Builder
↓
LLM
"""

from __future__ import annotations

import json
from typing import Any

from app.llm.base import BaseLLM
from app.prompts.extraction_prompt import build_extraction_prompt
from app.retrieval.context_builder import ContextBuilder
from app.retrieval.retriever import Retriever
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ExtractionAgent:
    """
    Extract structured information from a contract using
    retrieval-augmented generation.
    """

    def __init__(
        self,
        retriever: Retriever,
        llm: BaseLLM,
    ) -> None:

        self.retriever = retriever
        self.llm = llm

    def extract(
        self,
        fields: list[dict[str, Any]],
    ) -> dict[str, Any]:

        extracted: dict[str, Any] = {}

        validation_notes: list[str] = []

        logger.info(
            f"Starting extraction for {len(fields)} fields."
        )

        for field in fields:

            path = field["path"]

            description = field.get(
                "description",
                "",
            )

            field_schema = field.get("schema")

            logger.info(
                f"Extracting field: {path}"
            )

            try:

                value = self._extract_single_field(
                    path,
                    description,
                    field_schema,
                )

                self._insert_value(
                    extracted,
                    path,
                    value,
                )

            except Exception as error:

                logger.exception(error)

                validation_notes.append(
                    f"Failed to extract '{path}'."
                )

        extracted["validation_notes"] = validation_notes

        logger.info(
            "Extraction completed."
        )

        return extracted

    def _extract_single_field(
        self,
        path: str,
        description: str,
        field_schema: dict[str, Any] | None = None,
    ) -> Any:
        """
        Retrieve context and extract a single schema field.
        """

        # Hierarchical retrieval
        retrieved = self.retriever.retrieve(
            path,
            k=5,
        )

        logger.info(
            f"Retrieved {len(retrieved)} chunks for {path}"
        )

        context = ContextBuilder.build(
            retrieved,
        )

        prompt = build_extraction_prompt(
            field_name=path,
            field_description=description,
            context=context,
            field_schema=field_schema,
        )

        response = self.llm.generate(
            prompt=prompt,
            temperature=0.0,
        )

        try:

            parsed = json.loads(response)

        except json.JSONDecodeError:

            logger.warning(
                f"Invalid JSON returned for {path}"
            )

            return None

        return parsed.get(path)

    @staticmethod
    def _insert_value(
        output: dict[str, Any],
        path: str,
        value: Any,
    ) -> None:
        """
        Insert a value into a nested dictionary.

        Example:

        fees.reimbursement_cap.amount

        becomes

        {
            "fees": {
                "reimbursement_cap": {
                    "amount": value
                }
            }
        }
        """

        parts = path.split(".")

        current = output

        for part in parts[:-1]:

            current = current.setdefault(
                part,
                {},
            )

        current[parts[-1]] = value