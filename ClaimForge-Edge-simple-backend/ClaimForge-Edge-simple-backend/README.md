# ClaimForge Edge — Simple Backend

This is the intentionally simple backend flow requested for the frontend team.

## Architecture

React Native
    |
    | multipart/form-data
    v
FastAPI
    |
    +--> Hugging Face LLM/Vision
    |       |
    |       +--> verification verdict
    |
    +--> RAG store
    |       |
    |       +--> claim + evidence + verdict
    |
    +--> Question endpoint
            |
            +--> retrieve relevant stored evidence
            |
            +--> Hugging Face LLM
            |
            +--> answer

## 1. Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Put your Hugging Face token in `.env`:

```env
HF_TOKEN=hf_your_token_here
HF_MODEL=Qwen/Qwen2.5-VL-7B-Instruct
```

## 2. Run

```powershell
python run.py
```

Open:

http://localhost:8000/docs

## 3. Frontend -> claim verification

Endpoint:

`POST /api/claims/verify`

Content type:

`multipart/form-data`

Fields:

- `text` — claim/witness statement
- `image` — optional image
- `video` — optional video

Example:

```javascript
const form = new FormData();

form.append("text", "The accident happened at 4 PM.");
form.append("image", imageFile);
form.append("video", videoFile);

const response = await fetch(
  "http://localhost:8000/api/claims/verify",
  {
    method: "POST",
    body: form
  }
);

const result = await response.json();
console.log(result);
```

Response:

```json
{
  "claim_id": "...",
  "verdict": {
    "verdict": "requires_follow_up",
    "confidence": 0.82,
    "summary": "...",
    "conflicts": [],
    "supporting_evidence": [],
    "missing_evidence": [],
    "reason": "..."
  },
  "rag_record_id": "...",
  "rag_stored": true
}
```

## 4. Frontend -> question answering

Endpoint:

`POST /api/questions`

JSON:

```json
{
  "question": "Why was this claim marked for follow-up?"
}
```

Response:

```json
{
  "answer": "...",
  "reason": "...",
  "confidence": 0.88,
  "sources": ["..."]
}
```

## Important

The RAG store is deliberately simple and local: `data/rag_store.json`.

This lets the team run the backend with only a Hugging Face API key. Since your teammate already has Firebase, the same API contract can later be switched to Firestore/Storage by replacing the storage implementation.

For this simple version, video is used for basic metadata only. The image is sent directly to the vision-capable Hugging Face model. True video-content verification would require extracting key frames and sending selected frames to the vision model.

Never commit `.env` or Firebase/Hugging Face secrets to GitHub.
