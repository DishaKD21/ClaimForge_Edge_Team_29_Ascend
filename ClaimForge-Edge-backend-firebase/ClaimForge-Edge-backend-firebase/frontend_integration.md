# Frontend integration

## Analyze a claim
`POST /api/v1/claims/analyze` as `multipart/form-data`.

Fields:
- `incident_description`: string
- `claim_id`: optional string
- `incident_timestamp`: optional ISO timestamp
- `witness_statements`: JSON array, e.g. `["Witness saw impact at 3 PM"]`
- `evidence`: one or more photo/video/text files

Response includes:
- `claim_id`
- `verdict`: `valid`, `requires_follow_up`, or `fraudulent`
- `confidence`
- `explanation`
- `conflicts`
- `supporting_evidence`
- `missing_evidence`
- `evidence[].storage_url`
- `processing_ms`

## Get claim
`GET /api/v1/claims/{claim_id}`

## Claim chatbot
`POST /api/v1/claims/{claim_id}/chat`
JSON body: `{ "question": "Why was this claim flagged?" }`

## Local development
Run the backend on `http://localhost:8000` and give this base URL to the React Native team. Android emulator usually reaches host services through `http://10.0.2.2:8000`; a physical phone should use the computer's LAN IP.
