"""
JSON Schema loader.

Loads and analyzes a JSON Schema while preserving its nested
structure for extraction and validation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class SchemaLoader:
    """
    Loads and analyzes a JSON Schema.
    """

    def __init__(self, schema_path: Path) -> None:

        self.schema_path = schema_path
        self.schema: dict[str, Any] = {}

    def load(self) -> dict[str, Any]:
        """
        Load schema from disk.
        """

        logger.info(
            f"Loading schema: {self.schema_path.name}"
        )

        with open(
            self.schema_path,
            "r",
            encoding="utf-8",
        ) as file:

            self.schema = json.load(file)

        logger.info("Schema loaded successfully.")

        return self.schema

    def get_schema(self) -> dict[str, Any]:

        if not self.schema:
            self.load()

        return self.schema

    def get_required_fields(self) -> list[str]:

        return self.get_schema().get(
            "required",
            [],
        )

    def get_properties(self) -> dict[str, Any]:

        return self.get_schema().get(
            "properties",
            {},
        )

    def iter_leaf_fields(self) -> list[dict[str, Any]]:
        """
        Returns every extractable field while preserving
        its location inside the schema.

        Example:

        provider.name

        provider.address.city

        termination.notice_period
        """

        fields: list[dict[str, Any]] = []

        self._walk_schema(
            self.get_properties(),
            "",
            fields,
        )

        return fields

    def _walk_schema(
        self,
        properties: dict[str, Any],
        prefix: str,
        output: list[dict[str, Any]],
    ) -> None:

        for name, schema in properties.items():

            path = (
                f"{prefix}.{name}"
                if prefix
                else name
            )

            field_type = schema.get(
                "type",
                "string",
            )

            # Nested object
            if (
                field_type == "object"
                and "properties" in schema
            ):

                self._walk_schema(
                    schema["properties"],
                    path,
                    output,
                )

                continue

            # Array
            if (
                field_type == "array"
                and "items" in schema
            ):

                output.append(
                    {
                        "path": path,
                        "type": "array",
                        "description": schema.get(
                            "description",
                            "",
                        ),
                        "schema": schema,
                    }
                )

                continue

            # Leaf field
            output.append(
                {
                    "path": path,
                    "type": field_type,
                    "description": schema.get(
                        "description",
                        "",
                    ),
                    "schema": schema,
                }
            )