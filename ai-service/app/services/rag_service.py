class RAGIntegrationUnavailable(RuntimeError):
    pass


class RAGService:
    def analyze_claim(self, claim: dict, evidence: list[dict], image_bytes: bytes | None = None, text: str | None = None):
        raise RAGIntegrationUnavailable(
            "RAG integration is not configured. Add the RAG provider implementation before analyzing claims."
        )


rag_service = RAGService()