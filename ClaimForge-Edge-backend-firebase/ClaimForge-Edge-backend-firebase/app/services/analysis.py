import os
import time
from datetime import datetime, timezone
from dateutil import parser as date_parser
from pathlib import Path
import json
from app.core.config import settings
from app.rag.retriever import LocalRAG
from app.services.firebase_service import save_claim, upload_file
from app.services.hf_client import HFClient
from app.utils.media import image_to_data_url, sample_video_frames, sha256_file

class ClaimAnalyzer:
    def __init__(self):
        self.hf = HFClient()
        self.rag = LocalRAG(str(Path(__file__).parents[2] / "data" / "knowledge_base.json"))

    def _file_timestamp(self, path):
        try:
            return datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc).isoformat()
        except Exception:
            return None

    def _inspect(self, evidence):
        seen = {}
        result = []
        for e in evidence:
            digest = sha256_file(e["path"])
            duplicate = seen.get(digest)
            if not duplicate: seen[digest] = e["id"]
            result.append({**{k:e[k] for k in ["id","filename","media_type","size_bytes"]},
                           "sha256":digest, "timestamp":self._file_timestamp(e["path"]),
                           "duplicate_of":duplicate, "observation":"", "storage_url":None})
        return result

    def _observations(self, evidence):
        out=[]
        for e in evidence:
            mt=e["media_type"]; suffix=Path(e["path"]).suffix.lower()
            try:
                if mt.startswith("image/"):
                    text=self.hf.vision("Inspect this insurance claim image. Report only visible facts about damage, scene context, objects, people, documents, and visible date/time. Do not infer hidden facts.",[image_to_data_url(e["path"])])
                elif mt.startswith("video/") or suffix in {".mp4",".mov",".avi",".mkv"}:
                    frames=sample_video_frames(e["path"], str(Path(e["path"]).parent / f"frames_{e['id']}"), 3)
                    text=self.hf.vision("Inspect sampled frames from an insurance claim video. Summarize only visible facts and note inconsistencies between frames.",[image_to_data_url(p) for p in frames]) if frames else "Video frames could not be extracted; manual verification is required."
                elif suffix==".txt":
                    text=Path(e["path"]).read_text(encoding="utf-8",errors="ignore")[:8000]
                else: text="Unsupported evidence content for automatic semantic inspection."
            except Exception as exc:
                text=f"Automatic evidence inspection unavailable: {exc}"
            out.append((e["id"], text[:3000]))
        return out

    def analyze(self, claim_id, incident_description, witnesses, incident_timestamp, evidence):
        started=time.perf_counter()
        summaries=self._inspect(evidence)
        obs=dict(self._observations(evidence))
        conflicts=[]
        for s in summaries:
            s["observation"]=obs.get(s["id"],"")
            if s["duplicate_of"]:
                conflicts.append({"type":"duplicate_evidence","severity":"medium","description":f"{s['filename']} is identical to another uploaded file.","evidence_refs":[s["id"],s["duplicate_of"]]})
            if s["timestamp"] and incident_timestamp:
                try:
                    if abs((date_parser.isoparse(s["timestamp"])-date_parser.isoparse(incident_timestamp)).total_seconds()) > 86400:
                        conflicts.append({"type":"timestamp_mismatch","severity":"high","description":f"{s['filename']} has a file timestamp more than 24 hours from the reported incident time.","evidence_refs":[s["id"]]})
                except Exception: pass

        all_text=f"INCIDENT: {incident_description}\nINCIDENT_TIMESTAMP: {incident_timestamp or 'not provided'}\nWITNESSES:\n"+"\n".join(witnesses or [])+"\nEVIDENCE:\n"+"\n".join(f"{s['id']} ({s['filename']}): {s['observation']}" for s in summaries)
        rag=self.rag.retrieve(all_text,4)
        rag_text="\n".join(f"[{x['id']}] {x['title']}: {x['rule']}" for x in rag)
        prompt=f'''You are ClaimForge Edge, an insurance claim evidence reconciliation engine.
Return ONLY JSON with verdict (valid|requires_follow_up|fraudulent), confidence (0..1), explanation (under 100 words), conflicts, supporting_evidence, missing_evidence.
Never invent facts. Use requires_follow_up for material contradictions or incomplete evidence. Use fraudulent only when multiple strong indicators support deliberate deception; suspicion alone is insufficient.
RAG RULES:\n{rag_text}\nDETERMINISTIC FLAGS:\n{json.dumps(conflicts)}\nCLAIM:\n{all_text}'''
        result=None; ai_error=None
        try:
            result=self.hf.parse_json(self.hf.chat([{"role":"system","content":"Return strict JSON only."},{"role":"user","content":prompt}],max_tokens=900,temperature=0.05))
        except Exception as exc: ai_error=str(exc)
        if not isinstance(result,dict):
            result={"verdict":"requires_follow_up","confidence":0.45,"explanation":"Automated reconciliation could not complete reliably. Manual verification is required.","conflicts":[],"supporting_evidence":[],"missing_evidence":["Successful AI reconciliation"]}
            if ai_error: result["conflicts"].append({"type":"ai_service_error","severity":"medium","description":ai_error[:500],"evidence_refs":[]})
        result["conflicts"]=conflicts+result.get("conflicts",[])
        result["confidence"]=max(0,min(1,float(result.get("confidence",.5))))
        result["verdict"]=result.get("verdict") if result.get("verdict") in {"valid","requires_follow_up","fraudulent"} else "requires_follow_up"
        if conflicts and result["verdict"]=="valid": result["verdict"]="requires_follow_up"; result["confidence"]=min(result["confidence"],.82)
        result["explanation"]=" ".join(str(result.get("explanation","")).split())[:700] or "Additional verification is required."

        # Store evidence in Firebase Storage after analysis has succeeded enough to create a claim record.
        for s,e in zip(summaries,evidence):
            try:
                s["storage_url"]=upload_file(e["path"],f"claims/{claim_id}/evidence/{s['id']}_{e['filename']}",s["media_type"])
            except Exception as exc:
                s["storage_error"]=str(exc)[:300]
        record={"claim_id":claim_id,"incident_description":incident_description,"incident_timestamp":incident_timestamp,"witness_statements":witnesses or [],"evidence":summaries,**result,"rag_sources":rag,"processing_ms":int((time.perf_counter()-started)*1000),"created_at":datetime.now(timezone.utc).isoformat()}
        save_claim(record)
        return record
