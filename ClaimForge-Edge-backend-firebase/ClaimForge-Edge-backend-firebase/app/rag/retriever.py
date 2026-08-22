import json
import re
from pathlib import Path

class LocalRAG:
    def __init__(self, path: str):
        self.items = json.loads(Path(path).read_text(encoding="utf-8"))

    def retrieve(self, query: str, k: int = 4):
        tokens = set(re.findall(r"[a-z0-9]+", query.lower()))
        scored = []
        for item in self.items:
            text = f"{item.get('title','')} {item.get('rule','')}".lower()
            score = sum(1 for token in tokens if token in text)
            scored.append((score, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for score, item in scored[:k]]
