# DeceptiTech

Dark pattern detection system. Given a public website URL, it crawls the page in a real browser, runs five rule-based detectors (with an optional local LLM second pass for ambiguous text), and produces a structured report with evidence, confidence scores, severity, and suggested fixes.

## Status

| Phase | What it adds | Status |
|---|---|---|
| 1 | FastAPI scaffold, SQLite, SSRF-guarded URL validation | ✅ |
| 2 | Playwright crawler + viewport / full-page screenshots | ✅ |
| 3 | HTML/text extractor → buttons, checkboxes, modals, cookie banners, countdowns | ✅ |
| 4 | 5 rule-based detectors (urgency, scarcity, confirmshaming, preselected, cookie) | ✅ |
| 5 | Ollama LLM enrichment for confirmshaming variants | ✅ |
| 7 | Next.js dashboard | ✅ |
| 6 / 8 / 9 / 10 | Report export, history, evaluation, deployment | ⏳ |

## Setup

### Backend

```bash
# 1. Create Python venv (3.10+ required)
/opt/homebrew/bin/python3.13 -m venv .venv
source .venv/bin/activate

# 2. Install deps + Chromium
pip install -r backend/requirements.txt
python -m playwright install chromium

# 3. Run the API
uvicorn backend.main:app --reload --port 8000
```

API docs at http://localhost:8000/docs.

### Ollama (optional but recommended for Phase 5)

```bash
brew install ollama
ollama serve &
ollama pull llama3.1:8b
```

The backend probes Ollama at request time. If it's down, the LLM pass is silently skipped — rule detectors still run.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000.

The frontend reads the API base URL from `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`). To change it, create `frontend/.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/scan` | Start a scan. Body: `{"url": "https://..."}` |
| `GET`  | `/scan/{id}` | Scan status + summary (severity, total findings) |
| `GET`  | `/scan/{id}/detections` | List of detected patterns with evidence + suggested fixes |
| `GET`  | `/scan/{id}/extracted` | Raw extracted page sections (debug) |
| `GET`  | `/scan/{id}/screenshot/{full_page\|viewport}` | PNG |
| `GET`  | `/health` | Health check |

## Layout

```
backend/
  main.py                    FastAPI entry
  config.py                  Env vars (Ollama host/model)
  api/scan.py                /scan endpoints + background pipeline
  crawler/                   Playwright headless browser
  extractor/                 BeautifulSoup → structured page sections
  detectors/                 5 rule + DOM detectors, registry
  classifier/                Ollama client, prompts, few-shot, cache
  db/                        SQLAlchemy models + SQLite
  utils/url_validator.py     SSRF guard
  tests/                     Runnable smoke tests + fixture
frontend/
  app/page.tsx               URL submission form
  app/scan/[id]/page.tsx     Live-polled report viewer
  components/                ScanForm, DetectionCard, SeverityBadge, StatusBadge
  lib/api.ts                 Backend client
storage/
  screenshots/{scan_id}/     full_page.png · viewport.png · page.html
  llm_cache/                 prompt → JSON cache
dark-patterns-v2.csv         1,818-row labelled dataset
```

## Running the smoke tests

```bash
.venv/bin/python -m backend.tests.test_extractor       # 11 invariants on the popup fixture
.venv/bin/python -m backend.tests.test_detectors       # 9 detection invariants
.venv/bin/python -m backend.tests.test_llm_classifier  # positive/negative LLM cases (auto-skips if Ollama is down)
```

## Dataset

`dark-patterns-v2.csv` — 1,818 labeled rows (Scarcity, Urgency, Confirmshaming, Misdirection, Sneaking, Forced Action). Used for keyword mining (Phase 4), few-shot prompts (Phase 5), and evaluation (Phase 9).
