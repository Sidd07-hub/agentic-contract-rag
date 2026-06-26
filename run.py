"""
Main entry point for the Agentic Contract RAG pipeline.
"""

from __future__ import annotations

import json
from pathlib import Path

import typer

from app.agents.extraction_agent import ExtractionAgent
from app.agents.validator_agent import ValidatorAgent
from app.chunking.semantic_chunker import SemanticChunker
from app.config import OUTPUT_DIR
from app.embeddings.embedding_model import EmbeddingModel
from app.ingestion.document_builder import DocumentBuilder
from app.ingestion.pdf_parser import PDFParser
from app.ingestion.table_parser import TableParser
from app.llm.groq_provider import GroqProvider
from app.retrieval.retriever import Retriever
from app.schemas import schema_loader
from app.schemas.schema_loader import SchemaLoader
from app.vectorstore.faiss_store import FAISSStore
from app.vectorstore.vector_document import VectorDocument

app = typer.Typer()


@app.command()
def main(
    pdf: Path = typer.Option(
        ...,
        "--pdf",
        "-p",
        exists=True,
        readable=True,
        help="Path to contract PDF.",
    ),
    schema: Path = typer.Option(
        ...,
        "--schema",
        "-s",
        exists=True,
        readable=True,
        help="Path to extraction schema.",
    ),
):
    """
    Execute the complete extraction pipeline.
    """

    print("\n")
    print("=" * 80)
    print("AGENTIC CONTRACT RAG PIPELINE")
    print("=" * 80)

    # --------------------------------------------------
    # 1. Parse PDF
    # --------------------------------------------------

    pages = PDFParser(pdf).extract_text()

    tables = TableParser(pdf).extract_tables()

    document = DocumentBuilder.build(
        pages,
        tables,
    )

    # --------------------------------------------------
    # 2. Chunk
    # --------------------------------------------------

    chunker = SemanticChunker()

    chunks = chunker.chunk_document(document)

    # --------------------------------------------------
    # 3. Embeddings
    # --------------------------------------------------

    embedding_model = EmbeddingModel()

    embeddings = embedding_model.embed_documents(
        [chunk.text for chunk in chunks]
    )

    # --------------------------------------------------
# 4. Build Vector Documents
# --------------------------------------------------

    vector_documents: list[VectorDocument] = []

    for chunk, embedding in zip(chunks, embeddings):

        vector_documents.append(
            VectorDocument(
                chunk=chunk,
                embedding=embedding,
            )
        )
    vector_store = FAISSStore()

    vector_store.build(vector_documents)
    # --------------------------------------------------
    # 5. Load Schema
    # --------------------------------------------------

    schema_loader = SchemaLoader(schema)

    schema_loader.load()

    fields = schema_loader.iter_leaf_fields()

    # --------------------------------------------------
    # 6. Retriever
    # --------------------------------------------------

    retriever = Retriever(
        embedding_model,
        vector_store,
    )

    # --------------------------------------------------
    # 7. LLM
    # --------------------------------------------------

    llm = GroqProvider()

    # --------------------------------------------------
    # 8. Extraction
    # --------------------------------------------------

    extractor = ExtractionAgent(
        retriever,
        llm,
    )

    extracted = extractor.extract(fields)

    # --------------------------------------------------
    # 9. Validation
    # --------------------------------------------------

    validator = ValidatorAgent(
        schema_loader.get_schema()
    )

    validated = validator.validate(extracted)

    # --------------------------------------------------
    # 10. Save JSON
    # --------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = OUTPUT_DIR / "output.json"

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            validated,
            file,
            indent=4,
            ensure_ascii=False,
        )

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    print("\n")
    print("=" * 80)
    print("PIPELINE COMPLETED")
    print("=" * 80)

    print(f"Pages           : {len(pages)}")
    print(f"Chunks          : {len(chunks)}")
    print(f"Embedding Shape : {embeddings.shape}")
    print(f"Output          : {output_path}")

    print("\nDone ✅")


if __name__ == "__main__":
    app()