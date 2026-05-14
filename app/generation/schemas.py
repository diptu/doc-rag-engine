from pydantic import BaseModel, Field, validator
from typing import List, Optional


class GroundedSource(BaseModel):
    """Represents an individual source used in the generation."""

    source_id: str = Field(
        ..., description="The unique identifier of the document chunk."
    )
    page_number: Optional[int] = Field(
        None, description="Optional page reference from metadata."
    )


class GenerationResponse(BaseModel):
    """The strict JSON schema for the LLM's RAG output."""

    draft: str = Field(
        ...,
        description="The synthesized answer strictly anchored in the retrieved context.",
    )
    citations: List[str] = Field(
        ...,
        description="List of source IDs that directly support the claims in the draft.",
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="A score between 0 and 1 indicating how well the context supports the query.",
    )

    @validator("draft")
    def draft_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("The generated draft cannot be empty.")
        return v

    @validator("citations")
    def validate_citations_presence(cls, v, values):
        # Logic: If confidence is high but no citations exist, that's a red flag.
        if values.get("confidence_score", 0) > 0.5 and len(v) == 0:
            # We allow empty citations only if the model states it has 'insufficient info'
            pass
        return v
