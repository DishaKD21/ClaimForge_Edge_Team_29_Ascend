import os
import shutil
import tempfile
import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

from app.main import app
from app.rag.chunker import TextChunker
from app.rag.vector_store import VectorStore
from app.rag.firebase_loader import FirebaseDocumentLoader
from app.rag.rag_engine import RAGEngine

client = TestClient(app)


@pytest.fixture
def sample_document():
    return {
        "document_id": "doc_CLM123_desc",
        "claim_id": "CLM123",
        "evidence_id": "EVD1",
        "type": "claim_description",
        "timestamp": "2026-08-22T10:00:00Z",
        "title": "Claim Details: Rahul Sharma",
        "author": "Rahul Sharma",
        "content": "Vehicle collision at main street intersection. Front bumper heavily damaged. Witness confirms minor injury to passenger."
    }


@pytest.fixture
def temp_vector_dir():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_chunker_metadata_preservation(sample_document):
    chunker = TextChunker(chunk_size=50, chunk_overlap=10)
    chunks = chunker.chunk_document(sample_document)

    assert len(chunks) > 0
    for idx, chunk in enumerate(chunks):
        assert "chunk_id" in chunk
        assert "text" in chunk
        meta = chunk["metadata"]
        assert meta["document_id"] == "doc_CLM123_desc"
        assert meta["claim_id"] == "CLM123"
        assert meta["evidence_id"] == "EVD1"
        assert meta["source_type"] == "claim_description"
        assert meta["timestamp"] == "2026-08-22T10:00:00Z"
        assert meta["title"] == "Claim Details: Rahul Sharma"
        assert meta["chunk_index"] == idx


def test_vector_store_add_and_search(sample_document, temp_vector_dir):
    chunker = TextChunker(chunk_size=100, chunk_overlap=10)
    chunks = chunker.chunk_document(sample_document)

    vector_store = VectorStore(persist_directory=temp_vector_dir)
    added_count = vector_store.add_chunks(chunks)

    assert added_count == len(chunks)

    results = vector_store.search("collision bumper", top_k=2)
    assert len(results) > 0
    top_result = results[0]
    assert "text" in top_result
    assert "similarity_score" in top_result
    assert top_result["metadata"]["claim_id"] == "CLM123"


def test_vector_store_claim_filtering(temp_vector_dir):
    docs = [
        {
            "document_id": "doc-a",
            "claim_id": "CLM_A",
            "type": "text_evidence",
            "timestamp": "2026-08-22T00:00:00Z",
            "title": "Evidence A",
            "content": "Engine fire reported after front end collision."
        },
        {
            "document_id": "doc-b",
            "claim_id": "CLM_B",
            "type": "text_evidence",
            "timestamp": "2026-08-22T00:00:00Z",
            "title": "Evidence B",
            "content": "Water damage in basement due to broken pipe."
        }
    ]

    chunker = TextChunker(chunk_size=200, chunk_overlap=20)
    chunks = chunker.chunk_documents(docs)

    vector_store = VectorStore(persist_directory=temp_vector_dir)
    vector_store.add_chunks(chunks)

    # Search with claim_id filter
    results_a = vector_store.search("fire collision", top_k=5, claim_id="CLM_A")
    assert len(results_a) > 0
    assert all(r["metadata"]["claim_id"] == "CLM_A" for r in results_a)
    assert not any(r["metadata"]["claim_id"] == "CLM_B" for r in results_a)


def test_cross_claim_isolation(temp_vector_dir):
    docs = [
        {
            "document_id": "doc-a",
            "claim_id": "CLM_A",
            "type": "text_evidence",
            "timestamp": "2026-08-22T00:00:00Z",
            "title": "Evidence A",
            "content": "Secret claim details for claim A."
        },
        {
            "document_id": "doc-b",
            "claim_id": "CLM_B",
            "type": "text_evidence",
            "timestamp": "2026-08-22T00:00:00Z",
            "title": "Evidence B",
            "content": "Secret claim details for claim B."
        }
    ]

    chunker = TextChunker(chunk_size=200, chunk_overlap=20)
    chunks = chunker.chunk_documents(docs)

    vector_store = VectorStore(persist_directory=temp_vector_dir)
    vector_store.add_chunks(chunks)

    # Scoped query for CLM_A must never return CLM_B chunks
    results_a = vector_store.search("Secret claim details", top_k=5, claim_id="CLM_A")
    assert len(results_a) == 1
    assert results_a[0]["metadata"]["claim_id"] == "CLM_A"

    # Scoped query for CLM_B must never return CLM_A chunks
    results_b = vector_store.search("Secret claim details", top_k=5, claim_id="CLM_B")
    assert len(results_b) == 1
    assert results_b[0]["metadata"]["claim_id"] == "CLM_B"


def test_rag_engine_lifecycle(temp_vector_dir):
    vector_store = VectorStore(persist_directory=temp_vector_dir)

    # Mock document loader to return sample docs
    mock_loader = Mock()
    mock_loader.load_documents.return_value = [
        {
            "document_id": "doc-1",
            "claim_id": "CLM_TEST",
            "evidence_id": "",
            "type": "claim_description",
            "timestamp": "2026-08-22",
            "title": "Test Claim",
            "author": "Test Customer",
            "content": "Test vehicle rear end crash on highway."
        }
    ]

    rag_engine = RAGEngine(vector_store=vector_store, loader=mock_loader)

    # Sync
    sync_res = rag_engine.sync_documents(claim_id="CLM_TEST")
    assert sync_res["documents_processed"] == 1
    assert sync_res["chunks_indexed"] > 0

    # Query
    query_res = rag_engine.query(query="rear end crash", claim_id="CLM_TEST")
    assert query_res["claim_id"] == "CLM_TEST"
    assert "answer" in query_res
    assert len(query_res["retrieved_chunks"]) > 0


@patch("app.routes.rag.rag_engine")
def test_rag_api_sync_endpoint(mock_engine):
    mock_engine.sync_documents.return_value = {
        "message": "Successfully synced and indexed documents for claim CLM123",
        "documents_processed": 2,
        "chunks_indexed": 4
    }

    response = client.post("/api/v1/claims/CLM123/rag/sync")
    assert response.status_code == 200
    assert response.json()["documents_processed"] == 2
    assert response.json()["chunks_indexed"] == 4


@patch("app.routes.rag.rag_engine")
def test_rag_api_search_endpoint(mock_engine):
    mock_engine.search.return_value = [
        {
            "chunk_id": "c1",
            "text": "Bumper collision details",
            "metadata": {"claim_id": "CLM123", "source_type": "text"},
            "similarity_score": 0.85
        }
    ]

    response = client.post(
        "/api/v1/claims/CLM123/rag/search",
        json={"query": "bumper collision"}
    )
    assert response.status_code == 200
    assert response.json()["claim_id"] == "CLM123"
    assert len(response.json()["results"]) == 1
    assert response.json()["results"][0]["chunk_id"] == "c1"


@patch("app.routes.rag.rag_engine")
def test_rag_api_query_endpoint(mock_engine):
    mock_engine.query.return_value = {
        "query": "What caused the damage?",
        "claim_id": "CLM123",
        "answer": "The front bumper was damaged in a collision.",
        "retrieved_chunks": [
            {
                "chunk_id": "c1",
                "text": "Bumper collision details",
                "metadata": {"claim_id": "CLM123"},
                "similarity_score": 0.85
            }
        ]
    }

    response = client.post(
        "/api/v1/claims/CLM123/rag/query",
        json={"query": "What caused the damage?"}
    )
    assert response.status_code == 200
    assert response.json()["answer"] == "The front bumper was damaged in a collision."
