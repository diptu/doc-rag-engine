import torch
import numpy as np
from typing import List, Union
from sentence_transformers import SentenceTransformer


class Embedder:
    """
    Handles the transformation of text chunks into dense vector representations.
    Utilizes SentenceTransformers with automatic hardware acceleration detection.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = None):
        """
        Initializes the embedding model.

        Args:
            model_name (str): The identifier for the pre-trained model.
            device (str): Device to run the model on ('cuda', 'mps', or 'cpu').
                         If None, it is automatically detected.
        """
        # Auto-detect best available hardware (CUDA for NVIDIA, MPS for Apple Silicon)
        if device is None:
            if torch.cuda.is_available():
                self.device = "cuda"
            elif torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"
        else:
            self.device = device

        print(f"Initializing Embedder on device: {self.device}")

        # Load the model onto the specific device
        self.model = SentenceTransformer(model_name, device=self.device)

    def encode(self, texts: Union[str, List[str]], batch_size: int = 32) -> np.ndarray:
        """
        Converts text input into a batch of embeddings.

        Args:
            texts (Union[str, List[str]]): A single string or a list of strings to encode.
            batch_size (int): Number of texts to process simultaneously.

        Returns:
            np.ndarray: A matrix of shape (num_texts, embedding_dimension) in float32.
        """
        if isinstance(texts, str):
            texts = [texts]

        # convert_to_numpy=True ensures compatibility with FAISS
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=False,
        )

        return embeddings.astype("float32")

    @property
    def dimension(self) -> int:
        """Returns the output dimension of the current embedding model."""
        # Fix: Updated to the non-deprecated method name
        return self.model.get_embedding_dimension()
