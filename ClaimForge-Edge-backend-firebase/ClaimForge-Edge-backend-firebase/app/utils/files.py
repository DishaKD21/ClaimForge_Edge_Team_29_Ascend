import mimetypes
import re
import uuid
from pathlib import Path

ALLOWED_EXTENSIONS = {".jpg",".jpeg",".png",".webp",".mp4",".mov",".avi",".mkv",".txt"}

def new_id(prefix="id"):
    return f"{prefix}_{uuid.uuid4().hex[:12]}"

def safe_filename(name: str):
    name = Path(name).name
    return re.sub(r"[^A-Za-z0-9._-]", "_", name)[:150] or "evidence"

def guess_media_type(filename, content_type=None):
    return content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
