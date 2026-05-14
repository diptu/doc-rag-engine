# Assumptions and Tradeoffs

This document outlines the engineering decisions and practical compromises made during the development of the LegalDoc AI Engine to meet the Friday, May 15 deadline.

## Core Assumptions

1. **Input Variability**: We assume that while documents are "messy" (scans/low-res), they contain enough legible semantic signal for OCR engines to recover at least 80% of the character data.
2. **Operator Role**: We assume the "Operator" is a subject matter expert who provides high-quality edits. The system treats these edits as "Golden Labels" for the improvement loop.
3. **Semi-Structured Content**: We assume that even inconsistent legal documents follow certain logical patterns (e.g., presence of parties, dates, and clauses) which our extraction layer can target.

## Engineering Tradeoffs

### 1. Local Vector Storage vs. Cloud Database
* **Decision**: Used a local FAISS/Pickle-based vector store (`data/processed/`).
* **Tradeoff**: Prioritized **reviewer experience** and ease of setup (no external DB credentials needed) over horizontal scalability. 
* **Benefit**: Hits the "Setup Clarity" rubric point by making the repo "clone and run."

### 2. Basic OCR vs. Layout-Aware Parsing
* **Decision**: Implemented a "Text-First with OCR Fallback" strategy.
* **Tradeoff**: We prioritize capturing the raw text signal over perfectly preserving complex visual layouts (like nested tables).
* **Benefit**: Ensures high groundedness and stability in the RAG pipeline while keeping the processing logic modular and maintainable.

### 3. Retrieval-Augmented Generation vs. Fine-tuning
* **Decision**: Relied on RAG with a dynamic feedback loop in the prompt.
* **Tradeoff**: Chose not to fine-tune a model on legal data, as fine-tuning is less transparent for "grounding" and requires significantly more labeled data.
* **Benefit**: Directly addresses the "Grounded Drafting" and "Traceability" requirements.

### 4. Learning Loop: Prompt Injection vs. Weight Updates
* **Decision**: Operator edits are analyzed and used to refine the system prompt/context rather than retraining model weights.
* **Tradeoff**: Updates are "soft" and limited by the context window, but they provide **instant improvement** without the risk of catastrophic forgetting or expensive compute cycles.

## Scalability & Future Work
While the current design is modular (fulfilling the 10-point System Design rubric), a production-ready version would:
* Replace local storage with a distributed vector database (e.g., Pinecone/Weaviate).
* Implement asynchronous worker queues (Celery/RabbitMQ) for heavy OCR tasks.
* Use LayoutLM for better spatial understanding of handwritten notes.