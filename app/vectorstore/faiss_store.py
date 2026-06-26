"""
FAISS vector store implementation.
"""

from pathlib import Path
import pickle

import faiss
import numpy as np

from app.vectorstore.vector_document import VectorDocument
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class FAISSStore:
    """
    Wrapper around FAISS for semantic retrieval.
    """

    def __init__(self):

        self.index = None
        self.documents: list[VectorDocument] = []

    def build(
        self,
        documents: list[VectorDocument],
    ) -> None:
        """
        Build a FAISS index.
        """

        if not documents:
            raise ValueError("No documents supplied.")

        self.documents = documents

        embeddings = np.vstack(
            [doc.embedding for doc in documents]
        ).astype("float32")

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(embeddings)

        logger.info(
            f"Indexed {len(documents)} semantic chunks."
        )

    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 5,
    ) -> list[tuple[VectorDocument, float]]:
        """
        Perform semantic search.
        """

        if self.index is None:
            raise RuntimeError("FAISS index not built.")

        query = (
            np.asarray(query_embedding)
            .astype("float32")
            .reshape(1, -1)
        )

        scores, indices = self.index.search(query, k)

        results = []

        for score, idx in zip(scores[0], indices[0]):

            if idx == -1:
                continue

            results.append(
                (
                    self.documents[idx],
                    float(score),
                )
            )

        return results

    def save(
        self,
        index_path: Path,
        metadata_path: Path,
    ) -> None:
        """
        Save FAISS index and metadata.
        """

        faiss.write_index(
            self.index,
            str(index_path),
        )

        with open(metadata_path, "wb") as file:
            pickle.dump(
                self.documents,
                file,
            )

        logger.info("FAISS index saved.")

    def load(
        self,
        index_path: Path,
        metadata_path: Path,
    ) -> None:
        """
        Load FAISS index and metadata.
        """

        self.index = faiss.read_index(
            str(index_path)
        )

        with open(metadata_path, "rb") as file:
            self.documents = pickle.load(file)

        logger.info("FAISS index loaded.")