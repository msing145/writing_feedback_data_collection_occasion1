from pathlib import Path
import logging

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .config import settings
from .db import SessionLocal, engine, Base
from .schemas import (
    DemographicsIn, DemographicsOut,
    StartSessionIn, StartSessionOut,
    EssaySubmitIn, EssaySubmitOut,
    MessageOut,
)
from . import crud

# Logging
logging.basicConfig(
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("writing-app")

# Ensure tables are created (consider Alembic later)
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------------
# API ROUTES
# ------------------------

@app.get("/health", response_model=MessageOut)
def health() -> MessageOut:
    return MessageOut(message="ok")


@app.post("/api/demographics", response_model=DemographicsOut)
def post_demographics(payload: DemographicsIn, db: Session = Depends(get_db)) -> DemographicsOut:
    errors: list[str] = []

    # Q1–Q3
    if not payload.asurite:
        errors.append("Q1 (ASU email) is required.")
    if not payload.gender:
        errors.append("Q2 (Gender) is required.")
    if not payload.age:
        errors.append("Q3 (Age) is required.")

    # Q4 + Q5 packed into Race_Ethnicity
    race_line = (payload.race_ethnicity or "").strip()
    if not race_line:
        errors.append("Q4–Q5 (Hispanic origin and Race) are required.")
    else:
        hisp_ok = "Hispanic_Origin=" in race_line
        race_part = ""
        if "Race=" in race_line:
            race_part = race_line.split("Race=", 1)[1].strip()
        if not hisp_ok:
            errors.append("Q4 (Hispanic or Latino origin) is required.")
        if not race_part:
            errors.append("Q5 (Race) is required.")
        if "Other (please specify)" in race_part and not (payload.race_ethnicity_specify or "").strip():
            errors.append("Please specify your race for Q5 (Other).")

    # Q6 and conditional Q7–Q9
    if not payload.language_background:
        errors.append("Q6 (Language Background) is required.")
    if payload.language_background == "I grew up speaking language(s) other than English":
        if not payload.native_language:
            errors.append("Q7 (Native Language) is required.")
        if not payload.years_studied_english:
            errors.append("Q8 (Years Studied English) is required.")
        if not payload.years_in_us:
            errors.append("Q9 (Years in US) is required.")

    if errors:
        raise HTTPException(status_code=422, detail=errors)

    asurite = crud.save_demographics(db, payload)
    logger.info("Saved demographics for %s", asurite)
    return DemographicsOut(asurite=asurite, saved=True)


@app.post("/api/writing-session/start", response_model=StartSessionOut)
def start_writing_session(payload: StartSessionIn, db: Session = Depends(get_db)) -> StartSessionOut:
    if not payload.asurite:
        raise HTTPException(status_code=422, detail=["ASURite is required to start a session."])
    session = crud.start_session(db, payload)
    logger.info("Started writing session %s for %s", session.id, session.asurite)
    return StartSessionOut(session_id=session.id, started_at=session.started_at)


@app.post("/api/essay/submit", response_model=EssaySubmitOut)
def submit_essay(payload: EssaySubmitIn, db: Session = Depends(get_db)) -> EssaySubmitOut:
    try:
        session = crud.submit_essay(db, payload)
    except ValueError as e:
        msg = str(e)
        code = 400 if ("long" in msg or "already" in msg) else 404
        raise HTTPException(status_code=code, detail=msg)

    logger.info(
        "Submitted essay for session %s (%s seconds, %s words)",
        session.id, session.duration_seconds, session.word_count
    )
    return EssaySubmitOut(
        session_id=session.id,
        submitted_at=session.submitted_at,
        duration_seconds=session.duration_seconds or 0,
        word_count=session.word_count,
        char_count=session.char_count,
    )

# ------------------------
# STATIC FRONTEND
# ------------------------
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
