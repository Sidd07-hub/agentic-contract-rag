"""
PDF table extraction module.

Responsible for extracting structured tables from PDF documents.
"""

from pathlib import Path
from typing import Any, Dict, List

import pdfplumber

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class TableParser:
    """
    Extract tables from PDF documents using pdfplumber.
    """

    def __init__(self, pdf_path: Path):
        """
        Initialize the table parser.

        Args:
            pdf_path: Path to the input PDF.
        """
        self.pdf_path = pdf_path

    def extract_tables(self) -> List[Dict[str, Any]]:
        """
        Extract all tables from the PDF.

        Returns:
            List containing extracted tables and metadata.
        """

        if not self.pdf_path.exists():
            raise FileNotFoundError(
                f"PDF not found: {self.pdf_path}"
            )

        logger.info(f"Extracting tables from: {self.pdf_path.name}")

        extracted_tables: List[Dict[str, Any]] = []

        try:

            with pdfplumber.open(self.pdf_path) as pdf:

                for page_number, page in enumerate(pdf.pages, start=1):

                    tables = page.extract_tables()

                    if not tables:
                        continue

                    for table_index, table in enumerate(tables, start=1):

                        extracted_tables.append(
                            {
                                "page": page_number,
                                "table_index": table_index,
                                "rows": table,
                            }
                        )

        except Exception as error:
            logger.exception("Failed to extract tables.")
            raise RuntimeError(
                "Unable to extract tables."
            ) from error

        logger.info(
            f"Extracted {len(extracted_tables)} tables."
        )

        return extracted_tables