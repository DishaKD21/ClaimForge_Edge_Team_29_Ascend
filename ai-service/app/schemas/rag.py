from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class RAGSyncResponse(BaseModel):
    message: str
    documents_processed: int
    chunks_indexed: int


class RAGSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: Optional[int] = Field(default=None, ge=1, le=50)
    source_type: Optional[str] = None


class RAGChunkMetadata(BaseModel):
    document_id: Optional[str] = None
    claim_id: Optional[str] = None
    evidence_id: Optional[str] = None
    source_type: Optional[str] = None
    timestamp: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    chunk_index: Optional[int] = None
    char_offset: Optional[int] = None


class RAGChunkResult(BaseModel):
    chunk_id: str
    text: str
    metadata: Dict[str, Any]
    similarity_score: float


class RAGSearchResponse(BaseModel):
    query: str
    claim_id: Optional[str] = None
    results: List[RAGChunkResult]


class RAGQueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: Optional[int] = Field(default=None, ge=1, le=50)
    source_type: Optional[str] = None


class RAGQueryResponse(BaseModel):
    query: str
    claim_id: Optional[str] = None
    answer: str
    retrieved_chunks: List[RAGChunkResult]
