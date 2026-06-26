from pathlib import Path

import typer

from app.chunking.semantic_chunker import SemanticChunker
from app.embeddings.embedding_model import EmbeddingModel
from app.ingestion.document_builder import DocumentBuilder
from app.ingestion.pdf_parser import PDFParser
from app.ingestion.table_parser import TableParser
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
        help="Path to the contract PDF.",
    )
):
    """
    Run the complete RAG ingestion pipeline.
    """

    # --------------------------------------------------
    # Step 1: Extract PDF text
    # --------------------------------------------------
    pages = PDFParser(pdf).extract_text()

    # --------------------------------------------------
    # Step 2: Extract tables
    # --------------------------------------------------
    tables = TableParser(pdf).extract_tables()

    # --------------------------------------------------
    # Step 3: Build unified document
    # --------------------------------------------------
    document = DocumentBuilder.build(
        pages,
        tables,
    )

    # --------------------------------------------------
    # Step 4: Semantic chunking
    # --------------------------------------------------
    chunker = SemanticChunker()

    chunks = chunker.chunk_document(document)

    # --------------------------------------------------
    # Step 5: Generate embeddings
    # --------------------------------------------------
    embedding_model = EmbeddingModel()

    embeddings = embedding_model.embed_documents(
        [chunk.text for chunk in chunks]
    )

    # --------------------------------------------------
    # Step 6: Build vector documents
    # --------------------------------------------------
    vector_documents = []

    for chunk, embedding in zip(chunks, embeddings):

        vector_documents.append(
            VectorDocument(
                chunk=chunk,
                embedding=embedding,
            )
        )

    # --------------------------------------------------
    # Step 7: Build FAISS index
    # --------------------------------------------------
    store = FAISSStore()

    store.build(vector_documents)

    # --------------------------------------------------
    # Step 8: Test retrieval
    # --------------------------------------------------
    query = "termination clause"

    query_embedding = embedding_model.embed_text(query)

    results = store.search(
        query_embedding,
        k=3,
    )

    # --------------------------------------------------
    # Output
    # --------------------------------------------------
    print("\n")
    print("=" * 80)
    print("PIPELINE SUMMARY")
    print("=" * 80)

    print(f"Pages           : {len(pages)}")
    print(f"Chunks          : {len(chunks)}")
    print(f"Embedding Shape : {embeddings.shape}")

    print("\n")
    print("=" * 80)
    print(f"TOP RESULTS FOR: '{query}'")
    print("=" * 80)

    for rank, (document, score) in enumerate(results, start=1):

        print(f"\n#{rank}")

        print(f"Section    : {document.chunk.metadata.title}")

        print(f"Similarity : {score:.4f}")

        print(
            f"Pages      : {document.chunk.metadata.pages}"
        )


if __name__ == "__main__":
    app()

    from app.llm.groq_provider import GroqProvider

llm = GroqProvider()

response = llm.generate(
    "Reply with exactly one word: READY"
)

print("\n")
print("=" * 80)
print("LLM TEST")
print("=" * 80)
print(response)