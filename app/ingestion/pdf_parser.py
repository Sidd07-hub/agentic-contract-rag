"""
PDF text extraction module.

Responsible for extracting clean text and metadata from PDF documents
while removing repeated headers and footers.
"""

from pathlib import Path
from typing import Any, Dict, List

import fitz  # PyMuPDF

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class PDFParser:
    """
    Extracts cleaned text and metadata from a PDF document.
    """

    def __init__(self, pdf_path: Path):
        """
        Initialize the PDF parser.

        Args:
            pdf_path: Path to the input PDF.
        """
        self.pdf_path = pdf_path

    @staticmethod
    def _clean_page_text(text: str) -> str:
        """
        Remove repeated headers, footers, and page numbers.

        Args:
            text: Raw page text.

        Returns:
            Cleaned page text.
        """

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        cleaned: List[str] = []
        skip_next = False

        for index, line in enumerate(lines):

            if skip_next:
                skip_next = False
                continue

            # Remove two-line repeated page header
            if "CWZ-MSA" in line:
                if (
                    index + 1 < len(lines)
                    and "CONFIDENTIAL" in lines[index + 1]
                ):
                    skip_next = True
                    continue

            # Remove footer
            if "CloudWayZ Solutions LLP" in line:
                continue

            # Remove page number
            if line.startswith("Page "):
                continue

            cleaned.append(line)

        return "\n".join(cleaned)

    def extract_text(self) -> List[Dict[str, Any]]:
        """
        Extract cleaned text from every page.

        Returns:
            List of page dictionaries.
        """

        if not self.pdf_path.exists():
            raise FileNotFoundError(
                f"PDF not found: {self.pdf_path}"
            )

        logger.info(f"Reading PDF: {self.pdf_path.name}")

        pages: List[Dict[str, Any]] = []

        try:
            with fitz.open(self.pdf_path) as document:

                for page_number, page in enumerate(document, start=1):

                    raw_text = page.get_text("text")

                    cleaned_text = self._clean_page_text(raw_text)

                    pages.append(
                        {
                            "page": page_number,
                            "text": cleaned_text,
                            "tables": [],
                            "metadata": {
                                "source": self.pdf_path.name,
                                "page_count": len(document),
                            },
                        }
                    )

        except Exception as error:
            logger.exception("Failed to parse PDF.")
            raise RuntimeError("Unable to parse PDF.") from error

        logger.info(
            f"Successfully extracted {len(pages)} pages."
        )

        return pages