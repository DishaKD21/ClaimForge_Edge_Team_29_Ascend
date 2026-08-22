import firebase_admin
from firebase_admin import credentials, firestore, storage

from app.config import settings

_firebase_app = None
_firestore_client = None
_storage_bucket = None


def has_firebase_config():
    return all(value for value in settings.required_firebase_values().values())


def initialize_firebase():
    global _firebase_app, _firestore_client, _storage_bucket

    missing = [key for key, value in settings.required_firebase_values().items() if not value]
    if missing:
        raise RuntimeError(
            "Missing Firebase environment variables: " + ", ".join(missing)
        )

    if not firebase_admin._apps:
        private_key = settings.FIREBASE_PRIVATE_KEY.replace("\\n", "\n")
        service_account = {
            "type": "service_account",
            "project_id": settings.FIREBASE_PROJECT_ID,
            "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
            "private_key": private_key,
            "client_email": settings.FIREBASE_CLIENT_EMAIL,
            "client_id": settings.FIREBASE_CLIENT_ID,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": (
                f"https://www.googleapis.com/robot/v1/metadata/x509/"
                f"{settings.FIREBASE_CLIENT_EMAIL.replace('@', '%40')}"
            ),
        }
        cred = credentials.Certificate(service_account)
        _firebase_app = firebase_admin.initialize_app(
            cred,
            {
                "projectId": settings.FIREBASE_PROJECT_ID,
                "storageBucket": settings.FIREBASE_STORAGE_BUCKET,
            },
        )
    else:
        _firebase_app = firebase_admin.get_app()

    _firestore_client = firestore.client()
    _storage_bucket = storage.bucket(name=settings.FIREBASE_STORAGE_BUCKET)

    return _firebase_app


def get_firestore_client():
    if _firestore_client is None:
        initialize_firebase()
    return _firestore_client


def get_storage_bucket():
    if _storage_bucket is None:
        initialize_firebase()
    return _storage_bucket


def health_check_firebase():
    if _firestore_client is None:
        initialize_firebase()

    try:
        _firestore_client.collection("claims").limit(1).get()
        _storage_bucket.exists()
        return {"status": "ok", "firebase": "connected"}
    except Exception as exc:
        raise RuntimeError(f"Firebase connection check failed: {exc}") from exc
