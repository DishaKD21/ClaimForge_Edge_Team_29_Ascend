from datetime import date, datetime

from fastapi import HTTPException

from app.firebase.firestore_service import firestore_service


class ClaimService:
    @staticmethod
    def create_claim(payload: dict):
        try:
            return firestore_service.create_claim(payload)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Firestore write failure: {exc}") from exc

    @staticmethod
    def get_claim(claim_id: str):
        if not claim_id or len(claim_id) < 3:
            raise HTTPException(status_code=400, detail="Invalid claim ID")

        claim = firestore_service.get_claim(claim_id)
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")
        return claim


claim_service = ClaimService()
