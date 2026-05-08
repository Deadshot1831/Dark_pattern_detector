# DeceptiTech

Dark pattern detection system. Given a public website URL, it crawls the page and reports manipulative UI/UX patterns with evidence, severity, and suggested fixes.

## Status

- **Phase 1**: Scaffold + URL validation + scan persistence — done
- **Phase 2**: Playwright crawler + screenshot capture — done
- Phases 3–10: see plan in chat history

## Setup

```bash
# 1. Create venv (Python 3.10+)
/opt/homebrew/bin/python3.13 -m venv .venv
source .venv/bin/activate

# 2. Install backend deps + Chromium
pip install -r backend/requirements.txt
python -m playwright install chromium

# 3. Run API
uvicorn backend.main:app --reload --port 8000
```

Open http://localhost:8000/docs for the interactive API.

## API (current)

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/scan` | Start a scan. Body: `{"url": "https://..."}` |
| `GET`  | `/scan/{scan_id}` | Poll status / get result |
| `GET`  | `/scan/{scan_id}/screenshot/{full_page\|viewport}` | Serve screenshot |
| `GET`  | `/health` | Health check |

## Storage

- SQLite DB: `./deceptitech.db`
- Screenshots + HTML: `./storage/screenshots/{scan_id}/`

## Dataset

`dark-patterns-v2.csv` — 1,818 labeled rows (Scarcity, Urgency, Confirmshaming, etc.). Used in Phase 4 (rule mining), Phase 5 (LLM few-shot), and Phase 9 (evaluation).
