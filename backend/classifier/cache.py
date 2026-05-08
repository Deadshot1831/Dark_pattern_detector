"""File-backed prompt response cache.

Same prompt + same model => same answer, persisted to disk so repeated scans
don't re-hit Ollama. Atomic-enough for our single-process use.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Optional

from ..config import OLLAMA_MODEL

CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "storage" / "llm_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _key(prompt: str) -> str:
    h = hashlib.sha256(f"{OLLAMA_MODEL}::{prompt}".encode("utf-8")).hexdigest()
    return h[:32]


def get(prompt: str) -> Optional[dict]:
    f = CACHE_DIR / f"{_key(prompt)}.json"
    if not f.exists():
        return None
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return None


def put(prompt: str, value: dict) -> None:
    f = CACHE_DIR / f"{_key(prompt)}.json"
    f.write_text(json.dumps(value, indent=2), encoding="utf-8")
