from pathlib import Path
import uuid
from fastapi import APIRouter, File, Form, UploadFile, HTTPException

from app.llm import ask_llm
from app.rag import store_claim
from app.video import summarize_video

router = APIRouter(tags=["Claims"])
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

async def save_upload(upload: UploadFile | None, claim_id: str):
    if not upload:
        return None

    allowed = {".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov", ".avi", ".mkv"}
    suffix = Path(upload.filename or "").suffix.lower()

    if suffix not in allowed:
        raise HTTPException(400, f"Unsupported file type: {suffix}")

    path = UPLOAD_DIR / f"{claim_id}_{uuid.uuid4().hex}{suffix}"
    path.write_bytes(await upload.read())
    return path

@router.post("/claims/verify")
async def verify_claim(
    text: str = Form(...),
    image: UploadFile | None = File(None),
    video: UploadFile | None = File(None)
):
    if not text.strip() and not image and not video:
        raise HTTPException(400, "Send at least one evidence item.")

    claim_id = str(uuid.uuid4())

    image_path = await save_upload(image, claim_id)
    video_path = await save_upload(video, claim_id)

    video_summary = summarize_video(video_path) if video_path else "No video supplied."

    prompt = f'''
You are ClaimForge Edge, an insurance claim verification assistant.

Analyze the supplied claim evidence and return ONLY valid JSON:

{{
  "verdict": "valid | requires_follow_up | fraudulent",
  "confidence": 0.0,
  "summary": "short summary",
  "conflicts": ["conflict 1"],
  "supporting_evidence": ["evidence 1"],
  "missing_evidence": ["missing item"],
  "reason": "one clear reason"
}}

Rules:
- Do not invent facts.
- If evidence is incomplete or contradictory, prefer requires_follow_up.
- confidence must be between 0 and 1.
- Keep the explanation concise and under 100 words.

Claim text:
{text}

Video information:
{video_summary}
'''

    verdict = ask_llm(prompt, image_path)

    evidence = {
        "text": text,
        "image_filename": image.filename if image else None,
        "video_filename": video.filename if video else None,
        "video_summary": video_summary
    }

    stored = store_claim(text, evidence, verdict)

    return {
        "claim_id": claim_id,
        "verdict": verdict,
        "rag_record_id": stored["id"],
        "rag_stored": True
    }
