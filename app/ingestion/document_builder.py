"""
Document builder module.

Combines extracted page text and tables into a unified document structure.
"""

from typing import Any, Dict, List


class DocumentBuilder:
    """
    Build a unified document representation.
    """

    @staticmethod
    def build(
        pages: List[Dict[str, Any]],
        tables: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Merge page text with extracted tables.

        Args:
            pages: Output from PDFParser.
            tables: Output from TableParser.

        Returns:
            Unified document structure.
        """

        page_lookup = {
            page["page"]: page
            for page in pages
        }

        for table in tables:

            page_number = table["page"]

            if page_number in page_lookup:
                page_lookup[page_number]["tables"].append(
                    table["rows"]
                )

        return list(page_lookup.values())