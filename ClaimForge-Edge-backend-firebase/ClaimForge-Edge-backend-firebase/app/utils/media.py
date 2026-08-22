import base64
import mimetypes
import hashlib
from pathlib import Path
import cv2

def image_to_data_url(path: str):
    mime = mimetypes.guess_type(path)[0] or "image/jpeg"
    data = base64.b64encode(Path(path).read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"

def sha256_file(path: str):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def sample_video_frames(path: str, out_dir: str, count=3):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total <= 0:
        cap.release(); return []
    indexes = [int(i * (total - 1) / max(count - 1, 1)) for i in range(count)]
    result = []
    for n, idx in enumerate(indexes):
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, frame = cap.read()
        if ok:
            p = str(Path(out_dir) / f"frame_{n}.jpg")
            cv2.imwrite(p, frame)
            result.append(p)
    cap.release()
    return result
