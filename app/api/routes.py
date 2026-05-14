from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Any, List, Optional
import os
import shutil
from unittest.mock import MagicMock

# Core Engine Imports
from app.processing.loader import DocumentLoader
from app.processing.chunker import TextChunker
from app.retrieval.embedder import Embedder
from app.retrieval.vector_store import VectorStore

# Phase 3 & 4 Imports
from app.generation.generator import RAGGenerator
from app.generation.schemas import GenerationResponse
from app.feedback.analyzer import FeedbackAnalyzer
from app.feedback.schemas import (
    FeedbackEntry,
    FeedbackSubmitRequest,
)  # Ensure FeedbackSubmitRequest is in schemas.py

router = APIRouter()

# --- Dependencies & Initialization ---
loader = DocumentLoader(ocr_threshold=50)
chunker = TextChunker(chunk_size=500, overlap=100)
embedder = Embedder()
vector_store = VectorStore(dimension=embedder.dimension)

# Simulated LLM Client (e.g., OpenAI or local client)
# In production, use a singleton pattern or FastAPI Lifespan
llm_client = MagicMock()  # Replace with your actual client instance
generator = RAGGenerator(model_client=llm_client)
feedback_analyzer = FeedbackAnalyzer(llm_client=llm_client)


# --- Pydantic Models ---
class RetrievalRequest(BaseModel):
    prompt: str
    top_k: int = 5
    threshold: Optional[float] = None


class RetrievalResult(BaseModel):
    score: float
    content: dict[str, Any]


class RAGRequest(BaseModel):
    query: str
    top_k: int = 3


# --- Phase 1 & 2: Ingestion & Retrieval ---


@router.post("/ingest", tags=["Phase 1 & 2: Ingestion"])
async def ingest_document(file: UploadFile = File(...)) -> dict[str, Any]:
    """
    Full Pipeline: Extracts text, chunks it, generates embeddings,
    and indexes them for retrieval.
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

        # 1. Extraction & Chunking (Phase 1)
        extracted_data = loader.load(temp_path)
        chunks = chunker.chunk_document(extracted_data)

        # 2. Embedding & Indexing (Phase 2)
        texts = [chunk["content"] for chunk in chunks]
        embeddings = embedder.encode(texts)
        vector_store.add(embeddings, chunks)

        # Optional: Persist index
        processed_dir = "data/processed"
        os.makedirs(processed_dir, exist_ok=True)
        vector_store.save(processed_dir)

        return {
            "source": file.filename,
            "total_chunks": len(chunks),
            "status": "Indexed and ready for retrieval",
        }

    except Exception as e:
        # Log the error here in a real app
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

    finally:
        # Cleanup temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/retrieve", response_model=List[RetrievalResult])
async def retrieve_evidence(request: RetrievalRequest):
    # DEBUG LINE: Check if the store actually has data
    print(f"DEBUG: Vector Store has {len(vector_store.metadata)} chunks.")

    try:
        query_vector = embedder.encode(request.prompt)
        search_results = vector_store.search(
            query_vector=query_vector, k=request.top_k, threshold=request.threshold
        )
        return search_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Phase 3: Grounded Generation ---


@router.post(
    "/generate", response_model=GenerationResponse, tags=["Phase 3: Generation"]
)
async def generate_grounded_response(request: RAGRequest):
    """
    Combines retrieval and generation to provide a cited, grounded answer.
    """
    try:
        # 1. Retrieve relevant chunks
        query_vector = embedder.encode(request.query)
        search_results = vector_store.search(query_vector=query_vector, k=request.top_k)

        # Format for generator (list of dicts with 'content' and 'metadata')
        chunks = [res["content"] for res in search_results]

        # 2. Generate validated response
        response = await generator.generate(
            query=request.query, retrieved_chunks=chunks
        )
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


# --- Phase 4: Feedback & Alignment ---


@router.post("/feedback/submit", tags=["Phase 4: Feedback"])
async def submit_human_feedback(
    feedback: FeedbackSubmitRequest, background_tasks: BackgroundTasks
):
    """
    Endpoint to receive human corrections. Analysis runs in the background
    to extract signals for model alignment.
    """
    try:
        # In a real app, you'd fetch the original interaction from a DB here
        # For now, we trigger the background analysis task
        background_tasks.add_task(
            feedback_analyzer.analyze_and_map,
            interaction_id=feedback.interaction_id,
            query=feedback.query,
            original_draft=feedback.original_draft,
            edited_version=feedback.edited_version,
            context_ids=feedback.context_ids,
        )

        return {"status": "Feedback received. Analysis started in background."}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Feedback submission failed: {str(e)}"
        )


@router.get("/feedback/stats", tags=["Phase 4: Analytics"])
async def get_feedback_metrics():
    """
    Returns high-level stats on FACTUAL vs STYLE edits to monitor engine drift.
    """
    # Logic to query your feedback_logs.jsonl and aggregate counts
    return {"message": "Feature pending store.py implementation"}
