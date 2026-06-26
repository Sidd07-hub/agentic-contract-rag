from pathlib import Path

import typer

from app.ingestion.document_builder import DocumentBuilder
from app.ingestion.pdf_parser import PDFParser
from app.ingestion.table_parser import TableParser

app = typer.Typer()


@app.command()
def main(
    pdf: Path = typer.Option(
        ...,
        "--pdf",
        "-p",
        exists=True,
        readable=True,
        help="Path to the input contract PDF.",
    )
):

    pages = PDFParser(pdf).extract_text()
    tables = TableParser(pdf).extract_tables()

    document = DocumentBuilder.build(
        pages,
        tables,
    )

    print("\n")
    print("=" * 80)
    print("DOCUMENT SUMMARY")
    print("=" * 80)

    print(f"Pages : {len(document)}")

    total_tables = sum(
        len(page["tables"])
        for page in document
    )

    print(f"Tables: {total_tables}")

    for page in document:
        print(
            f"Page {page['page']} | "
            f"Tables: {len(page['tables'])}"
        )


if __name__ == "__main__":
    app()