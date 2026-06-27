"""
Validator Agent.

Validates extracted contract data using:
1. JSON Schema conformance checks.
2. Null-field detection.
3. LLM-powered contradiction and conflict detection against the
   full source document.
"""

from __future__ import annotations

import json
from typing import Any

from jsonschema import Draft202012Validator

from app.llm.base import BaseLLM
from app.prompts.validation_prompt import (
    VALIDATION_SYSTEM_PROMPT,
    build_validation_prompt,
)
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ValidatorAgent:
    """
    Validates extracted contract information using schema checks
    and LLM-powered contradiction detection.
    """

    def __init__(
        self,
        schema: dict[str, Any],
        llm: BaseLLM,
        full_document_text: str,
    ) -> None:

        self.schema = schema
        self.validator = Draft202012Validator(schema)
        self.llm = llm
        self.full_document_text = full_document_text

    def validate(
        self,
        extracted: dict[str, Any],
    ) -> dict[str, Any]:

        notes: list[dict[str, str]] = []

        # Step 1: JSON Schema validation
        self._validate_schema(
            extracted,
            notes,
        )

        # Step 2: Null-field detection
        self._validate_nulls(
            extracted,
            notes,
        )

        # Step 3: LLM-powered contradiction and conflict detection
        self._validate_with_llm(
            extracted,
            notes,
        )

        extracted["validation_notes"] = notes

        logger.info(
            f"Validation completed with {len(notes)} issue(s)."
        )

        return extracted

    # ---------------------------------------------------------
    # Step 1: JSON Schema Validation
    # ---------------------------------------------------------

    def _validate_schema(
        self,
        extracted: dict[str, Any],
        notes: list[dict[str, str]],
    ) -> None:

        errors = sorted(
            self.validator.iter_errors(extracted),
            key=lambda e: list(e.path),
        )

        for error in errors:

            field = ".".join(map(str, error.path))

            if not field:
                field = "root"

            notes.append(
                {
                    "field": field,
                    "issue": error.message,
                    "severity": "high",
                }
            )

    # ---------------------------------------------------------
    # Step 2: Null Detection
    # ---------------------------------------------------------

    def _validate_nulls(
        self,
        obj: Any,
        notes: list[dict[str, str]],
        path: str = "",
    ) -> None:

        if isinstance(obj, dict):

            for key, value in obj.items():

                new_path = (
                    f"{path}.{key}"
                    if path
                    else key
                )

                self._validate_nulls(
                    value,
                    notes,
                    new_path,
                )

            return

        if isinstance(obj, list):

            for index, item in enumerate(obj):

                self._validate_nulls(
                    item,
                    notes,
                    f"{path}[{index}]",
                )

            return

        if obj is None:

            notes.append(
                {
                    "field": path,
                    "issue": "Value could not be extracted from the contract.",
                    "severity": "medium",
                }
            )

    # ---------------------------------------------------------
    # Step 3: LLM-Powered Contradiction Detection
    # ---------------------------------------------------------

    def _validate_with_llm(
        self,
        extracted: dict[str, Any],
        notes: list[dict[str, str]],
    ) -> None:
        """
        Send the full document text and extracted data to the LLM
        to detect contradictions, conflicts, and errors.
        """

        logger.info(
            "Running LLM-powered contradiction detection..."
        )

        prompt = build_validation_prompt(
            extracted_json=extracted,
            full_document_text=self.full_document_text,
        )

        try:
            # Use the validation-specific system prompt
            # by temporarily generating with it
            response = self.llm.generate_with_system(
                prompt=prompt,
                system_prompt=VALIDATION_SYSTEM_PROMPT,
                temperature=0.0,
            )

            parsed = json.loads(response)

            llm_issues = parsed.get("issues", [])

            logger.info(
                f"LLM detected {len(llm_issues)} issue(s)."
            )

            for issue in llm_issues:
                # Validate the issue structure before adding
                if all(k in issue for k in ("field", "issue", "severity")):
                    # Ensure severity is valid
                    if issue["severity"] not in ("low", "medium", "high"):
                        issue["severity"] = "medium"
                    notes.append(issue)

        except json.JSONDecodeError:
            logger.warning(
                "LLM returned invalid JSON during validation."
            )
            notes.append(
                {
                    "field": "validation_notes",
                    "issue": "LLM validator returned unparseable response.",
                    "severity": "low",
                }
            )

        except Exception as error:
            logger.exception(
                "LLM validation failed."
            )
            notes.append(
                {
                    "field": "validation_notes",
                    "issue": f"LLM validation error: {error}",
                    "severity": "low",
                }
            )