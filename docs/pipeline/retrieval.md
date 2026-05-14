# Grounded Retrieval

The retrieval module is responsible for surfacing the exact evidence needed to support a generated draft. It ensures that the system remains anchored in the source documents rather than relying on the general knowledge of a language model.

## Retrieval Strategy

Our engine uses a dense retrieval approach to bridge the gap between noisy text and semantic meaning:

* **Vector Embeddings (`embedder.py`)**: Transforms document chunks into high-dimensional vectors that capture semantic intent.
* **Vector Store (`vector_store.py`)**: A local index that stores these embeddings, allowing for efficient similarity searches against operator queries or drafting requirements.
* **Contextual Anchoring**: The system identifies the specific source files and page segments that correspond to a query, providing the "ground truth" for the generation layer.

## Evidence Surfacing

To meet the engineering standards of Pearson Specter Litt, the retrieval process is optimized for:

1.  **Precision**: Filtering out irrelevant noise from messy documents to focus on legal facts.
2.  **Traceability**: Maintaining a direct link between every retrieved chunk and its original source location.
3.  **Grounding Support**: Supplying the generation module with a curated context window that prevents hallucination.

## Component Breakdown

| Module | Responsibility |
| :--- | :--- |
| `embedder.py` | Manages the generation of semantic embeddings for text chunks. |
| `vector_store.py` | Handles indexing, persistence, and querying of the vector database. |