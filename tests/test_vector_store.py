import pytest
import numpy as np
import os
import shutil
from app.retrieval.vector_store import VectorStore


@pytest.fixture
def temp_dir():
    """Creates a temporary directory for persistence tests."""
    path = "./tests/temp_data"
    os.makedirs(path, exist_ok=True)
    yield path
    if os.path.exists(path):
        shutil.rmtree(path)


@pytest.fixture
def store():
    """Initializes a VectorStore with 384 dimensions."""
    return VectorStore(dimension=384)


def test_add_and_search_logic(store):
    """Verify that we can retrieve the exact same document added."""
    # Create a unique vector (all ones)
    vector = np.ones((1, 384), dtype="float32")
    metadata = [{"text": "Target Document", "id": "123"}]

    store.add(vector, metadata)

    # Query with a similar vector
    results = store.search(vector, k=1)

    assert len(results) == 1
    assert results[0]["content"]["text"] == "Target Document"
    assert results[0]["score"] < 0.0001  # L2 distance should be near zero


def test_threshold_filtering(store):
    """Verify that the threshold correctly excludes distant results."""
    v1 = np.zeros((1, 384), dtype="float32")
    v2 = np.ones((1, 384), dtype="float32")  # Very far from zeros

    store.add(v1, [{"text": "Near"}])

    # Search with v2 but set a strict threshold
    results = store.search(v2, k=1, threshold=0.1)

    assert len(results) == 0


def test_persistence_cycle(store, temp_dir):
    """Verify the save and load functionality preserves index and metadata."""
    vector = np.random.rand(1, 384).astype("float32")
    metadata = [{"text": "Persistent data"}]

    store.add(vector, metadata)
    store.save(temp_dir, filename_prefix="test_store")

    # Load into a new instance
    new_store = VectorStore.load(temp_dir, filename_prefix="test_store")

    assert new_store.dimension == 384
    assert len(new_store.metadata) == 1
    assert new_store.metadata[0]["text"] == "Persistent data"


def test_mismatched_dimensions(store):
    """Ensure an error is raised when adding vectors of the wrong size."""
    wrong_vector = np.random.rand(1, 512).astype("float32")

    with pytest.raises(ValueError):
        store.add(wrong_vector, [{"text": "error"}])
