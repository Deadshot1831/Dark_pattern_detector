"""Runtime configuration. All settings are environment-overridable."""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# --- Storage paths (point to a mounted volume in production) -----------------
DATABASE_PATH = os.getenv("DATABASE_PATH", str(PROJECT_ROOT / "deceptitech.db"))
STORAGE_DIR = Path(os.getenv("STORAGE_DIR", str(PROJECT_ROOT / "storage")))

# --- CORS --------------------------------------------------------------------
# Comma-separated list. "*" allows everything (only sensible in dev).
ALLOWED_ORIGINS = [
    o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",") if o.strip()
]

# --- Ollama ------------------------------------------------------------------
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_TIMEOUT_S = int(os.getenv("OLLAMA_TIMEOUT_S", "60"))
# "auto" = probe at request time and disable gracefully if not reachable
OLLAMA_ENABLED = os.getenv("OLLAMA_ENABLED", "auto").lower()
