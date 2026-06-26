from pathlib import Path

import typer

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
        help="Path to the input contract PDF."
    )
):

    parser = PDFParser(pdf)
    pages = parser.extract_text()

    table_parser = TableParser(pdf)
    tables = table_parser.extract_tables()

    print("\n")
    print("=" * 80)
    print("TABLE SUMMARY")
    print("=" * 80)

    print(f"Pages : {len(pages)}")
    print(f"Tables: {len(tables)}")

    for table in tables:

        print(
            f"\nPage {table['page']} | "
            f"Table {table['table_index']} | "
            f"Rows: {len(table['rows'])}"
        )


if __name__ == "__main__":
    app()