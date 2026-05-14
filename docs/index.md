# LegalDoc AI Engine

Welcome to the internal workflow engine for **Pearson Specter Litt**. This system is specifically engineered to automate the ingestion of complex, inconsistently formatted legal documents and transform them into high-fidelity, grounded draft outputs.

## Project Mission
The legal field often relies on data that is far from "clean". Our engine is built to cope with scanned pages, low-resolution PDFs, and noisy records, ensuring that no critical information is lost during the digitization process. Beyond mere extraction, the system anchors every generated draft in verifiable source evidence.

## Core Workflow
The system follows a five-stage lifecycle designed for reliability and iterative improvement:

1.  **Ingestion & OCR:** Processes messy source documents (scans, noisy PDFs) to extract usable text and structured fields.
2.  **Structured Extraction:** Organizes extracted content into data formats ready for downstream retrieval without further manual cleanup.
3.  **Grounded Retrieval:** Surfaces the exact passages and evidence needed for a specific drafting task.
4.  **Draft Generation:** Produces legal-style drafts (e.g., case summaries or internal memos) that are strictly grounded in retrieved evidence.
5.  **Learning Loop:** Captures operator edits to extract reusable patterns, allowing the system to improve automatically over time.

## Key Features for Operators
* **Evidence Inspection:** Every part of a generated draft can be traced back to the specific source material that supported it.
* **Edit Capture:** The system doesn't just store versions; it learns from your refinements to minimize future corrections.
* **Anti-Hallucination:** We prioritize grounded answering over generic generation, ensuring the output contains no unsupported assumptions.

## Technical Quick Links
* [**Architecture Overview:**](./architecture.md) Deep dive into the modular system design.
* [**Setup Guide:**](./setup.md) Instructions for local installation and Docker deployment.
* [**Evaluation Results:**](./evaluation.md) Detailed rubric breakdown and system performance metrics.


