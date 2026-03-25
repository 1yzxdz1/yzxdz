from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class StudyRecord(TimestampMixin, Base):
    __tablename__ = "study_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False, index=True)
    question_id: Mapped[Optional[int]] = mapped_column(ForeignKey("questions.id"), nullable=True, index=True)
    chapter_id: Mapped[Optional[int]] = mapped_column(ForeignKey("chapters.id"), nullable=True, index=True)
    mode: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    user_answer: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    score_obtained: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    practiced_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False, default=datetime.utcnow)

    subject: Mapped["Subject"] = relationship(back_populates="study_records")
    question: Mapped[Optional["Question"]] = relationship(back_populates="study_records")
