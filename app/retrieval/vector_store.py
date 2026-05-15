import os
import pickle
from typing import Any, Dict, List, Optional

import faiss  # type: ignore[import-untyped]
import numpy as np


class VectorStore:
    """
    Manages a FAISS index and associated metadata for semantic retrieval.
    Provides persistence to disk and similarity search orchestration.
    """

    def __init__(self, dimension: int):
        """
        Initializes the VectorStore using L2 distance.
        Note: For L2, a score of 0.0 is a perfect match.
        """
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata: List[Dict[str, Any]] = []

    def add(self, embeddings: np.ndarray, documents: List[Dict[str, Any]]):
        """
        Adds vectors to the index and links them to metadata.
        """
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)

        if embeddings.shape[1] != self.dimension:
            raise ValueError(
                f"Embedding dimension {embeddings.shape[1]} mismatch with index {self.dimension}"
            )

        # FAISS requires float32
        self.index.add(embeddings.astype("float32"))
        self.metadata.extend(documents)

    def search(
        self, query_vector: np.ndarray, k: int = 5, threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves the top-K most similar documents.

        Args:
            query_vector: The encoded query.
            k: Number of results to return.
            threshold: Maximum L2 distance allowed (lower is closer).
                       If results are empty, try increasing this to 1.5 or 2.0.
        """
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)

        # Perform search
        distances, indices = self.index.search(query_vector.astype("float32"), k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            # FAISS returns -1 if no neighbors are found
            if idx == -1:
                continue

            # LOGIC FIX: In L2 distance, we want dist <= threshold.
            # If dist is GREATER than threshold, it's too far away.
            if threshold is not None and dist > threshold:
                continue

            results.append(
                {"score": round(float(dist), 4), "content": self.metadata[idx]}
            )

        return results

    def save(self, directory: str, filename_prefix: str = "vector_store"):
        """Serializes the FAISS index and metadata to disk."""
        os.makedirs(directory, exist_ok=True)

        index_path = os.path.join(directory, f"{filename_prefix}.index")
        meta_path = os.path.join(directory, f"{filename_prefix}.pkl")

        faiss.write_index(self.index, index_path)
        with open(meta_path, "wb") as f:
            pickle.dump(self.metadata, f)

    @classmethod
    def load(
        cls, directory: str, filename_prefix: str = "vector_store"
    ) -> "VectorStore":
        """Loads a VectorStore instance from disk."""
        index_path = os.path.join(directory, f"{filename_prefix}.index")
        meta_path = os.path.join(directory, f"{filename_prefix}.pkl")

        if not os.path.exists(index_path) or not os.path.exists(meta_path):
            raise FileNotFoundError(f"Vector store files not found in {directory}")

        index = faiss.read_index(index_path)
        with open(meta_path, "rb") as f:
            metadata = pickle.load(f)

        instance = cls(dimension=index.d)
        instance.index = index
        instance.metadata = metadata
        return instance
