import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Settings:
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "")
    FIREBASE_PRIVATE_KEY_ID = os.getenv("FIREBASE_PRIVATE_KEY_ID", "")
    FIREBASE_PRIVATE_KEY = os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n")
    FIREBASE_CLIENT_EMAIL = os.getenv("FIREBASE_CLIENT_EMAIL", "")
    FIREBASE_CLIENT_ID = os.getenv("FIREBASE_CLIENT_ID", "")
    FIREBASE_STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET", "")
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".mp4", ".mov", ".txt"}
    ALLOWED_MIME_TYPES = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "video/mp4": ".mp4",
        "video/quicktime": ".mov",
        "text/plain": ".txt",
    }

    @classmethod
    def required_firebase_values(cls):
        return {
            "FIREBASE_PROJECT_ID": cls.FIREBASE_PROJECT_ID,
            "FIREBASE_PRIVATE_KEY_ID": cls.FIREBASE_PRIVATE_KEY_ID,
            "FIREBASE_PRIVATE_KEY": cls.FIREBASE_PRIVATE_KEY,
            "FIREBASE_CLIENT_EMAIL": cls.FIREBASE_CLIENT_EMAIL,
            "FIREBASE_CLIENT_ID": cls.FIREBASE_CLIENT_ID,
            "FIREBASE_STORAGE_BUCKET": cls.FIREBASE_STORAGE_BUCKET,
        }


settings = Settings()
