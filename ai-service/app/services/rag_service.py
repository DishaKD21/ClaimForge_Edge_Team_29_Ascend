from app.rag.rag_engine import RAGEngine
from app.config import settings

class RAGIntegrationUnavailable(RuntimeError):
    pass

class RAGService:
    def __init__(self):
        self.engine = RAGEngine()

    def analyze_claim(
        self,
        claim: dict,
        evidence: list[dict],
        image_bytes: bytes | None = None,
        image_mime_type: str | None = None,
        text: str | None = None,
    ) -> dict:
        claim_id = str(claim["claimId"])
        query = (text or "").strip() or (
            f"Analyze the claim and determine whether the evidence supports it: "
            f"{claim.get('description', '')}"
        ).strip()

        try:
            self.engine.sync_documents(claim_id=claim_id)
            result = self.engine.query(query=query, claim_id=claim_id)

            if image_bytes:
                result["image_analysis"] = self._analyze_image(
                    claim=claim,
                    evidence=evidence,
                    image_bytes=image_bytes,
                    image_mime_type=image_mime_type or "image/jpeg",
                    retrieved_context=result.get("answer", ""),
                )

            return result
        except Exception as exc:
            raise RAGIntegrationUnavailable(f"RAG analysis failed: {exc}") from exc

    @staticmethod
    def _analyze_image(
        claim: dict,
        evidence: list[dict],
        image_bytes: bytes,
        image_mime_type: str,
        retrieved_context: str,
    ) -> str:
        if not settings.LLM_API_KEY:
            raise RAGIntegrationUnavailable(
                "Image analysis requires LLM_API_KEY. Add the Gemini API key to ai-service/.env."
            )

        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise RAGIntegrationUnavailable(
                "Image analysis requires the google-genai package. Install backend requirements."
            ) from exc

        evidence_summary = "\n".join(
            f"- {item.get('type', 'unknown')}: {item.get('content', item.get('fileName', ''))}"
            for item in evidence
        )
        prompt = f"""Analyze this insurance claim image together with the claim context.
Claim: {claim.get('description', '')}
Location: {claim.get('location', '')}
Date: {claim.get('incidentDate', '')}
Saved evidence:
{evidence_summary or 'None'}
Retrieved RAG context:
{retrieved_context or 'None'}

Describe only visible, relevant facts. Identify visible damage, objects, scene details,
and any inconsistencies with the claim. Do not invent details. Mention uncertainty."""

        client = genai.Client(api_key=settings.LLM_API_KEY)
        response = client.models.generate_content(
            model=settings.LLM_MODEL,
            contents=[
                prompt,
                types.Part.from_bytes(data=image_bytes, mime_type=image_mime_type),
            ],
        )
        if not response or not response.text:
            raise RAGIntegrationUnavailable("The image analysis provider returned no result.")
        return response.text.strip()


rag_service = RAGService()