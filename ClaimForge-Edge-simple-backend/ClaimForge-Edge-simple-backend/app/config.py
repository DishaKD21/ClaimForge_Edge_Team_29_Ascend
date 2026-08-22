import os
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL = os.getenv("HF_MODEL", "Qwen/Qwen2.5-VL-7B-Instruct")

if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN is missing. Add it to .env")
