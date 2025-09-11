# Writing Data Collection App (FastAPI + Vanilla JS)

This project rebuilds your Streamlit app into a **FastAPI backend** and a **vanilla JavaScript frontend**.


## Quick start

### 1) Create and activate a virtual environment

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

