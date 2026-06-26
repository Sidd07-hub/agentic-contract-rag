"""
Validator Agent.

Validates extracted contract data against the JSON Schema.
Only performs additional checks that JSON Schema cannot express.
"""

from __future__ import annotations

from typing import Any

from jsonschema import Draft202012Validator

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ValidatorAgent:
    """
    Validates extracted contract information.
    """

    def __init__(
        self,
        schema: dict[str, Any],
    ) -> None:

        self.schema = schema
        self.validator = Draft202012Validator(schema)

    def validate(
        self,
        extracted: dict[str, Any],
    ) -> dict[str, Any]:

        notes: list[dict[str, str]] = []

        self._validate_schema(
            extracted,
            notes,
        )

        self._validate_nulls(
            extracted,
            notes,
        )

        extracted["validation_notes"] = notes

        logger.info(
            f"Validation completed with {len(notes)} issue(s)."
        )

        return extracted

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