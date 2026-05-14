# Sample Inputs and Outputs

This document provides concrete examples of how the LegalDoc AI Engine processes complex documents, retrieves specific technical evidence, and learns from operator refinements.

## 1. Document Ingestion (Input)

### Scenario: High-Density Technical Paper
* **Input File**: `arxiv_1706_03762.pdf` (Attention Is All You Need)
* **Status**: Digital PDF with complex mathematical notation and multi-column layout.

### Processing Workflow:
1. **Extraction**: Native text extraction identifies key sections and symbols.
2. **Chunking**: The system segments the paper into semantically coherent blocks (e.g., "Scaled Dot-Product Attention" section on Page 4).
3. **Indexing**: Chunks are embedded and stored in the vector store with precise source mapping.


---

## 2. Grounded Retrieval (Intermediate)

### Operator Query:
> `/retrieve "What is the formula for Scaled Dot-Product Attention?"`

### Retrieved Context:
* **Source**: `1706.03762v7.pdf`, Page 4.
* **Context IDs**: `["1706.03762v7.pdf_page_4_chunk_1", "1706.03762v7.pdf_page_4_chunk_5"]`
* **Content Snippet**: *"We call our particular attention 'Scaled Dot-Product Attention'... The input consists of queries and keys of dimension $d_k$, and values of dimension $d_v$."*

---
## 3. Draft Generation (Output)

### Operator Command:
> `/generate "Explain the role of Multi-Head Attention in the Transformer encoder."`

### Generated Draft (Initial):
> **RESPONSE:**
> The formula for Scaled Dot-Product Attention involves using dot products between queries and keys to weight the values. This allows the model to attend to different parts of the sequence.

---

## 4. Learning Loop (Improvement)

### Operator Edit (`/submit`):
The operator refines the draft to include rigorous mathematical detail and reasoning:

* **ID**: `transformer_formula_check_001`
* **Edited Version**: *"The formula is Attention(Q, K, V) = softmax((QK^T) / sqrt(d_k))V. It uses a scaling factor of 1/sqrt(d_k) to prevent dot products from growing too large in magnitude for the softmax function."*

### System Learning & Signal Extraction:
1. **Precision Capture**: The system identifies that for technical queries, the operator prefers explicit mathematical formulas over high-level descriptions.
2. **Context Association**: The system links the successful edit to the specific chunks in Page 4 of the paper.
3. **Future Behavior**: Subsequent requests for architecture formulas will now prioritize the "Formula + Rationale" structure in the generation phase.

---

## Evaluation Alignment
* **Handling of Complex Input**: Successfully parsed academic LaTeX-style PDF content.
* **Groundedness**: Every component of the operator's edit is directly supported by the retrieved context IDs.
* **Improvement from Edits**: Demonstrates how a generic draft is transformed into a high-utility technical response through the feedback loop.