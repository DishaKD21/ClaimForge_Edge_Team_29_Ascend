import os
import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings
from app.rag.rag_engine import RAGEngine
from app.rag.vector_store import VectorStore
from app.rag.chunker import TextChunker

client = TestClient(app)


def test_gemini_api_key_missing_uses_fallback(tmp_path):
    """
    1. Verify that when API key is missing/empty, the system uses the deterministic fallback response.
    """
    vstore = VectorStore(persist_directory=str(tmp_path))
    vstore.add_chunks([
        {
            "chunk_id": "c1",
            "text": "Bumper damaged in collision.",
            "metadata": {"claim_id": "CLM_NO_KEY", "source_type": "text", "title": "Evidence Note"}
        }
    ])

    engine = RAGEngine(vector_store=vstore)

    with patch.object(settings, "LLM_API_KEY", ""):
        with patch.object(settings, "GEMINI_API_KEY", ""):
            res = engine.query(query="What was damaged?", claim_id="CLM_NO_KEY")
            assert "Synthesized RAG Response for Query" in res["answer"]
            assert "Bumper damaged in collision" in res["answer"]


def test_gemini_llm_client_initialization_and_response(tmp_path):
    """
    2. Verify that when GEMINI_API_KEY/LLM_API_KEY is configured:
       - The google.genai Client is initialized with the API key.
       - Retrieved chunks are sent as context in the prompt.
       - The actual LLM-generated answer is returned in the response.
    """
    vstore = VectorStore(persist_directory=str(tmp_path))
    vstore.add_chunks([
        {
            "chunk_id": "c1",
            "text": "Front bumper and hood crushed during highway crash.",
            "metadata": {"claim_id": "CLM_WITH_KEY", "source_type": "text", "title": "Witness Report"}
        }
    ])

    engine = RAGEngine(vector_store=vstore)

    from google import genai

    fake_api_key = "AIzaSyTEST_FAKE_GEMINI_KEY_12345"
    mock_genai_response = Mock()
    mock_genai_response.text = "Based on the witness report, the front bumper and hood were crushed in a highway crash."

    mock_client_instance = Mock()
    mock_client_instance.models.generate_content.return_value = mock_genai_response

    with patch.object(settings, "LLM_API_KEY", fake_api_key):
        with patch.object(settings, "GEMINI_API_KEY", fake_api_key):
            with patch.object(genai, "Client", return_value=mock_client_instance) as mock_client_cls:
                res = engine.query(query="Summarize vehicle damage", claim_id="CLM_WITH_KEY")

                # Verify Client was initialized with the API key
                mock_client_cls.assert_called_once_with(api_key=fake_api_key)

                # Verify generate_content was called with prompt containing retrieved chunks context
                mock_client_instance.models.generate_content.assert_called_once()
                call_kwargs = mock_client_instance.models.generate_content.call_args[1]
                assert call_kwargs["model"] == settings.LLM_MODEL
                assert "Front bumper and hood crushed" in call_kwargs["contents"]

                # Verify the real LLM response is returned in the API output
                assert res["answer"] == "Based on the witness report, the front bumper and hood were crushed in a highway crash."
                assert len(res["retrieved_chunks"]) == 1
                assert res["retrieved_chunks"][0]["chunk_id"] == "c1"


def test_api_endpoint_with_gemini_llm(tmp_path):
    """
    3. Verify that the FastAPI endpoint /api/v1/claims/{claim_id}/rag/query returns the real LLM answer when API key is set.
    """
    fake_api_key = "AIzaSyTEST_FAKE_GEMINI_KEY_12345"

    with patch("app.routes.rag.rag_engine.query") as mock_engine_query:
        mock_engine_query.return_value = {
            "query": "Is there structural damage?",
            "claim_id": "CLM999",
            "answer": "Yes, Gemini LLM analysis confirms structural frame damage on the left side.",
            "retrieved_chunks": [
                {
                    "chunk_id": "c1",
                    "text": "Left frame bent.",
                    "metadata": {"claim_id": "CLM999"},
                    "similarity_score": 0.92
                }
            ]
        }

        response = client.post(
            "/api/v1/claims/CLM999/rag/query",
            json={"query": "Is there structural damage?"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["claim_id"] == "CLM999"
        assert data["answer"] == "Yes, Gemini LLM analysis confirms structural frame damage on the left side."
        assert len(data["retrieved_chunks"]) == 1
