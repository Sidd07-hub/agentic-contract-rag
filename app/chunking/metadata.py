"""
Metadata models for semantic document chunks.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ChunkMetadata:
    """
    Metadata associated with a semantic chunk.
    """

    chunk_id: str
    title: str
    section: str
    pages: list[int]

    source: str

    has_table: bool = False
    table_count: int = 0


@dataclass
class DocumentChunk:
    """
    Represents one semantic chunk.
    """

    text: str

    metadata: ChunkMetadata

    tables: list[list[Any]] = field(default_factory=list)