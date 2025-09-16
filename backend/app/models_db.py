from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
import uuid

from .db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Participant(Base):
    __tablename__ = "participants"

    # ASURITE IDs at ASU are usually short (max ~30 chars)
    asurite: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)

    program_use_only: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    demographics = relationship("Demographics", back_populates="participant", uselist=False)
    sessions = relationship("WritingSession", back_populates="participant")


class Demographics(Base):
    __tablename__ = "demographics"
    __table_args__ = (UniqueConstraint("asurite", name="uq_demographics_asurite"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # FK must match Participant.asurite length
    asurite: Mapped[str] = mapped_column(String(50), ForeignKey("participants.asurite"), nullable=False, index=True)

    # Demographic fields — VARCHAR(255) is a safe default
    gender: Mapped[str] = mapped_column(String(50), nullable=False)
    age: Mapped[str] = mapped_column(String(10), nullable=False)
    race_ethnicity: Mapped[str] = mapped_column(String(100), nullable=False)
    race_ethnicity_specify: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    major: Mapped[str] = mapped_column(String(255), nullable=False)
    major_category: Mapped[str] = mapped_column(String(255), nullable=False)
    major_category_specify: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    language_background: Mapped[str] = mapped_column(String(100), nullable=False)
    native_language: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    years_studied_english: Mapped[str] = mapped_column(String(10), default="", nullable=False)
    years_in_us: Mapped[str] = mapped_column(String(10), default="", nullable=False)

    program_use_only: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    participant = relationship("Participant", back_populates="demographics")


class WritingSession(Base):
    __tablename__ = "writing_sessions"

    # UUID stored as string — 36 chars (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    asurite: Mapped[str] = mapped_column(String(50), ForeignKey("participants.asurite"), nullable=False, index=True)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=True)

    essay_text: Mapped[str] = mapped_column(Text, default="", nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    char_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    participant = relationship("Participant", back_populates="sessions")
