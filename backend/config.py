"""Runtime configuration. All settings are environment-overridable."""
import os

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_TIMEOUT_S = int(os.getenv("OLLAMA_TIMEOUT_S", "60"))
# "auto" = probe at request time and disable gracefully if not reachable
OLLAMA_ENABLED = os.getenv("OLLAMA_ENABLED", "auto").lower()
