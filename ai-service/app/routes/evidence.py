from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

router = APIRouter(prefix="/api/v1/claims", tags=["evidence"])


@router.post("/{claim_id}/evidence")
def upload_evidence(
    claim_id: str,
    type: str = Form(...),
    content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    from app.main import firestore_service, storage_service

    normalized_type = type.lower()
    if normalized_type not in {"image", "video", "text"}:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    if normalized_type == "text" and file is not None:
        raise HTTPException(status_code=400, detail="Text evidence should not include a file")

    if normalized_type != "text" and content is not None:
        raise HTTPException(status_code=400, detail="Content is only supported for text evidence")

    if normalized_type == "text":
        if not content or not content.strip():
            raise HTTPException(status_code=400, detail="Text evidence content cannot be empty")
        try:
            return firestore_service.create_evidence(
                claim_id,
                {
                    "type": "text",
                    "content": content,
                    "fileName": "text_evidence.txt",
                    "storagePath": "",
                    "mimeType": "text/plain",
                },
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Firestore write failure: {exc}") from exc

    if file is None:
        raise HTTPException(status_code=400, detail="Empty file")
    if file.filename is None or file.filename == "":
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        storage_path = storage_service.upload_file(file.file, claim_id, file.filename)
    except ValueError as exc:
        message = str(exc)
        if message == "Empty file":
            raise HTTPException(status_code=400, detail="Empty file") from exc
        if message == "Unsupported file type":
            raise HTTPException(status_code=400, detail="Unsupported file type") from exc
        raise HTTPException(status_code=500, detail=f"Firebase Storage upload failure: {message}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Firebase Storage upload failure: {exc}") from exc

    try:
        return firestore_service.create_evidence(
            claim_id,
            {
                "type": normalized_type,
                "fileName": file.filename,
                "storagePath": storage_path,
                "mimeType": file.content_type or "application/octet-stream",
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Firestore write failure: {exc}") from exc


@router.get("/{claim_id}/evidence")
def list_evidence(claim_id: str):
    from app.main import firestore_service

    claim = firestore_service.get_claim(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return firestore_service.list_evidence(claim_id)
