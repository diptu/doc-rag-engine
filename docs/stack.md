# Technology Stack

The LegalDoc AI Engine is built using a modern, modular Python stack designed for high-performance document processing and reliable retrieval-augmented generation (RAG).

## Core Language & Environment
* **Python 3.11+**: Chosen for its robust ecosystem in data science and machine learning.
* **Docker & Docker Compose**: Ensures environment parity and simplifies the reviewer's setup process.
* **Virtualenv / Pip**: Standard package management for dependency isolation.

## Document Processing (Ingestion)
* **PyMuPDF (fitz)**: Used for high-speed, native PDF text and metadata extraction.
* **Tesseract OCR**: Serves as the fallback engine for scanned or low-resolution documents, ensuring no "messy" data is lost.
* **python-magic**: Used for reliable file type identification and validation.

## Retrieval & Vector Search
* **FAISS (Facebook AI Similarity Search)**: Provides the core vector indexing and similarity search capabilities for efficient context retrieval.
* **Sentence-Transformers**: Utilized for generating high-quality semantic embeddings from legal text chunks.
* **NumPy / Pandas**: Handles structured data manipulation and mathematical operations during the chunking and indexing phases.

## Generation & LLM Orchestration
* **OpenAI / Anthropic API**: Powers the grounded generation layer (configurable via `.env`).
* **Pydantic**: Enforces strict data validation and schema definitions for API responses and grounded outputs.
* **Uvicorn / FastAPI**: (Or Flask/Gunicorn) Provides the high-performance asynchronous web interface for the engine.

## Documentation & Tooling
* **MkDocs (ReadTheDocs Theme)**: Powers the professional-grade documentation site.
* **Mermaid.js**: Renders dynamic architecture and sequence diagrams directly in the documentation.
* **Pytest**: Drives the automated testing suite to ensure module reliability.

## Why This Stack?
This specific combination was selected to maximize **modularity** and **maintainability**—two key pillars of the Pearson Specter Litt engineering rubric. By separating OCR, Vector Search, and Generation into distinct modules, the system remains scalable and easy for an operator to audit.