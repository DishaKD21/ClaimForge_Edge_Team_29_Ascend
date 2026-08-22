from datetime import datetime, timezone

from google.cloud.firestore_v1 import DocumentReference

from app.firebase.firebase_config import get_firestore_client


class FirestoreService:
    def __init__(self):
        self.db = None

    def _ensure_db(self):
        if self.db is None:
            self.db = get_firestore_client()
        return self.db

    def get_claim_collection(self):
        return self._ensure_db().collection("claims")

    def get_evidence_collection(self):
        return self.db.collection("evidence")

    def get_analyses_collection(self):
        return self.db.collection("analyses")

    def create_claim(self, claim_data: dict) -> dict:
        claim_ref = self.get_claim_collection().document()
        claim_id = claim_ref.id
        incident_date = claim_data["incidentDate"]
        incident_time = claim_data["incidentTime"]

        parsed_time = datetime.strptime(incident_time, "%H:%M").time()
        incident_datetime = datetime.combine(incident_date, parsed_time)

        payload = {
            "customerName": claim_data["customerName"],
            "description": claim_data["description"],
            "incidentDate": incident_datetime,
            "incidentTime": incident_time,
            "location": claim_data["location"],
            "status": "submitted",
            "createdAt": datetime.now(timezone.utc),
        }

        claim_ref.set(payload)
        return {"claimId": claim_id, "message": "Claim created successfully"}

    def get_claim(self, claim_id: str):
        claim_ref = self.get_claim_collection().document(claim_id)
        doc = claim_ref.get()
        if not doc.exists:
            return None
        return self._serialize_claim(doc)

    def create_evidence(self, claim_id: str, evidence_data: dict) -> dict:
        claim_ref = self.get_claim_collection().document(claim_id)
        evidence_ref = self.get_evidence_collection().document()
        payload = {
            "claimId": claim_ref,
            "type": evidence_data["type"],
            "mimeType": evidence_data.get("mimeType", ""),
            "uploadedAt": datetime.now(timezone.utc),
        }

        if evidence_data.get("fileName"):
            payload["fileName"] = evidence_data["fileName"]

        if evidence_data.get("content") is not None:
            payload["content"] = evidence_data["content"]

        evidence_ref.set(payload)
        return self._serialize_evidence(evidence_ref.get())

    def list_evidence(self, claim_id: str):
        claim_ref = self.get_claim_collection().document(claim_id)
        docs = self.get_evidence_collection().where("claimId", "==", claim_ref).stream()
        return [self._serialize_evidence(doc) for doc in docs]

    def create_analysis(self, claim_id: str, analysis_data: dict) -> dict:
        claim_ref = self.get_claim_collection().document(claim_id)
        analysis_ref = self.get_analyses_collection().document()
        payload = {
            "claimId": claim_ref,
            "result": analysis_data,
            "createdAt": datetime.now(timezone.utc),
        }
        analysis_ref.set(payload)
        return self._serialize_analysis(analysis_ref.get())

    @staticmethod
    def _serialize_claim(doc):
        data = doc.to_dict() or {}
        data["claimId"] = doc.id
        for key in ["incidentDate", "createdAt"]:
            value = data.get(key)
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data

    @staticmethod
    def _serialize_evidence(doc):
        data = doc.to_dict() or {}
        data["id"] = doc.id
        claim_ref = data.get("claimId")
        if isinstance(claim_ref, DocumentReference):
            data["claimId"] = claim_ref.id
        for key in ["uploadedAt"]:
            value = data.get(key)
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data

    @staticmethod
    def _serialize_analysis(doc):
        data = doc.to_dict() or {}
        data["id"] = doc.id
        claim_ref = data.get("claimId")
        if isinstance(claim_ref, DocumentReference):
            data["claimId"] = claim_ref.id
        created_at = data.get("createdAt")
        if isinstance(created_at, datetime):
            data["createdAt"] = created_at.isoformat()
        return data


firestore_service = FirestoreService()
