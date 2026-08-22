from pathlib import Path
import cv2

def summarize_video(path: Path) -> str:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        return "Video could not be opened."

    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0)
    duration = frames / fps if fps else 0
    cap.release()

    return f"Video metadata: approximately {duration:.1f} seconds, {frames} frames."
