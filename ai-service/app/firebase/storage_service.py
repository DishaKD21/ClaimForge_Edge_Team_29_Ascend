import os
from datetime import datetime, timezone

from firebase_admin import storage

from app.config import settings
from app.firebase.firebase_config import get_storage_bucket


class StorageService:
    def __init__(self):
        self.bucket = None

    def _ensure_bucket(self):
        if self.bucket is None:
            self.bucket = get_storage_bucket()
        return self.bucket

    def upload_file(self, file, claim_id: str, original_filename: str) -> str:
        if file is None:
            raise ValueError("Empty file")

        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)

        if size == 0:
            raise ValueError("Empty file")

        if size > settings.MAX_FILE_SIZE_BYTES:
            raise ValueError("File size exceeds the configured limit")

        filename = os.path.basename(original_filename)
        file_ext = os.path.splitext(filename)[1].lower()

        if file_ext not in {".jpg", ".jpeg", ".png", ".txt"}:
            raise ValueError("Unsupported file type")

        raise NotImplementedError("Firebase Storage is temporarily disabled for this project")

    @staticmethod
    def _detect_content_type(filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        mapping = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".txt": "text/plain",
        }
        return mapping.get(ext, "application/octet-stream")


storage_service = StorageService()
