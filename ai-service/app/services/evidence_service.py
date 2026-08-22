import os
from typing import Optional

from fastapi import HTTPException, UploadFile

from app.config import settings
from app.firebase.firestore_service import firestore_service


class EvidenceService:
    @staticmethod
    def validate_file(file: Optional[UploadFile], evidence_type: str):
        if not file:
            raise HTTPException(status_code=400, detail="Empty file")

        if file.filename is None or file.filename == "":
            raise HTTPException(status_code=400, detail="Empty file")

        ext = os.path.splitext(file.filename)[1].lower()
        if evidence_type == "image" and ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        if evidence_type == "text":
            return

        if file.content_type not in {"image/jpeg", "image/png"}:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)

        if file_size == 0:
            raise HTTPException(status_code=400, detail="Empty file")

        if file_size > settings.MAX_FILE_SIZE_BYTES:
            raise HTTPException(status_code=413, detail="File size exceeds the configured limit")

    @staticmethod
    def create_evidence(claim_id: str, evidence_type: str, file: Optional[UploadFile], content: Optional[str]):
        claim = firestore_service.get_claim(claim_id)
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")

        if evidence_type == "text":
            if not content or not content.strip():
                raise HTTPException(status_code=400, detail="Text evidence content cannot be empty")
            try:
                return firestore_service.create_evidence(
                    claim_id,
                    {
                        "type": "text",
                        "content": content,
                        "mimeType": "text/plain",
                    },
                )
            except Exception as exc:
                raise HTTPException(status_code=500, detail=f"Firestore write failure: {exc}") from exc

        EvidenceService.validate_file(file, evidence_type)

        try:
            result = firestore_service.create_evidence(
                claim_id,
                {
                    "type": evidence_type,
                    "fileName": file.filename,
                    "mimeType": file.content_type or "application/octet-stream",
                },
            )
            return result
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Firestore write failure: {exc}") from exc

    @staticmethod
    def list_evidence(claim_id: str):
        claim = firestore_service.get_claim(claim_id)
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")

        return firestore_service.list_evidence(claim_id)


evidence_service = EvidenceService()
