from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.schemas.claim import ClaimCreate, ClaimResponse, ClaimWithEvidenceCreate
from app.services.rag_service import RAGIntegrationUnavailable, rag_service

router = APIRouter(prefix="/api/v1/claims", tags=["claims"])


@router.post("", response_model=ClaimResponse)
def create_claim(payload: ClaimCreate):
    from app.main import firestore_service

    try:
        result = firestore_service.create_claim(payload.model_dump())
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Firestore write failure: {exc}") from exc


@router.post("/with-evidence")
def create_claim_with_evidence(payload: ClaimWithEvidenceCreate):
    from app.main import firestore_service

    try:
        claim_result = firestore_service.create_claim(payload.model_dump(exclude={"evidence"}))
        evidence = payload.evidence
        evidence_result = firestore_service.create_evidence(
            claim_result["claimId"],
            {"type": evidence.type, "content": evidence.content},
        )
        return {**claim_result, "evidence": evidence_result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Firestore write failure: {exc}") from exc


@router.get("/{claim_id}")
def get_claim(claim_id: str):
    from app.main import firestore_service

    claim = firestore_service.get_claim(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim


@router.post("/{claim_id}/analyze")
async def analyze_claim(
    claim_id: str,
    text: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
):
    from app.main import firestore_service

    claim = firestore_service.get_claim(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    image_bytes = await image.read() if image is not None else None
    evidence = firestore_service.list_evidence(claim_id)

    try:
        result = rag_service.analyze_claim(
            claim,
            evidence,
            image_bytes=image_bytes,
            image_mime_type=image.content_type if image is not None else None,
            text=text,
        )
        return firestore_service.create_analysis(claim_id, result)
    except RAGIntegrationUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failure: {exc}") from exc
