from typing import Optional

from pydantic import BaseModel, Field


class EvidenceCreateForm(BaseModel):
    type: str = Field(..., pattern=r"^(image|video|text)$")
    content: Optional[str] = None


class EvidenceResponse(BaseModel):
    id: Optional[str] = None
    claimId: Optional[str] = None
    type: Optional[str] = None
    fileName: Optional[str] = None
    storagePath: Optional[str] = None
    mimeType: Optional[str] = None
    content: Optional[str] = None
    uploadedAt: Optional[str] = None
