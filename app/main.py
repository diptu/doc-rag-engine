from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI(
    title="Pearson Specter Litt RAG Engine",
    description="Internal workflow for ingesting messy legal documents and generating grounded drafts[cite: 4, 5].",
    version="0.1.0",
)

# Include Phase 1 routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
async def root():
    return {"message": "RAG Engine API is operational", "phase": 1}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
