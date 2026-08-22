from fastapi import APIRouter
from pydantic import BaseModel

from app.rag import search
from app.llm import ask_llm

router = APIRouter(tags=["Questions"])

class Question(BaseModel):
    question: str
    claim_id: str | None = None

@router.post("/questions")
def ask_question(payload: Question):
    matches = search(payload.question, top_k=5)

    if not matches:
        return {
            "answer": "I could not find relevant evidence in the RAG store.",
            "sources": []
        }

    context = "\n\n".join(
        f"Claim ID: {m['id']}\n"
        f"Claim: {m['claim_text']}\n"
        f"Evidence: {m['evidence']}\n"
        f"Verdict: {m['verdict']}"
        for m in matches
    )

    prompt = f'''
Answer the frontend user's question using ONLY the retrieved ClaimForge evidence.

Question:
{payload.question}

Retrieved evidence:
{context}

Return ONLY valid JSON:
{{
  "answer": "direct answer under 100 words",
  "reason": "brief evidence-based reason",
  "confidence": 0.0
}}

Do not invent information.
'''

    result = ask_llm(prompt)

    return {
        "answer": result.get("answer", result.get("summary", "")),
        "reason": result.get("reason", ""),
        "confidence": result.get("confidence", 0),
        "sources": [m["id"] for m in matches]
    }
