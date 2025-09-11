# Writing Data Collection App (FastAPI + Vanilla JS)

This project rebuilds your Streamlit app into a **FastAPI backend** and a **vanilla JavaScript frontend**.


## Quick start

### 1) Create and activate a virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 2) Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3) Run the API

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at: http://localhost:8000

### 4) Open the frontend

Open `frontend/index.html` in your browser. For local development with CORS-friendly defaults, you can use a simple static server (optional):

```bash
# from the project root
python -m http.server 5173
# then visit http://localhost:5173/frontend/index.html
```

> The frontend talks to the backend at `http://localhost:8000` by default. You can change this in `frontend/js/api.js` if needed.

---

## Data Storage

- Uses **SQLite** by default (`./backend/data/app.db`).
- Tables:
  - `participants` – stores the `asurite` and `program_use_only` flag.
  - `demographics` – one row per participant with demographic survey responses.
  - `writing_sessions` – one row per writing session. When a user lands on the writing page, the frontend calls `/api/writing-session/start`, which creates a session and stores the **server-side** `started_at`. On submission, the frontend calls `/api/essay/submit` with `session_id` and the essay text. The server records `submitted_at`, computes `duration_seconds`, and stores the essay.

> You can back up the DB or export to CSV later as needed.

---

## API Overview

- `POST /api/demographics` – Save demographic data.
- `POST /api/writing-session/start` – Start a writing session (stores server-side `started_at`).
- `POST /api/essay/submit` – Submit essay for a given `session_id`; server computes and stores duration.
- `GET  /health` – Health check.

See `backend/app/main.py` and `backend/app/schemas.py` for request/response payloads.

---

## Validation & Consent

- Mirrors the Streamlit fields and conditional logic.
- `program_use_only` is saved with the participant and demographic record.

---

## Notes

- Minimal styling with vanilla CSS; feel free to layer on your preferred UI framework later.
- Code follows PEP 8, uses type hints, and has structured logging for auditability.

