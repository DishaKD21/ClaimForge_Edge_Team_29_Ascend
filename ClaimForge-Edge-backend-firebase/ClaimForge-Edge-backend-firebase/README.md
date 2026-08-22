# ClaimForge Edge — Simple Firebase Backend

Backend only. No Docker, no local database, and no Firebase client SDK is required in this backend.

## What it provides
- FastAPI REST API
- Firebase Firestore for claim records
- Firebase Storage for photos/videos/text evidence
- Hugging Face Inference Providers for LLM + vision analysis
- Local lightweight RAG knowledge base
- Duplicate evidence detection using SHA-256
- Timestamp mismatch detection
- Conflict reconciliation
- Confidence score and explanation
- Claim-specific AI chatbot

## 1. Install

```bash
python -m venv .venv
```

Windows PowerShell:
```powershell
.venv\Scripts\Activate.ps1
```

Then:
```bash
pip install -r requirements.txt
```

## 2. Configure Firebase

Your teammate must provide a **Firebase Admin service account** for the Firebase project. This is different from the normal React Native Firebase client configuration.

Place the downloaded service-account JSON beside this README as:
`firebase-service-account.json`

OR set `FIREBASE_SERVICE_ACCOUNT_JSON` in `.env`.

Also set the Firebase Storage bucket in `.env`.

Never commit the service-account JSON or `.env`.

## 3. Configure Hugging Face

Copy `.env.example` to `.env` and add:

```env
HF_TOKEN=hf_your_token_here
```

The default model names can be changed if your Hugging Face account/provider exposes different models.

## 4. Run

```bash
python run.py
```

or:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open:
`http://localhost:8000/docs`

## Firebase data model

Firestore collection:
`claims/{claim_id}`

Each claim document contains incident details, witness statements, evidence metadata, AI observations, conflicts, verdict, confidence, explanation, RAG sources, and processing time.

Storage layout:
`claims/{claim_id}/evidence/{evidence_id}_{filename}`

## Important

This backend uses Firebase Admin SDK. Your teammate's Firebase Web/API config alone is normally **not enough** for a trusted server backend. You need the Firebase service-account credentials or a deployment environment with Google Application Default Credentials.

## 6-hour MVP note

This version intentionally avoids Docker and keeps the architecture small:
React Native → FastAPI → Firebase + Hugging Face.

See `frontend_integration.md` for the exact API contract.
