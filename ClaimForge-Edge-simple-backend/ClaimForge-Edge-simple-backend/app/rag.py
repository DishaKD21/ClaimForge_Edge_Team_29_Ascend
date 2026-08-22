import json
import math
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

STORE = Path("data/rag_store.json")

def load_store():
    if not STORE.exists():
        return []
    try:
        return json.loads(STORE.read_text(encoding="utf-8"))
    except Exception:
        return []

def save_store(items):
    STORE.parent.mkdir(parents=True, exist_ok=True)
    STORE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")

def tokens(text):
    return set(re.findall(r"[a-zA-Z0-9_]+", text.lower()))

def store_claim(claim_text, evidence, verdict):
    items = load_store()
    record = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "claim_text": claim_text,
        "evidence": evidence,
        "verdict": verdict
    }
    items.append(record)
    save_store(items)
    return record

def search(query, top_k=5):
    q = tokens(query)
    scored = []

    for item in load_store():
        text = " ".join([
            item.get("claim_text", ""),
            json.dumps(item.get("evidence", {}), ensure_ascii=False),
            json.dumps(item.get("verdict", {}), ensure_ascii=False)
        ])
        t = tokens(text)
        score = len(q & t) / max(1, math.sqrt(len(q) * len(t)))
        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:top_k]]
