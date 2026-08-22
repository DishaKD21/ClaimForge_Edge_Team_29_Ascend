from fastapi import APIRouter, HTTPException

from app.schemas.claim import ClaimCreate, ClaimResponse

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


@router.get("/{claim_id}")
def get_claim(claim_id: str):
    from app.main import firestore_service

    claim = firestore_service.get_claim(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim
