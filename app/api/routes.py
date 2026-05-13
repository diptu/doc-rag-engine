from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Any
import os
import shutil

from app.processing.loader import DocumentLoader
from app.processing.chunker import TextChunker

router = APIRouter()

# Initialize processing components
loader = DocumentLoader(ocr_threshold=50)  # Handles noisy/scanned files
chunker = TextChunker(chunk_size=500, overlap=100)


@router.post("/ingest", tags=["Document Intelligence & Pre-processing"])
async def ingest_document(file: UploadFile = File(...)) -> dict[str, Any]:
    """
    Ingests a document, performs hybrid extraction (OCR if needed),
    and returns structured chunks ready for retrieval[cite: 28, 67].
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400, detail="Invalid file type. Only PDFs are supported."
        )

    # Create temporary path for processing [cite: 98]
    raw_dir = "data/raw"
    os.makedirs(raw_dir, exist_ok=True)
    temp_path = os.path.join(raw_dir, file.filename)

    try:
        # Save uploaded file
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 1. Extraction: OCR/Text extraction over messy/noisy files [cite: 25, 65]
        extracted_data = loader.load(temp_path)

        # 2. Chunking: Produce data that downstream steps can use [cite: 27, 68]
        chunks = chunker.chunk_document(extracted_data)

        return {
            "source": file.filename,
            "metadata": extracted_data["metadata"],
            "total_pages": len(extracted_data["pages"]),
            "total_chunks": len(chunks),
            "chunks": chunks,  # Structured output for Phase 2 [cite: 28, 30]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    finally:
        # Cleanup: Keep data/raw clean or implement archival logic
        if os.path.exists(temp_path):
            os.remove(temp_path)
