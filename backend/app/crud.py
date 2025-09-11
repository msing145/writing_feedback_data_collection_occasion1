from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone

from . import models_db as models
from .schemas import DemographicsIn, StartSessionIn, EssaySubmitIn
from .utils import word_count

def ensure_participant(db: Session, asurite: str, program_use_only: bool) -> models.Participant:
    participant = db.get(models.Participant, asurite)
    if participant is None:
        participant = models.Participant(asurite=asurite, program_use_only=program_use_only)
        db.add(participant)
        db.flush()
    else:
        # keep the latest choice for program_use_only
        participant.program_use_only = program_use_only
    return participant

def save_demographics(db: Session, payload: DemographicsIn) -> str:
    participant = ensure_participant(db, payload.ASURite.strip(), payload.program_use_only)

    demo = models.Demographics(
        asurite=participant.asurite,
        gender=payload.Gender,
        age=payload.Age,
        race_ethnicity=payload.Race_Ethnicity,
        race_ethnicity_specify=payload.Race_Ethnicity_Specify or "",
        major=payload.Major,
        major_category=payload.Major_Category,
        major_category_specify=payload.Major_Category_Specify or "",
        language_background=payload.Language_Background,
        native_language=payload.Native_Language or "",
        years_studied_english=payload.Years_Studied_English or "",
        years_in_us=payload.Years_in_US or "",
        program_use_only=payload.program_use_only,
    )
    db.add(demo)
    db.commit()
    return participant.asurite

def start_session(db: Session, payload: StartSessionIn) -> models.WritingSession:
    asurite = payload.asurite.strip()
    participant = ensure_participant(db, asurite, program_use_only=False)
    session = models.WritingSession(asurite=participant.asurite)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def submit_essay(db: Session, payload: EssaySubmitIn) -> models.WritingSession:
    session = db.get(models.WritingSession, payload.session_id)
    if session is None:
        raise ValueError("Invalid session_id")

    now = datetime.now(timezone.utc)
    session.submitted_at = now
    session.essay_text = payload.essay_text or ""
    session.word_count = word_count(session.essay_text)
    session.char_count = len(session.essay_text)

    if session.started_at:
        delta = now - session.started_at
        session.duration_seconds = int(delta.total_seconds())
    else:
        session.duration_seconds = 0

    db.add(session)
    db.commit()
    db.refresh(session)
    return session
