# ClaimForge Edge

ClaimForge Edge is a mobile-first insurance claim intake and verification system. A field agent can enter a claim, attach written or photographic evidence, and submit the information to a FastAPI backend. The backend stores the claim in Firebase/Firestore, indexes claim records in a local ChromaDB vector store, and uses Google Gemini to answer evidence-based questions and analyze claim images.

## What The Project Does

1. The React Native app collects claimant details, incident details, witness statements, and evidence.
2. The app sends claim and evidence data to the FastAPI service.
3. The backend stores claims, evidence, and analysis results in Firestore.
4. The RAG pipeline loads claim data, splits it into chunks, creates embeddings, and stores them in ChromaDB.
5. Gemini receives the retrieved evidence and produces a claim analysis or answer.
6. Image analysis describes visible damage and notes possible inconsistencies with the saved claim evidence.

## Repository Structure

```text
ClaimForge_Edge_Team_29_Ascend/
├── ai-service/       # FastAPI backend, Firebase integration, RAG, and Gemini analysis
├── frontend/         # React Native mobile claim intake application
├── firebase/         # Firestore and Storage security rules
└── README.md         # This guide
```

## Technologies Used

### Frontend

- React Native 0.73.4
- TypeScript 5.3.3
- React Navigation native stack
- `react-native-image-picker` for camera/gallery evidence
- `react-native-safe-area-context` and `react-native-screens`
- React Native Firebase packages for future native Firebase features

### Backend

- Python 3.12 recommended
- FastAPI and Uvicorn
- Pydantic for request validation
- Firebase Admin SDK and Google Cloud Firestore
- Firebase Storage integration
- ChromaDB for persistent vector search
- Sentence Transformers (`all-MiniLM-L6-v2` by default) for embeddings
- Google GenAI SDK for Gemini text and image analysis
- Pytest and FastAPI `TestClient` for testing

## Prerequisites

- Git
- Python 3.10 or newer
- Node.js 18 or newer and npm
- Android Studio, Android SDK, and an Android emulator for Android development
- Java 17 for Android builds
- macOS and Xcode for iOS builds
- A Firebase project with Firestore and Storage enabled
- A Google Gemini API key

## Backend Setup

From the repository root, create and activate a virtual environment:

### Windows PowerShell

```powershell
cd ai-service
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS/Linux

```bash
cd ai-service
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create `ai-service/.env` with Firebase and Gemini settings. Use values from your own Firebase service account; do not commit API keys, private keys, or service-account files.

```dotenv
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account-email
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_STORAGE_BUCKET=your-project-id.firebasestorage.app
LLM_API_KEY=your-gemini-api-key
LLM_MODEL=gemini-3.6-flash
MAX_FILE_SIZE_MB=10
CHROMA_DB_DIR=./chroma_db
```

The backend also contains a Firebase service-account JSON file for local project use. Keep credential files private and rotate them if they are ever exposed.

Start the API from `ai-service/`:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Useful URLs:

- API root: `http://localhost:8000/`
- Health check: `http://localhost:8000/health`
- Interactive API docs: `http://localhost:8000/docs`

## Frontend Setup

Install the mobile dependencies:

```bash
cd frontend
npm install
```

For iOS, install CocoaPods dependencies from the `frontend` directory:

```bash
cd ios
pod install
cd ..
```

Start Metro and run the app:

```bash
npm start
npm run android
```

For iOS on macOS:

```bash
npm run ios
```

The API URL is defined in `frontend/src/services/apiClient.ts`. The current configuration uses `http://localhost:8000` on iOS and `http://172.29.80.1:8000` on Android. Change the Android host to the IP address reachable from your emulator or physical device when necessary.

## Backend API

All claim routes use the `/api/v1/claims` prefix.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Confirm that the API is running |
| `GET` | `/health` | Check Firebase connectivity |
| `POST` | `/api/v1/claims` | Create a claim |
| `POST` | `/api/v1/claims/with-evidence` | Create a claim with text evidence |
| `GET` | `/api/v1/claims/{claim_id}` | Get one claim |
| `POST` | `/api/v1/claims/{claim_id}/evidence` | Upload text or image evidence using multipart form data |
| `GET` | `/api/v1/claims/{claim_id}/evidence` | List evidence for a claim |
| `POST` | `/api/v1/claims/{claim_id}/analyze` | Run RAG analysis, optionally with text and an image |
| `POST` | `/api/v1/claims/{claim_id}/rag/sync` | Load and index claim documents |
| `POST` | `/api/v1/claims/{claim_id}/rag/search` | Search retrieved evidence chunks |
| `POST` | `/api/v1/claims/{claim_id}/rag/query` | Retrieve evidence and generate a Gemini answer |

Example claim request:

```json
{
	"customerName": "Rahul Sharma",
	"description": "Rear bumper damage after a parking collision",
	"incidentDate": "2026-08-22",
	"incidentTime": "20:00",
	"location": "Rajkot"
}
```

Example RAG query:

```bash
curl -X POST http://localhost:8000/api/v1/claims/CLAIM_ID/rag/query \
	-H "Content-Type: application/json" \
	-d '{"query":"Does the evidence support the claim?","top_k":3}'
```

## Testing

Run the backend tests from `ai-service/`:

```bash
python -m pytest tests/ -q
```

The test suite covers API routes, request validation, chunking, vector search, claim isolation, and the RAG lifecycle. Live Firebase and Gemini smoke tests require valid credentials in `ai-service/.env` and create real test data, so use clearly marked test claims when running them.

## Firebase Rules

The `firebase/` directory contains the Firestore and Storage rules used to control access to stored claim data and uploaded evidence. Deploy them with the Firebase CLI after configuring the project:

```bash
firebase login
firebase use YOUR_FIREBASE_PROJECT_ID
firebase deploy --only firestore:rules,storage
```

## Current Limitations

- The backend currently stores image evidence metadata in Firestore; the uploaded image bytes are passed to analysis but are not uploaded by the current evidence route to Firebase Storage.
- The RAG vector database is local to the backend environment and is persisted in `ai-service/chroma_db`.
- iOS builds require macOS and Xcode.
- The Gemini model must be available to the configured API key. The current default is `gemini-3.6-flash`, and it can be overridden with `LLM_MODEL` in `.env`.
