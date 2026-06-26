from dataclasses import dataclass

import numpy as np

from app.chunking.metadata import DocumentChunk


@dataclass
class VectorDocument:
    """
    Represents a semantic chunk together with its embedding.
    """

    chunk: DocumentChunk
    embedding: np.ndarray