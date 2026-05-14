from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Any, List, Optional
import os

from dotenv import load_dotenv
import shutil
from openai import AsyncOpenAI

# Core Engine Imports
from app.processing.loader import DocumentLoader
from app.processing.chunker import TextChunker
from app.retrieval.embedder import Embedder
from app.retrieval.vector_store import VectorStore

# Phase 3 & 4 Imports
from app.generation.generator import RAGGenerator
from app.generation.schemas import GenerationResponse
from app.feedback.analyzer import FeedbackAnalyzer
from app.feedback.schemas import FeedbackSubmitRequest

load_dotenv()
router = APIRouter()

# --- Dependencies & Initialization ---
loader = DocumentLoader(ocr_threshold=50)
chunker = TextChunker(chunk_size=500, overlap=100)
embedder = Embedder()

# Persistence Configuration
PROCESSED_DIR = "data/processed"
INDEX_FILE = os.path.join(PROCESSED_DIR, "vector_store.index")

# Initialize VectorStore - Load if exists, else create new
if os.path.exists(INDEX_FILE):
    print(f"Loading existing vector store from {PROCESSED_DIR}...")
    vector_store = VectorStore.load(PROCESSED_DIR)
else:
    print("Initializing new empty vector store...")
    vector_store = VectorStore(dimension=embedder.dimension)

# --- LLM Client Configuration (OpenAI) ---
# Ensure you have exported your key: export api_key='sk-...'
llm_client = AsyncOpenAI(api_key=os.getenv("api_key"))

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


# --- Endpoints ---


@router.post("/ingest", tags=["Phase 1: Ingestion"])
async def ingest_document(file: UploadFile = File(...)) -> dict[str, Any]:
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDFs supported.")

    os.makedirs("data/raw", exist_ok=True)
    temp_path = f"data/raw/{file.filename}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        extracted_data = loader.load(temp_path)
        chunks = chunker.chunk_document(extracted_data)
        embeddings = embedder.encode([c["content"] for c in chunks])
        vector_store.add(embeddings, chunks)

        # PERSISTENCE: Save so data survives server reloads
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        vector_store.save(PROCESSED_DIR)

        return {
            "source": file.filename,
            "chunks": len(chunks),
            "status": "Indexed and Persisted",
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.post(
    "/retrieve", response_model=List[RetrievalResult], tags=["Phase 2: Retrieval"]
)
async def retrieve_evidence(request: RetrievalRequest):
    if not vector_store.metadata:
        print("WARNING: Search requested but Vector Store is empty.")

    try:
        query_vector = embedder.encode(request.prompt)
        search_results = vector_store.search(
            query_vector=query_vector, k=request.top_k, threshold=request.threshold
        )
        return search_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/generate", response_model=GenerationResponse, tags=["Phase 3: Generation"]
)
async def generate_grounded_response(request: RAGRequest):
    if not vector_store.metadata:
        raise HTTPException(
            status_code=404,
            detail="Vector store is empty. Please run /ingest with the paper first.",
        )

    try:
        # 1. Retrieve
        query_vector = embedder.encode(request.query)
        search_results = vector_store.search(query_vector=query_vector, k=request.top_k)
        context_chunks = [res["content"] for res in search_results]

        # 2. Generate (Now using real AsyncOpenAI client)
        response = await generator.generate(
            query=request.query, retrieved_chunks=context_chunks
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/feedback/submit", tags=["Phase 4: Feedback"])
async def submit_human_feedback(
    feedback: FeedbackSubmitRequest, background_tasks: BackgroundTasks
):
    try:
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
        raise HTTPException(status_code=500, detail=str(e))


# Ensure you have initialized the store at the top of your routes file
from app.feedback.store import FeedbackStore

feedback_store = FeedbackStore()


@router.get("/feedback/stats", tags=["Phase 4: Analytics"])
async def get_feedback_metrics():
    """
    Returns high-level stats on FACTUAL vs STYLE edits to monitor engine drift.
    """
    try:
        stats = feedback_store.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve analytics: {str(e)}"
        )
