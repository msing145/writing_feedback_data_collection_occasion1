from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone

from . import models_db as models
from .schemas import DemographicsIn, StartSessionIn, EssaySubmitIn
from .utils import word_count

import logging

logger = logging.getLogger("writing-app")

MAX_ESSAY_CHARS = 20_000


def _norm_asurite(s: str) -> str:
    return (s or "").strip().lower()


def ensure_participant(db: Session, asurite: str, program_use_only: Optional[bool] = None) -> models.Participant:
    asurite = _norm_asurite(asurite)
    participant = db.get(models.Participant, asurite)
    if participant is None:
        participant = models.Participant(asurite=asurite, program_use_only=bool(program_use_only))
        db.add(participant)
        db.flush()
    elif program_use_only is not None and participant.program_use_only != program_use_only:
        participant.program_use_only = program_use_only
    return participant


def save_demographics(db: Session, payload: DemographicsIn) -> str:
    asurite = _norm_asurite(payload.asurite)
    participant = ensure_participant(db, asurite, payload.program_use_only)

    # upsert one-to-one demographics
    demo = db.scalar(select(models.Demographics).where(models.Demographics.asurite == participant.asurite))
    if demo is None:
        demo = models.Demographics(asurite=participant.asurite)
        db.add(demo)

    demo.gender = payload.gender
    demo.age = payload.age
    demo.race_ethnicity = payload.race_ethnicity
    demo.race_ethnicity_specify = payload.race_ethnicity_specify or ""
    demo.major = payload.major
    demo.major_category = payload.major_category
    demo.major_category_specify = payload.major_category_specify or ""
    demo.language_background = payload.language_background
    demo.native_language = payload.native_language or ""
    demo.years_studied_english = payload.years_studied_english or ""
    demo.years_in_us = payload.years_in_us or ""
    demo.program_use_only = payload.program_use_only

    db.commit()
    return participant.asurite


def start_session(db: Session, payload: StartSessionIn) -> models.WritingSession:
    asurite = _norm_asurite(payload.asurite)
    participant = ensure_participant(db, asurite, program_use_only=None)  # don't overwrite consent
    session = models.WritingSession(asurite=participant.asurite)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def _as_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Return a UTC-aware datetime. If naive, assume it was intended as UTC."""
    if dt is None:
        return None
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def submit_essay(db: Session, payload: EssaySubmitIn) -> models.WritingSession:
    session = db.get(models.WritingSession, payload.session_id)
    if session is None:
        raise ValueError("Invalid session_id")
    if session.submitted_at is not None:
        raise ValueError("Session already submitted")

    essay = (payload.essay_text or "").strip()
    if len(essay) > MAX_ESSAY_CHARS:
        raise ValueError(f"Essay too long (>{MAX_ESSAY_CHARS} characters).")

    now = datetime.now(timezone.utc)
    start = _as_utc(session.started_at)

    session.submitted_at = now
    session.essay_text = essay
    session.word_count = word_count(session.essay_text)
    session.char_count = len(session.essay_text)

    if start is not None:
        delta = now - start
        session.duration_seconds = int(delta.total_seconds())
    else:
        session.duration_seconds = 0

    db.commit()
    db.refresh(session)
    return session
