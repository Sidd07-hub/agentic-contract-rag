"""
Semantic retriever for the RAG pipeline.

Retrieves the most relevant semantic chunks from the FAISS vector
store based on a schema field or a custom query.
"""

from app.embeddings.embedding_model import EmbeddingModel
from app.retrieval.field_queries import FIELD_QUERIES
from app.vectorstore.faiss_store import FAISSStore
from app.vectorstore.vector_document import VectorDocument
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class Retriever:
    """
    Performs semantic retrieval over the FAISS vector store.
    """

    def __init__(
        self,
        embedding_model: EmbeddingModel,
        vector_store: FAISSStore,
    ) -> None:
        """
        Initialize the retriever.

        Args:
            embedding_model: Embedding model.
            vector_store: FAISS vector store.
        """

        self.embedding_model = embedding_model
        self.vector_store = vector_store

    def retrieve(
        self,
        field_name: str,
        k: int = 3,
    ) -> list[tuple[VectorDocument, float]]:
        """
        Retrieve the most relevant chunks for a schema field.

        Resolution order:

        1. Full field path
        fees.headline_fee

        2. Parent path
        fees

        3. Raise error if nothing exists.
        """

        query = FIELD_QUERIES.get(field_name)

        if query is None:

            parent = field_name.split(".")[0]

            query = FIELD_QUERIES.get(parent)

        if query is None:

            raise ValueError(
                f"No retrieval query defined for '{field_name}'."
            )

        logger.info(
            f"Searching field: {field_name}"
        )

        query_embedding = self.embedding_model.embed_text(query)

        return self.vector_store.search(
            query_embedding,
            k=k,
        )


    def retrieve_custom(
        self,
        query: str,
        k: int = 3,
    ) -> list[tuple[VectorDocument, float]]:
        """
        Retrieve chunks using a custom query.
        """

        logger.info(f"Custom query: {query}")

        query_embedding = self.embedding_model.embed_text(query)

        return self.vector_store.search(
            query_embedding,
            k=k,
        )