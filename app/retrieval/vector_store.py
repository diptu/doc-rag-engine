import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Any, Optional


class VectorStore:
    """
    Manages a FAISS index and associated metadata for semantic retrieval.
    Provides persistence to disk and similarity search orchestration.
    """

    def __init__(self, dimension: int):
        """
        Initializes the VectorStore.

        Args:
            dimension (int): The dimensionality of the vectors (must match Embedder output).
        """
        self.dimension = dimension
        # IndexFlatL2 measures squared Euclidean distance
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata: List[Dict[str, Any]] = []

    def add(self, embeddings: np.ndarray, documents: List[Dict[str, Any]]):
        """
        Adds vectors to the index and links them to metadata.

        Args:
            embeddings (np.ndarray): Matrix of shape (N, dimension).
            documents (List[Dict]): Metadata for each vector.
        """
        if embeddings.shape[1] != self.dimension:
            raise ValueError(
                f"Embedding dimension {embeddings.shape[1]} mismatch with index {self.dimension}"
            )

        self.index.add(embeddings.astype("float32"))
        self.metadata.extend(documents)

    def search(
        self, query_vector: np.ndarray, k: int = 5, threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves the top-K most similar documents.

        Args:
            query_vector (np.ndarray): The encoded query (1, dimension).
            k (int): Number of results to return.
            threshold (float): Optional distance threshold (L2 distance).

        Returns:
            List[Dict]: Results containing 'score' and 'content'.
        """
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)

        distances, indices = self.index.search(query_vector.astype("float32"), k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue

            if threshold is not None and dist > threshold:
                continue

            results.append({"score": float(dist), "content": self.metadata[idx]})

        return results

    def save(self, directory: str, filename_prefix: str = "vector_store"):
        """
        Serializes the FAISS index and metadata to disk.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)

        index_path = os.path.join(directory, f"{filename_prefix}.index")
        meta_path = os.path.join(directory, f"{filename_prefix}.pkl")

        faiss.write_index(self.index, index_path)
        with open(meta_path, "wb") as f:
            pickle.dump(self.metadata, f)

    @classmethod
    def load(
        cls, directory: str, filename_prefix: str = "vector_store"
    ) -> "VectorStore":
        """
        Loads a VectorStore instance from disk.
        """
        index_path = os.path.join(directory, f"{filename_prefix}.index")
        meta_path = os.path.join(directory, f"{filename_prefix}.pkl")

        if not os.path.exists(index_path) or not os.path.exists(meta_path):
            raise FileNotFoundError(f"Vector store files not found in {directory}")

        index = faiss.read_index(index_path)
        with open(meta_path, "rb") as f:
            # Fix: Using pickle.load() for retrieval
            metadata = pickle.load(f)

        instance = cls(dimension=index.d)
        instance.index = index
        instance.metadata = metadata
        return instance
