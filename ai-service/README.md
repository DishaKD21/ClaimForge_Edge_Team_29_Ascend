# ClaimForge Edge Backend

This backend provides the Firebase-backed API layer for the ClaimForge Edge application. It currently supports claim creation, claim lookup, evidence uploads, text evidence storage, and Firebase connectivity health checks.

## 1. Firebase project setup

1. Create a Firebase project in the Firebase Console.
2. Enable Firestore Database.
3. Enable Firebase Storage.
4. In Project Settings > Service Accounts, generate a new private key.
5. Download the JSON file and copy the values into your environment variables.
6. Make sure the service account has the following roles or equivalent permissions:
   - Firebase Admin SDK Administrator Service Agent
   - Cloud Datastore User
   - Storage Object Admin

## 2. Required environment variables

Create a `.env` file based on `.env.example`:

```env
FIREBASE_PROJECT_ID=
FIREBASE_PRIVATE_KEY_ID=
FIREBASE_PRIVATE_KEY=
FIREBASE_CLIENT_EMAIL=
FIREBASE_CLIENT_ID=
FIREBASE_STORAGE_BUCKET=
MAX_FILE_SIZE_MB=10
```

Notes:
- `FIREBASE_PRIVATE_KEY` should include the full PEM value and may contain escaped newlines like `\n`.
- The backend automatically converts escaped newline characters to the correct format.

## 3. Install dependencies

From the `ai-service` folder:

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# or .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## 4. How to run FastAPI

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open:

- Swagger docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 5. How to test every endpoint using Swagger

1. Start the server.
2. Open http://localhost:8000/docs.
3. Use the `/health` endpoint to check Firebase connectivity.
4. Create a claim using `POST /api/v1/claims`.
5. Retrieve it with `GET /api/v1/claims/{claim_id}`.
6. Upload an image or video with `POST /api/v1/claims/{claim_id}/evidence`.
7. Add text evidence with `type=text` and `content` in form-data.
8. List all evidence with `GET /api/v1/claims/{claim_id}/evidence`.

## 6. Example requests and responses

### Create claim

Request:

```json
{
  "customerName": "Rahul Sharma",
  "description": "Car accident on highway",
  "incidentDate": "2026-08-22",
  "incidentTime": "20:00",
  "location": "Rajkot"
}
```

Response:

```json
{
  "claimId": "abcd1234",
  "message": "Claim created successfully"
}
```

### Health check

Response:

```json
{
  "status": "ok",
  "firebase": "connected"
}
```

### Upload image evidence

Form-data fields:
- `type`: `image`
- `file`: binary file

### Upload text evidence

Form-data fields:
- `type`: `text`
- `content`: `Witness statement`

### List evidence

Response:

```json
[
  {
    "id": "evidence_doc_id",
    "claimId": "claim_doc_id",
    "type": "image",
    "fileName": "accident.jpg",
    "storagePath": "claims/CLM001/evidence/accident.jpg",
    "mimeType": "image/jpeg",
    "uploadedAt": "2026-08-22T12:00:00+00:00"
  }
]
```

## Notes

- This project intentionally does not include AI, RAG, LLM, or media analysis features yet.
- Firebase Firestore and Firebase Storage are the only integration pieces configured at this stage.
- Firestore collections are automatically created on first write when the API is called.
