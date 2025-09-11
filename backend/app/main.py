from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import logging

from .config import settings
from .db import SessionLocal, engine, Base
from .schemas import (
    DemographicsIn, DemographicsOut,
    StartSessionIn, StartSessionOut,
    EssaySubmitIn, EssaySubmitOut,
    MessageOut
)
from . import crud

# Configure logging
logging.basicConfig(
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("writing-app")

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME)

# CORS (allow localhost and file:// origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_ORIGINS + ["*"],  # dev-friendly
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health", response_model=MessageOut)
def health() -> MessageOut:
    return MessageOut(message="ok")

@app.post("/api/demographics", response_model=DemographicsOut)
def post_demographics(payload: DemographicsIn, db: Session = Depends(get_db)) -> DemographicsOut:
    # Basic validation mirroring the Streamlit app's required fields
    errors: list[str] = []
    if not payload.ASURite:
        errors.append("Q1 (ASURite) is required.")
    if not payload.Gender:
        errors.append("Q2 (Gender) is required.")
    if not payload.Age:
        errors.append("Q3 (Age) is required.")
    if not payload.Race_Ethnicity:
        errors.append("Q4 (Race/Ethnicity) is required.")
    if payload.Race_Ethnicity == "Multiple ethnicity / Other (please specify)" and not payload.Race_Ethnicity_Specify:
        errors.append("Please specify your ethnicity.")
    if not payload.Major:
        errors.append("Q5 (Major) is required.")
    if not payload.Major_Category:
        errors.append("Q6 (Major Category) is required.")
    if payload.Major_Category == "Other (Please specify)" and not payload.Major_Category_Specify:
        errors.append("Please specify the category for Q6.")
    if not payload.Language_Background:
        errors.append("Q7 (Language Background) is required.")
    if payload.Language_Background == "I grew up speaking language(s) other than English":
        if not payload.Native_Language:
            errors.append("Q8 (Native Language) is required.")
        if not payload.Years_Studied_English:
            errors.append("Q9 (Years Studied English) is required.")
        if not payload.Years_in_US:
            errors.append("Q10 (Years in US) is required.")
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
        raise HTTPException(status_code=404, detail=str(e))

    logger.info("Submitted essay for session %s (%s seconds, %s words)",
                session.id, session.duration_seconds, session.word_count)
    return EssaySubmitOut(
        session_id=session.id,
        submitted_at=session.submitted_at,
        duration_seconds=session.duration_seconds or 0,
        word_count=session.word_count,
        char_count=session.char_count,
    )
