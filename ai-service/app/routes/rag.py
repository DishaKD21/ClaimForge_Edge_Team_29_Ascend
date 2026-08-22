from fastapi import APIRouter, HTTPException

from app.rag.rag_engine import RAGEngine
from app.schemas.rag import (
    RAGSyncResponse,
    RAGSearchRequest,
    RAGSearchResponse,
    RAGQueryRequest,
    RAGQueryResponse,
)

router = APIRouter(prefix="/api/v1/claims", tags=["rag"])

rag_engine = RAGEngine()


@router.post("/{claim_id}/rag/sync", response_model=RAGSyncResponse)
def sync_claim_documents(claim_id: str):
    if not claim_id or not claim_id.strip():
        raise HTTPException(status_code=400, detail="claim_id is required")
    try:
        res = rag_engine.sync_documents(claim_id=claim_id.strip())
        return res
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"RAG sync failed: {exc}") from exc


@router.post("/{claim_id}/rag/search", response_model=RAGSearchResponse)
def search_claim_chunks(claim_id: str, payload: RAGSearchRequest):
    if not claim_id or not claim_id.strip():
        raise HTTPException(status_code=400, detail="claim_id is required")
    try:
        chunks = rag_engine.search(
            query=payload.query,
            claim_id=claim_id.strip(),
            top_k=payload.top_k,
            source_type=payload.source_type
        )
        return {
            "query": payload.query,
            "claim_id": claim_id.strip(),
            "results": chunks
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"RAG search failed: {exc}") from exc


@router.post("/{claim_id}/rag/query", response_model=RAGQueryResponse)
def query_claim_rag(claim_id: str, payload: RAGQueryRequest):
    if not claim_id or not claim_id.strip():
        raise HTTPException(status_code=400, detail="claim_id is required")
    try:
        result = rag_engine.query(
            query=payload.query,
            claim_id=claim_id.strip(),
            source_type=payload.source_type,
            top_k=payload.top_k
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {exc}") from exc
