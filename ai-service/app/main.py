from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.firebase.firebase_config import has_firebase_config, health_check_firebase, initialize_firebase
from app.firebase.firestore_service import firestore_service
from app.firebase.storage_service import storage_service
from app.routes.claims import router as claims_router
from app.routes.evidence import router as evidence_router

app = FastAPI(title="ClaimForge Edge API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    if has_firebase_config():
        initialize_firebase()


@app.get("/health")
def health_check():
    try:
        if hasattr(firestore_service, "health_check"):
            return firestore_service.health_check()
        return health_check_firebase()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


app.include_router(claims_router)
app.include_router(evidence_router)


@app.get("/")
def root():
    return {"message": "ClaimForge Edge API is running"}
