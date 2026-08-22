import json
import re
from huggingface_hub import InferenceClient
from app.core.config import settings

class HFClient:
    def __init__(self):
        self.client = InferenceClient(token=settings.hf_token, provider="auto", timeout=settings.analysis_timeout_seconds)

    def _check(self):
        if not settings.hf_token:
            raise RuntimeError("HF_TOKEN is missing. Add it to .env")

    def chat(self, messages, model=None, max_tokens=800, temperature=0.1):
        self._check()
        result = self.client.chat.completions.create(
            model=model or settings.hf_text_model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return result.choices[0].message.content or ""

    def vision(self, prompt, image_data_urls):
        self._check()
        content = [{"type":"text", "text":prompt}]
        for url in image_data_urls[:4]:
            content.append({"type":"image_url", "image_url":{"url":url}})
        return self.chat([{"role":"user", "content":content}], model=settings.hf_vision_model, max_tokens=500)

    @staticmethod
    def parse_json(text: str):
        text = text.strip()
        try:
            return json.loads(text)
        except Exception:
            match = re.search(r"\{.*\}", text, re.S)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception:
                    return None
        return None
