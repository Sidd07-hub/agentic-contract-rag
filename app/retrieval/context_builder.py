"""
Builds LLM context from retrieved chunks.
"""

from app.vectorstore.vector_document import VectorDocument


class ContextBuilder:
    """
    Converts retrieved chunks into a clean context string.
    """

    @staticmethod
    def build(
        results: list[tuple[VectorDocument, float]],
    ) -> str:

        sections = []

        for document, score in results:

            chunk = document.chunk

            section = (
                f"Section: {chunk.metadata.title}\n"
                f"Pages: {chunk.metadata.pages}\n\n"
                f"{chunk.text}"
            )

            sections.append(section)

        return "\n\n" + ("-" * 80) + "\n\n".join(sections)