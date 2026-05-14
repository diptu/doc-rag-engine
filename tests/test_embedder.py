import pytest
import numpy as np
import torch
from app.retrieval.embedder import Embedder


@pytest.fixture(scope="module")
def embedder():
    """Module-scoped fixture to avoid reloading the model for every test."""
    return Embedder(model_name="all-MiniLM-L6-v2")


def test_embedder_initialization_device(embedder):
    """Verify the embedder selects the best available hardware."""
    if torch.cuda.is_available():
        assert embedder.device == "cuda"
    elif torch.backends.mps.is_available():
        assert embedder.device == "mps"
    else:
        assert embedder.device == "cpu"


def test_embedder_output_dimension(embedder):
    """Verify the output dimension matches the model's reported dimension."""
    text = "Testing embedding dimensions."
    embedding = embedder.encode(text)

    assert embedding.shape == (1, embedder.dimension)
    # all-MiniLM-L6-v2 should specifically be 384
    assert embedder.dimension == 384


def test_embedder_batch_encoding(embedder):
    """Verify that multiple inputs are processed into a 2D matrix."""
    texts = ["Hello world", "Machine Learning is fun", "FAISS is fast"]
    embeddings = embedder.encode(texts)

    assert embeddings.shape == (3, embedder.dimension)
    assert embeddings.dtype == np.float32


def test_embedder_single_vs_list(embedder):
    """Ensure the encode method handles both strings and lists gracefully."""
    single = embedder.encode("String")
    multiple = embedder.encode(["String"])

    np.testing.assert_array_almost_equal(single, multiple)
