# doc-rag-engine
A modular system that transforms messy documents into structured insights using OCR, retrieval, and grounded AI-driven draft generation.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Production-green)
![License](https://img.shields.io/badge/License-MIT-green)
## Overview

This project implements an end-to-end system for processing messy legal-style documents, retrieving relevant evidence, generating grounded draft outputs, and improving over time using operator edits.

## For This Version, will focus on:

- Reliable document extraction
- Evidence-based retrieval (RAG)
- Grounded draft generation with citations
- Simple feedback loop from user edits

## Scope
- Due to time constraints, this implementation prioritizes core functionality over completeness:
  
| Component | Status |
| -------- | -------- |
| Document Processing | :white_check_mark: Basic (PDF + OCR fallback) |
| Retrieval (RAG) |:white_check_mark: FAISS-based |
| Draft Generation|:white_check_mark:  Grounded with citations |
| Draft Generation|:white_check_mark:  Grounded with citations |
| API |:white_check_mark:  Minimal |
|UI | :negative_squared_cross_mark: not included|

## ⚙️ Tech Stack
- FastAPI (API layer)
- PyMuPDF + Tesseract (document processing)
- SentenceTransformers (embeddings)
- FAISS (vector search)
- OpenAI / LLM (generation)

## 📂 Project Structure
```
app/ ├── processing/ # OCR + text extraction
├── retrieval/ # embeddings + FAISS
├── generation/ # prompt + drafting
├── feedback/ # edit capture
├── api/ # endpoints
└── main.py

data/
├── raw/
├── processed/
└── feedback/

```

## 📄 Sample Workflow
 1. Upload Document: Input a scanned legal PDF.

 2. Processing: System performs OCR and generates structured chunks.

 3. Query Task: Request a grounded summary or memo.

 4. Output Structure:

```json
{ "summary": "...", "evidence": [ { "text": "...", "source": "doc.pdf", "page": 1 } ] }
```

## Learning from Edits

- Input: Original LLM output vs. final edited version.

- Process: Detects improvements in facts, clarity, or formatting.

- Optimization: Stored as reusable few-shot examples to tune future prompts.

## Evaluation Metrics
- Retrieval Relevance: Top-K accuracy and hit rate.

- Grounding Quality: Citation coverage and faithfulness.

- Improvement Velocity: Reduction in operator edit distance over time.

## Assumptions & Tradeoffs

### Assumptions
 - Input documents may be noisy or partially unreadable
 - Legal accuracy is not required

### Tradeoffs 
- No advanced layout parsing
- No fine-tuned models
- Simple feedback loop (no ML training)
Local FAISS instead of scalable DB

## Future Improvements

[ ] UI/UX: Dashboard for document upload and live editing.

[ ] Models: Fine-tuned domain-specific SLMs.

[ ] Vision: Advanced layout-aware parsing for tables and signatures.

[] Database: Scalable vector DB (e.g., Pinecone)

[] Handle file upload as a background jobs.(e.g., celery)


# Setup Guide

* [**Setup Instruction:**](./docs/setup.md) Deep dive into the modular system design.