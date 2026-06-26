"""
Pydantic models used throughout the contract extraction pipeline.
"""

from typing import Any

from pydantic import BaseModel, Field


class ContractField(BaseModel):
    """
    Represents a single field discovered in the JSON schema.
    """

    path: str
    field_type: str
    description: str = ""


class ChunkReference(BaseModel):
    """
    Metadata about a retrieved chunk.
    """

    chunk_id: str
    title: str
    pages: list[int]
    similarity: float


class ExtractionResult(BaseModel):
    """
    Result returned after extracting a single field.
    """

    field: str
    value: Any = None

    confidence: float = 0.0

    chunk_references: list[ChunkReference] = Field(
        default_factory=list
    )

    validation_notes: list[str] = Field(
        default_factory=list
    )


class ContractExtraction(BaseModel):
    """
    Final extracted contract.
    """

    data: dict[str, Any] = Field(
        default_factory=dict
    )

    validation_notes: list[str] = Field(
        default_factory=list
    )


class ValidationResult(BaseModel):
    """
    Result of schema validation.
    """

    is_valid: bool

    validation_notes: list[str] = Field(
        default_factory=list
    )