from typing import List, Optional

from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Question(TimestampMixin, Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False, index=True)
    chapter_id: Mapped[Optional[int]] = mapped_column(ForeignKey("chapters.id"), nullable=True, index=True)
    chapter: Mapped[str] = mapped_column(String(120), nullable=False)
    question_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    stem: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    answer: Mapped[list] = mapped_column(JSON, nullable=False)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, default="medium", index=True)
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=2)

    subject: Mapped["Subject"] = relationship(back_populates="questions")
    chapter_rel: Mapped[Optional["Chapter"]] = relationship(back_populates="questions")
    study_records: Mapped[List["StudyRecord"]] = relationship(back_populates="question")
    wrong_questions: Mapped[List["WrongQuestion"]] = relationship(back_populates="question")
    favorites: Mapped[List["FavoriteQuestion"]] = relationship(back_populates="question")
    mock_exam_answers: Mapped[List["MockExamAnswer"]] = relationship(back_populates="question")
