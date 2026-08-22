from datetime import date

from pydantic import BaseModel, Field


class TextEvidenceCreate(BaseModel):
    type: str = Field(default="text", pattern="^text$")
    content: str = Field(..., min_length=1)


class ClaimCreate(BaseModel):
    customerName: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    incidentDate: date
    incidentTime: str = Field(..., pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    location: str = Field(..., min_length=1)


class ClaimResponse(BaseModel):
    claimId: str
    message: str


class ClaimWithEvidenceCreate(ClaimCreate):
    evidence: TextEvidenceCreate
