"""
Embedding model for semantic document chunks.
"""

from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL
import numpy as np

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class EmbeddingModel:
    """
    Wrapper around SentenceTransformer.
    """

    MODEL_NAME = EMBEDDING_MODEL

    def __init__(self) -> None:

        logger.info(
            f"Loading embedding model: {self.MODEL_NAME}"
        )

        self.model = SentenceTransformer(
            self.MODEL_NAME
        )

        logger.info("Embedding model loaded successfully.")

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for one text.

        Args:
            text: Input text.

        Returns:
            Embedding vector.
        """

        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        return embedding

    def embed_documents(
        self,
        texts: list[str],
    ) -> np.ndarray:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of chunk texts.

        Returns:
            Matrix of embeddings.
        """

        logger.info(
            f"Generating embeddings for {len(texts)} chunks."
        )

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=True,
        )

        logger.info("Embeddings generated successfully.")

        return embeddings