import logging
from typing import List, Dict, Any, Optional

from app.config import settings
from app.rag.firebase_loader import FirebaseDocumentLoader
from app.rag.chunker import TextChunker
from app.rag.vector_store import VectorStore

logger = logging.getLogger("RAGEngine")


class RAGEngine:
    """
    Coordinates Firebase document fetching, text chunking, vector indexing,
    similarity search, and RAG answer synthesis.
    """
    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        loader: Optional[FirebaseDocumentLoader] = None,
        chunker: Optional[TextChunker] = None
    ):
        self.loader = loader or FirebaseDocumentLoader()
        self.chunker = chunker or TextChunker(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        self.vector_store = vector_store or VectorStore(
            persist_directory=settings.CHROMA_DB_DIR,
            model_name=settings.EMBEDDING_MODEL_NAME
        )

    def sync_documents(self, claim_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetches stored documents from Firebase (or fallback), chunks them with metadata,
        and indexes them into the persistent vector database.
        """
        documents = self.loader.load_documents(claim_id=claim_id)
        if not documents:
            return {
                "message": "No documents found to sync",
                "documents_processed": 0,
                "chunks_indexed": 0
            }

        chunks = self.chunker.chunk_documents(documents)
        indexed_count = self.vector_store.add_chunks(chunks)

        return {
            "message": f"Successfully synced and indexed documents for {'all claims' if not claim_id else f'claim {claim_id}'}",
            "documents_processed": len(documents),
            "chunks_indexed": indexed_count
        }

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        claim_id: Optional[str] = None,
        source_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Performs vector similarity search over indexed chunks with optional metadata filtering.
        """
        k = top_k or settings.RAG_TOP_K
        return self.vector_store.search(
            query=query,
            top_k=k,
            claim_id=claim_id,
            source_type=source_type
        )

    def query(
        self,
        query: str,
        claim_id: Optional[str] = None,
        source_type: Optional[str] = None,
        top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Full RAG pipeline:
        1. Performs vector similarity retrieval.
        2. Generates an answer incorporating retrieved evidence chunks.
        """
        k = top_k or settings.RAG_TOP_K
        retrieved_chunks = self.search(
            query=query,
            top_k=k,
            claim_id=claim_id,
            source_type=source_type
        )

        answer = self._synthesize_answer(query, retrieved_chunks, claim_id)

        return {
            "query": query,
            "claim_id": claim_id,
            "answer": answer,
            "retrieved_chunks": retrieved_chunks
        }

    def _synthesize_answer(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        claim_id: Optional[str] = None
    ) -> str:
        """
        Generates a RAG answer using Gemini LLM if API key is configured,
        or a structured deterministic synthesis fallback.
        """
        context_str = "\n---\n".join([
            f"[Source: {c['metadata'].get('source_type', 'text')} | ClaimID: {c['metadata'].get('claim_id')} | Title: {c['metadata'].get('title')}]\n{c['text']}"
            for c in chunks
        ])

        if settings.LLM_API_KEY:
            prompt = f"""You are an AI assistant for claim analysis.
Query: {query}
Claim ID Filter: {claim_id or 'All Claims'}

Retrieved Relevant Evidence Chunks:
{context_str if context_str else 'No evidence chunks found'}

Please answer the query concisely based strictly on the provided claim evidence and context."""

            # 1. Try google-genai SDK (recommended)
            try:
                from google import genai
                client = genai.Client(api_key=settings.LLM_API_KEY)
                response = client.models.generate_content(
                    model=settings.LLM_MODEL,
                    contents=prompt,
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e1:
                logger.debug(f"google.genai SDK call failed/unavailable: {e1}. Trying fallback.")
                # 2. Try legacy google.generativeai SDK fallback
                try:
                    import google.generativeai as legacy_genai
                    legacy_genai.configure(api_key=settings.LLM_API_KEY)
                    model = legacy_genai.GenerativeModel(settings.LLM_MODEL)
                    response = model.generate_content(prompt)
                    if response and response.text:
                        return response.text.strip()
                except Exception as e2:
                    logger.warning(f"LLM API call failed: {e2}. Falling back to structured synthesis.")

        # Structured deterministic synthesis fallback
        if not chunks:
            return f"No relevant evidence chunks found matching query '{query}'."

        synthesis_lines = [
            f"Synthesized RAG Response for Query: '{query}'",
            f"Retrieved {len(chunks)} relevant evidence chunks from claim records."
        ]

        if claim_id:
            synthesis_lines.append(f"Target Claim ID: {claim_id}")

        synthesis_lines.append("\nTop Relevant Evidence Snippets:")
        for idx, chunk in enumerate(chunks[:3], 1):
            meta = chunk.get("metadata", {})
            synthesis_lines.append(
                f"{idx}. [{meta.get('title', 'Doc')} ({meta.get('source_type', 'evidence')})] \"{chunk['text'][:150]}...\" (Similarity: {chunk.get('similarity_score', 0.0)})"
            )

        return "\n".join(synthesis_lines)
