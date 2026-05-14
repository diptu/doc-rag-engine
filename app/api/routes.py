from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from typing import Any, List, Optional
import os
import shutil

from app.processing.loader import DocumentLoader
from app.processing.chunker import TextChunker
from app.retrieval.embedder import Embedder
from app.retrieval.vector_store import VectorStore

router = APIRouter()

# --- Dependencies & Initialization ---
# Initialize Core Engines [cite: 25, 27]
loader = DocumentLoader(ocr_threshold=50)
chunker = TextChunker(chunk_size=500, overlap=100)

# In a production environment, these should be managed via FastAPI Lifespan
# Embedder dimension must match VectorStore dimension (384 for all-MiniLM-L6-v2)
embedder = Embedder()
vector_store = VectorStore(dimension=embedder.dimension)


# --- Pydantic Models for Phase 2 ---
class RetrievalRequest(BaseModel):
    prompt: str
    top_k: int = 5
    threshold: Optional[float] = None


class RetrievalResult(BaseModel):
    score: float
    content: dict[str, Any]


# --- Endpoints ---


@router.post("/ingest", tags=["Phase 1 & 2: Ingestion Pipeline"])
async def ingest_document(file: UploadFile = File(...)) -> dict[str, Any]:
    """
    Full Pipeline: Extracts text, chunks it, generates embeddings,
    and indexes them for retrieval[cite: 28, 30, 44].
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400, detail="Invalid file type. Only PDFs are supported."
        )

    raw_dir = "data/raw"
    os.makedirs(raw_dir, exist_ok=True)
    temp_path = os.path.join(raw_dir, file.filename)

    try:
        # Save file locally for processing
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 1. Extraction & Chunking (Phase 1) [cite: 25, 27, 28]
        extracted_data = loader.load(temp_path)
        chunks = chunker.chunk_document(extracted_data)

        # 2. Embedding & Indexing (Phase 2) [cite: 30, 36, 40]
        texts = [chunk["content"] for chunk in chunks]
        embeddings = embedder.encode(texts)
        vector_store.add(embeddings, chunks)

        # Optional: Persist index for future use
        processed_dir = "data/processed"
        vector_store.save(processed_dir)

        return {
            "source": file.filename,
            "total_chunks": len(chunks),
            "status": "Indexed and ready for retrieval",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.post(
    "/retrieve", response_model=List[RetrievalResult], tags=["Phase 2: Semantic Search"]
)
async def retrieve_evidence(request: RetrievalRequest) -> List[RetrievalResult]:
    """
    Performs semantic search to find the most relevant document chunks[cite: 32, 40, 46].
    """
    try:
        # 1. Vectorize the incoming query
        query_vector = embedder.encode(request.prompt)

        # 2. Search the FAISS index
        search_results = vector_store.search(
            query_vector=query_vector, k=request.top_k, threshold=request.threshold
        )

        return search_results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")
