from pydantic import BaseModel, Field
from typing import Any

class VerdictResponse(BaseModel):
    claim_id: str
    verdict: str
    confidence: float
    explanation: str
    conflicts: list[dict[str, Any]] = []
    supporting_evidence: list[Any] = []
    missing_evidence: list[Any] = []
    evidence: list[dict[str, Any]] = []
    rag_sources: list[dict[str, Any]] = []
    processing_ms: int

class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)

class ChatResponse(BaseModel):
    claim_id: str
    answer: str
    citations: list[str] = []
