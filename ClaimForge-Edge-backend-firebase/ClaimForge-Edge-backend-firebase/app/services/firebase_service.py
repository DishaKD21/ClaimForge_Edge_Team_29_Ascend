import json
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore, storage
from app.core.config import settings

_app = None
_db = None
_bucket = None

def init_firebase():
    global _app, _db, _bucket
    if _app:
        return
    if settings.firebase_service_account_json:
        info = json.loads(settings.firebase_service_account_json)
        cred = credentials.Certificate(info)
    elif settings.firebase_service_account_path and Path(settings.firebase_service_account_path).exists():
        cred = credentials.Certificate(settings.firebase_service_account_path)
    else:
        # Supports GOOGLE_APPLICATION_CREDENTIALS / platform ADC when deployed.
        cred = credentials.ApplicationDefault()
    options = {}
    if settings.firebase_storage_bucket:
        options["storageBucket"] = settings.firebase_storage_bucket
    _app = firebase_admin.initialize_app(cred, options)
    _db = firestore.client()
    _bucket = storage.bucket(app=_app)

def db():
    init_firebase()
    return _db

def bucket():
    init_firebase()
    return _bucket

def save_claim(claim: dict):
    db().collection(settings.firebase_claims_collection).document(claim["claim_id"]).set(claim)
    return claim

def get_claim(claim_id: str):
    snap = db().collection(settings.firebase_claims_collection).document(claim_id).get()
    return snap.to_dict() if snap.exists else None

def upload_file(local_path: str, destination: str, content_type: str | None = None):
    blob = bucket().blob(destination)
    blob.upload_from_filename(local_path, content_type=content_type)
    # Use a signed URL for frontend access without making the bucket public.
    url = blob.generate_signed_url(version="v4", expiration=3600, method="GET")
    return url
