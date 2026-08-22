import base64
import json
from pathlib import Path
from huggingface_hub import InferenceClient
from app.config import HF_TOKEN, HF_MODEL

client = InferenceClient(api_key=HF_TOKEN)

def image_data_url(path: Path) -> str:
    mime = "image/jpeg"
    if path.suffix.lower() == ".png":
        mime = "image/png"
    elif path.suffix.lower() == ".webp":
        mime = "image/webp"
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"

def ask_llm(prompt: str, image_path: Path | None = None) -> dict:
    content = [{"type": "text", "text": prompt}]
    if image_path:
        content.append({
            "type": "image_url",
            "image_url": {"url": image_data_url(image_path)}
        })

    response = client.chat.completions.create(
        model=HF_MODEL,
        messages=[{"role": "user", "content": content}],
        max_tokens=700,
        temperature=0.1,
    )

    raw = (response.choices[0].message.content or "").strip()
    if raw.startswith("```"):
        raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "verdict": "requires_follow_up",
            "confidence": 0.0,
            "summary": raw[:500],
            "conflicts": ["Model response was not valid JSON."],
            "supporting_evidence": [],
            "missing_evidence": [],
            "reason": "The system could not safely parse the AI response."
        }
