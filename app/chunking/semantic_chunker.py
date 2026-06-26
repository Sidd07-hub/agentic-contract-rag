"""
Semantic chunking for legal contract documents.

Creates semantic chunks using major legal section headings while
preserving tables and metadata.
"""

import re
from typing import Any

from app.chunking.metadata import ChunkMetadata, DocumentChunk
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class SemanticChunker:
    """
    Creates semantic chunks from parsed legal documents.
    """

    def chunk_document(
        self,
        document: list[dict[str, Any]],
    ) -> list[DocumentChunk]:

        chunks: list[DocumentChunk] = []

        current_lines: list[str] = []
        current_tables: list[list[Any]] = []
        current_pages: list[int] = []

        chunk_number = 1

        current_title = "Introduction"
        current_section = "0"
        current_source = ""

        for page in document:

            page_number = page["page"]

            current_source = page["metadata"]["source"]

            if page_number not in current_pages:
                current_pages.append(page_number)

            for line in page["text"].splitlines():

                line = line.strip()

                if not line:
                    continue

                if self._should_ignore(line):
                    continue

                if self._is_major_heading(line):

                    if current_lines:

                        chunks.append(
                            self._build_chunk(
                                chunk_number,
                                current_title,
                                current_section,
                                current_pages.copy(),
                                current_source,
                                current_lines,
                                current_tables,
                            )
                        )

                        chunk_number += 1

                    current_lines = []
                    current_tables = []
                    current_pages.clear()
                    current_pages.append(page_number)

                    current_title = line

                    if line.upper().startswith("SCHEDULE"):
                        current_section = line
                    else:
                        current_section = line.split(".", 1)[0]
                if page_number not in current_pages:
                    current_pages.append(page_number)
                current_lines.append(line)

            if page["tables"]:
                current_tables.extend(page["tables"])

        if current_lines:

            chunks.append(
                self._build_chunk(
                    chunk_number,
                    current_title,
                    current_section,
                    current_pages,
                    current_source,
                    current_lines,
                    current_tables,
                )
            )

        logger.info(
            f"Created {len(chunks)} semantic chunks."
        )

        return chunks

    @staticmethod
    def _should_ignore(line: str) -> bool:
        """
        Ignore isolated table values.
        """

        line = line.strip()

        upper = line.upper()

        if re.fullmatch(
            r"\d+\s*(MINUTES?|HOURS?|BUSINESS DAYS?|DAYS?)",
            upper,
        ):
            return True

        if re.fullmatch(
            r"\d{1,2}\s+[A-Z]+\s+\d{4}",
            upper,
        ):
            return True

        return False

    @staticmethod
    def _is_major_heading(line: str) -> bool:
        """
        Detect top-level legal section headings.
        """

        line = line.strip()

        # Match only top-level numbered headings (1., 2., 3., ...)
        if re.match(r"^\d+\.\s+", line):
            # Reject subsection headings like 2.1 or 10.2
            if re.match(r"^\d+\.\d+", line):
                return False
            return True

        # Match only real schedule headings
        if re.match(
            r"^SCHEDULE\s+[A-Z]\s+[—\-:]\s+.+",
            line,
            re.IGNORECASE,
        ):
            return True

        return False

    @staticmethod
    def _build_chunk(
        chunk_number: int,
        title: str,
        section: str,
        pages: list[int],
        source: str,
        lines: list[str],
        tables: list[list[Any]],
    ) -> DocumentChunk:

        metadata = ChunkMetadata(
            chunk_id=f"chunk_{chunk_number:03}",
            title=title,
            section=section,
            pages=sorted(set(pages)),
            source=source,
            has_table=len(tables) > 0,
            table_count=len(tables),
        )

        return DocumentChunk(
            text="\n".join(lines),
            metadata=metadata,
            tables=tables,
        )