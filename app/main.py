from __future__ import annotations

import os
import json
from typing import Any

from app.processing.loader import DocumentLoader
from app.processing.chunker import TextChunker


def run_ingestion_test(file_path: str):
    """
    Simulates the Pearson Specter Litt internal workflow for Phase 1.
    """
    print(f"🚀 Starting Ingestion: {file_path}")

    # 1. Initialize Phase 1 Components
    # Using threshold 50 to trigger OCR on messy/scanned pages [cite: 25]
    loader = DocumentLoader(ocr_threshold=50)
    chunker = TextChunker(chunk_size=500, overlap=100)

    try:
        # 2. Step 1: Hybrid Extraction
        # Handles low-resolution and partially illegible records [cite: 6, 26]
        print("📝 Extracting and cleaning text...")
        extracted_data = loader.load(file_path)

        # 3. Step 2: Semantic Segmentation
        # Produces structured data for downstream retrieval [cite: 27, 30]
        print("✂️ Chunking text for retrieval layer...")
        chunks = chunker.chunk_document(extracted_data)

        # 4. Display Results for Validation
        print("\n" + "=" * 50)
        print("📊 INGESTION SUMMARY")
        print("=" * 50)
        print(f"File: {extracted_data['source']}")
        print(f"Metadata: {json.dumps(extracted_data['metadata'], indent=2)}")
        print(f"Total Pages: {len(extracted_data['pages'])}")
        print(f"Total Chunks: {len(chunks)}")

        # Check for OCR usage [cite: 65]
        ocr_pages = [
            p["page_number"] for p in extracted_data["pages"] if p.get("is_ocr")
        ]
        if ocr_pages:
            print(f"⚠️ OCR triggered on pages: {ocr_pages}")
        else:
            print("✅ Native text extraction successful for all pages.")

        # 5. Show sample chunk for grounding check
        if chunks:
            print("\n🔍 SAMPLE CHUNK (Traceability Check):")
            sample = chunks[0]
            for sample in chunks:
                print(f"Source: {sample['metadata']['source']}")
                print(f"Page: {sample['metadata']['page_number']}")
                print(f"Content: {sample['content'][:150]}...")

        return chunks

        # # 5. Display Full Content [cite: 27, 34]
        # if chunks:
        #     print("\n📄 FULL EXTRACTED CONTENT:")
        #     print("-" * 50)

        #     # To avoid seeing overlaps in a single terminal scroll,
        #     # we iterate and print with clear markers.
        #     for i, chunk in enumerate(chunks):
        #         print(f"[Chunk {i + 1} | Page {chunk['metadata']['page_number']}]")
        #         print(chunk["content"])
        #         print(
        #             "-" * 30
        #         )  # Visual separator for grounded inspection [cite: 34, 73]

        # return chunks

    except Exception as e:
        print(f"❌ Error during processing: {e}")


if __name__ == "__main__":
    # Test with a sample file - update this path as needed
    target_file = "tests/files/PublicWaterMassMailing.pdf"

    if os.path.exists(target_file):
        run_ingestion_test(target_file)
    else:
        print(f"❌ File not found: {target_file}. Run 'task init' to generate samples.")
