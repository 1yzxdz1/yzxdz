from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class MockExamAnswer(TimestampMixin, Base):
    __tablename__ = "mock_exam_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    mock_exam_id: Mapped[int] = mapped_column(ForeignKey("mock_exams.id"), nullable=False, index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False, index=True)
    user_answer: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    obtained_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    explanation_snapshot: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    mock_exam: Mapped["MockExam"] = relationship(back_populates="answers")
    question: Mapped["Question"] = relationship(back_populates="mock_exam_answers")
