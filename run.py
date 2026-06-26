from pathlib import Path
from typing import Optional

import typer

from app.ingestion.pdf_parser import PDFParser

app = typer.Typer()


@app.command()
def main(
    pdf: Path = typer.Option(
        ...,
        "--pdf",
        "-p",
        help="Path to the input contract PDF.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    )
):
    """
    Parse a contract PDF and extract its contents.
    """

    parser = PDFParser(pdf)

    pages = parser.extract_text()

    for page in pages:
        print("=" * 80)
        print(f"PAGE {page['page']}")
        print("=" * 80)
        print(page["text"][:500])


if __name__ == "__main__":
    app()