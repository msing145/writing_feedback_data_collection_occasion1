from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
import uuid

from .db import Base

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

class Participant(Base):
    __tablename__ = "participants"
    asurite: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    program_use_only: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    demographics = relationship("Demographics", back_populates="participant", uselist=False)
    sessions = relationship("WritingSession", back_populates="participant")

class Demographics(Base):
    __tablename__ = "demographics"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asurite: Mapped[str] = mapped_column(String, ForeignKey("participants.asurite"), nullable=False, index=True)

    # Fields mirrored from Streamlit app
    gender: Mapped[str] = mapped_column(String, nullable=False)
    age: Mapped[str] = mapped_column(String, nullable=False)
    race_ethnicity: Mapped[str] = mapped_column(String, nullable=False)
    race_ethnicity_specify: Mapped[str] = mapped_column(String, default="", nullable=False)
    major: Mapped[str] = mapped_column(String, nullable=False)
    major_category: Mapped[str] = mapped_column(String, nullable=False)
    major_category_specify: Mapped[str] = mapped_column(String, default="", nullable=False)
    language_background: Mapped[str] = mapped_column(String, nullable=False)
    native_language: Mapped[str] = mapped_column(String, default="", nullable=False)
    years_studied_english: Mapped[str] = mapped_column(String, default="", nullable=False)
    years_in_us: Mapped[str] = mapped_column(String, default="", nullable=False)

    program_use_only: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    participant = relationship("Participant", back_populates="demographics")

class WritingSession(Base):
    __tablename__ = "writing_sessions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    asurite: Mapped[str] = mapped_column(String, ForeignKey("participants.asurite"), nullable=False, index=True)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=True)

    essay_text: Mapped[str] = mapped_column(Text, default="", nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    char_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    participant = relationship("Participant", back_populates="sessions")
