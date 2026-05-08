"""Minimal async client for the local Ollama HTTP API.

Two methods only:
    - is_alive(): probe /api/tags and confirm the configured model is loaded.
    - chat_json(system, user): send a chat request demanding a JSON response.

All errors are logged and swallowed — the caller treats None as "no signal".
"""
from __future__ import annotations

import json
import logging
from typing import Optional

import httpx

from ..config import OLLAMA_ENABLED, OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_TIMEOUT_S

log = logging.getLogger(__name__)

_alive_cache: Optional[bool] = None


async def is_alive() -> bool:
    """True if Ollama is reachable AND the configured model is present.

    Cached after the first successful probe to avoid extra round-trips.
    """
    global _alive_cache
    if OLLAMA_ENABLED == "false":
        return False
    if _alive_cache is True:
        return True
    try:
        async with httpx.AsyncClient(timeout=3) as c:
            r = await c.get(f"{OLLAMA_HOST}/api/tags")
            r.raise_for_status()
            tags = r.json().get("models", [])
            for m in tags:
                if m.get("name") == OLLAMA_MODEL or m.get("model") == OLLAMA_MODEL:
                    _alive_cache = True
                    return True
            log.warning("Ollama is up but model %s is not loaded", OLLAMA_MODEL)
    except Exception as e:
        log.info("Ollama probe failed (%s): %s", type(e).__name__, e)
    return False


async def chat_json(system: str, user: str) -> Optional[dict]:
    """Send a chat completion in Ollama JSON mode. Returns parsed dict or None."""
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "format": "json",
        "stream": False,
        "options": {"temperature": 0.1},
    }
    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT_S) as c:
            r = await c.post(f"{OLLAMA_HOST}/api/chat", json=payload)
            r.raise_for_status()
            content = r.json().get("message", {}).get("content", "")
            return json.loads(content)
    except (httpx.HTTPError, json.JSONDecodeError, KeyError) as e:
        log.warning("Ollama chat failed: %s: %s", type(e).__name__, e)
        return None
