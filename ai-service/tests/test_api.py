from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.main import app


client = TestClient(app)


@patch("app.main.firestore_service")
@patch("app.main.storage_service")
def test_create_claim_returns_created_claim(mock_storage, mock_firestore):
    mock_firestore.create_claim.return_value = {
        "claimId": "CLM123",
        "message": "Claim created successfully",
    }

    response = client.post(
        "/api/v1/claims",
        json={
            "customerName": "Rahul Sharma",
            "description": "Car accident on highway",
            "incidentDate": "2026-08-22",
            "incidentTime": "20:00",
            "location": "Rajkot",
        },
    )

    assert response.status_code == 200
    assert response.json()["claimId"] == "CLM123"
    assert response.json()["message"] == "Claim created successfully"


@patch("app.main.firestore_service")
@patch("app.main.storage_service")
def test_create_claim_with_text_evidence_in_one_payload(mock_storage, mock_firestore):
    mock_firestore.create_claim.return_value = {
        "claimId": "CLM123",
        "message": "Claim created successfully",
    }
    mock_firestore.create_evidence.return_value = {
        "id": "EVD123",
        "claimId": "CLM123",
        "type": "text",
        "content": "Witness statement",
    }

    response = client.post(
        "/api/v1/claims/with-evidence",
        json={
            "customerName": "Rahul Sharma",
            "description": "Car accident on highway",
            "incidentDate": "2026-08-22",
            "incidentTime": "20:00",
            "location": "Rajkot",
            "evidence": {
                "type": "text",
                "content": "Witness statement",
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["claimId"] == "CLM123"
    assert response.json()["evidence"]["id"] == "EVD123"
    mock_firestore.create_evidence.assert_called_once_with(
        "CLM123",
        {"type": "text", "content": "Witness statement"},
    )


@patch("app.main.firestore_service")
@patch("app.main.storage_service")
def test_upload_text_evidence_works(mock_storage, mock_firestore):
    mock_firestore.get_claim.return_value = {"id": "CLM123", "customerName": "Rahul Sharma"}
    mock_firestore.create_evidence.return_value = {
        "id": "EVD123",
        "claimId": "CLM123",
        "type": "text",
        "content": "Witness statement",
    }

    response = client.post(
        "/api/v1/claims/CLM123/evidence",
        data={"type": "text", "content": "Witness statement"},
    )

    assert response.status_code == 200
    assert response.json()["type"] == "text"
    assert response.json()["content"] == "Witness statement"


@patch("app.main.firestore_service")
@patch("app.main.storage_service")
def test_health_endpoint_returns_connected_status(mock_storage, mock_firestore):
    mock_firestore.health_check.return_value = {"status": "ok", "firebase": "connected"}

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["firebase"] == "connected"
