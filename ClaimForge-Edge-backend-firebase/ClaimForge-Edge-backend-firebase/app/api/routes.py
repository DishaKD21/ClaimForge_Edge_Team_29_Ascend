import json
from pathlib import Path
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from app.core.config import settings
from app.schemas.models import ChatRequest, ChatResponse, VerdictResponse
from app.services.analysis import ClaimAnalyzer
from app.services.firebase_service import get_claim
from app.services.hf_client import HFClient
from app.rag.retriever import LocalRAG
from app.utils.files import ALLOWED_EXTENSIONS, guess_media_type, new_id, safe_filename

router=APIRouter(prefix="/api/v1")
analyzer=ClaimAnalyzer()

@router.get("/claims/{claim_id}")
def read_claim(claim_id:str):
    claim=get_claim(claim_id)
    if not claim: raise HTTPException(404,"Claim not found")
    return claim

@router.post("/claims/analyze", response_model=VerdictResponse)
async def analyze_claim(incident_description:str=Form(...), claim_id:str|None=Form(None), witness_statements:str|None=Form(None), incident_timestamp:str|None=Form(None), evidence:list[UploadFile]=File(default=[])):
    claim_id=claim_id or new_id("clm")
    try:
        witnesses=json.loads(witness_statements) if witness_statements else []
        if not isinstance(witnesses,list): raise ValueError
        witnesses=[str(x) for x in witnesses]
    except Exception: raise HTTPException(400,"witness_statements must be a JSON array of strings")
    total_limit=settings.max_upload_mb*1024*1024
    work=Path("./tmp")/claim_id; work.mkdir(parents=True,exist_ok=True)
    saved=[]
    for upload in evidence:
        filename=safe_filename(upload.filename or "evidence")
        ext=Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS: raise HTTPException(400,f"Unsupported file type: {ext}")
        dest=work/f"{new_id('ev')}_{filename}"; size=0
        with dest.open("wb") as out:
            while chunk:=await upload.read(1024*1024):
                size+=len(chunk)
                if size>total_limit: dest.unlink(missing_ok=True); raise HTTPException(413,f"File exceeds {settings.max_upload_mb} MB")
                out.write(chunk)
        saved.append({"id":new_id("evi"),"filename":filename,"path":str(dest),"media_type":guess_media_type(filename,upload.content_type),"size_bytes":size})
    try: return analyzer.analyze(claim_id,incident_description,witnesses,incident_timestamp,saved)
    except Exception as exc: raise HTTPException(500,f"Claim analysis failed: {exc}")

@router.post("/claims/{claim_id}/chat", response_model=ChatResponse)
def claim_chat(claim_id:str, request:ChatRequest):
    claim=get_claim(claim_id)
    if not claim: raise HTTPException(404,"Claim not found")
    rag=LocalRAG(str(Path(__file__).parents[2]/"data"/"knowledge_base.json"))
    sources=rag.retrieve(request.question+"\n"+json.dumps(claim),4)
    rules="\n".join(f"[{s['id']}] {s['title']}: {s['rule']}" for s in sources)
    prompt=f"Answer only from this claim and rules. Be concise and do not invent facts.\nCLAIM:\n{json.dumps(claim)}\nRULES:\n{rules}\nQUESTION: {request.question}"
    try: answer=HFClient().chat([{"role":"system","content":"You are a careful insurance claims assistant."},{"role":"user","content":prompt}],max_tokens=450,temperature=.1)
    except Exception as exc: raise HTTPException(502,f"AI chat failed: {exc}")
    return {"claim_id":claim_id,"answer":answer.strip(),"citations":[s["id"] for s in sources]}
