import os
import json
import logging
from typing import List, Dict, Any, Optional

from app.firebase.firestore_service import firestore_service
from app.firebase.storage_service import storage_service

logger = logging.getLogger("FirebaseDocumentLoader")


class FirebaseDocumentLoader:
    """
    Loader for claim and evidence text documents stored in Firebase (Firestore / Storage).
    Integrates directly with the existing firestore_service and storage_service.
    Does not modify any existing Firebase data or configuration.
    """
    def __init__(self, fallback_path: str = "data/sample_documents.json"):
        self.fallback_path = fallback_path

    def load_documents(self, claim_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetches claims and text evidence documents from Firestore (and Storage if text file).
        Returns a list of standardized document dictionaries ready for chunking.
        """
        documents = []

        try:
            if claim_id:
                docs = self._load_single_claim_documents(claim_id)
                if docs:
                    return docs
            else:
                docs = self._load_all_claims_documents()
                if docs:
                    return docs
        except Exception as e:
            logger.error(f"Error fetching documents from Firestore: {e}. Checking fallback mode.")

        # Fallback mode if no Firestore documents were loaded
        return self._load_fallback_documents(claim_id)

    def _load_single_claim_documents(self, claim_id: str) -> List[Dict[str, Any]]:
        docs = []
        claim = firestore_service.get_claim(claim_id)
        if claim:
            # 1. Claim summary document
            claim_desc = claim.get("description", "")
            if claim_desc:
                docs.append({
                    "document_id": f"claim_desc_{claim_id}",
                    "claim_id": claim_id,
                    "evidence_id": "",
                    "type": "claim_description",
                    "timestamp": claim.get("createdAt", claim.get("incidentDate", "")),
                    "title": f"Claim Details: {claim.get('customerName', 'Unknown')}",
                    "author": claim.get("customerName", "Customer"),
                    "content": f"Customer Name: {claim.get('customerName', '')}\nIncident Location: {claim.get('location', '')}\nIncident Date: {claim.get('incidentDate', '')}\nDescription: {claim_desc}"
                })

            # 2. Evidence documents for this claim
            evidences = firestore_service.list_evidence(claim_id)
            for ev in evidences:
                doc = self._extract_evidence_doc(claim_id, ev)
                if doc:
                    docs.append(doc)

        return docs

    def _load_all_claims_documents(self) -> List[Dict[str, Any]]:
        docs = []
        try:
            claim_collection = firestore_service.get_claim_collection()
            stream = claim_collection.stream()
            for doc_snapshot in stream:
                c_id = doc_snapshot.id
                claim_docs = self._load_single_claim_documents(c_id)
                docs.extend(claim_docs)
        except Exception as e:
            logger.error(f"Error streaming all claims: {e}")
        return docs

    def _extract_evidence_doc(self, claim_id: str, evidence: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        ev_id = evidence.get("id", "ev_unknown")
        ev_type = evidence.get("type", "")
        content = evidence.get("content", "")

        # If it's a text type evidence with direct content in Firestore
        if ev_type == "text" and content:
            return {
                "document_id": f"evidence_{ev_id}",
                "claim_id": claim_id,
                "evidence_id": ev_id,
                "type": "text_evidence",
                "timestamp": evidence.get("uploadedAt", ""),
                "title": evidence.get("fileName", "Text Evidence"),
                "author": "Witness/Adjuster",
                "content": content
            }

        # If it's a text file uploaded to Firebase Storage
        storage_path = evidence.get("storagePath", "")
        mime_type = evidence.get("mimeType", "")
        if storage_path and (mime_type == "text/plain" or storage_path.endswith(".txt")):
            try:
                bucket = storage_service._ensure_bucket()
                blob = bucket.blob(storage_path)
                if blob.exists():
                    text_data = blob.download_as_text()
                    if text_data:
                        return {
                            "document_id": f"evidence_storage_{ev_id}",
                            "claim_id": claim_id,
                            "evidence_id": ev_id,
                            "type": "text_file_evidence",
                            "timestamp": evidence.get("uploadedAt", ""),
                            "title": evidence.get("fileName", os.path.basename(storage_path)),
                            "author": "Storage Document",
                            "content": text_data
                        }
            except Exception as e:
                logger.warning(f"Could not download text file from storage path {storage_path}: {e}")

        return None

    def _load_fallback_documents(self, claim_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Loads documents from local fallback JSON fixture if available."""
        if not os.path.exists(self.fallback_path):
            return []

        try:
            with open(self.fallback_path, 'r', encoding='utf-8') as f:
                docs = json.load(f)

            results = [self._normalize_fallback_document(d) for d in docs]
            if claim_id:
                results = [d for d in results if d.get("claim_id") == claim_id]

            return results
        except Exception as e:
            logger.error(f"Error reading fallback file {self.fallback_path}: {e}")
            return []

    def _normalize_fallback_document(self, doc_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "document_id": str(doc_data.get("document_id", doc_data.get("id", ""))),
            "claim_id": str(doc_data.get("claim_id", doc_data.get("patient_id", ""))),
            "evidence_id": str(doc_data.get("evidence_id", "")),
            "type": str(doc_data.get("type", doc_data.get("source_type", "text"))),
            "timestamp": str(doc_data.get("timestamp", "")),
            "title": str(doc_data.get("title", "Document")),
            "author": str(doc_data.get("author", "Unknown")),
            "content": str(doc_data.get("content", ""))
        }
