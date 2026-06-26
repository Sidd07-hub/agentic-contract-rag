from pathlib import Path

import typer

from app.chunking.semantic_chunker import SemanticChunker
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
    )
):

    pages = PDFParser(pdf).extract_text()

    tables = TableParser(pdf).extract_tables()

    document = DocumentBuilder.build(
        pages,
        tables,
    )

    chunker = SemanticChunker()

    chunks = chunker.chunk_document(document)

    print("\n")
    print("=" * 80)
    print("CHUNK SUMMARY")
    print("=" * 80)

    print(f"Total Chunks : {len(chunks)}")

    for chunk in chunks:

        print()

        print(chunk.metadata.chunk_id)

        print(chunk.metadata.title)

        print(f"Pages : {chunk.metadata.pages}")

        print(f"Tables: {chunk.metadata.table_count}")

        print("-" * 80)


if __name__ == "__main__":
    app()