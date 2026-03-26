from typing import List, Optional

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Subject(TimestampMixin, Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    level: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    exam_duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=90)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommended_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    chapters: Mapped[List["Chapter"]] = relationship(
        back_populates="subject",
        cascade="all, delete-orphan",
        order_by="Chapter.sort_order",
    )
    questions: Mapped[List["Question"]] = relationship(
        back_populates="subject",
        cascade="all, delete-orphan",
    )
    study_records: Mapped[List["StudyRecord"]] = relationship(back_populates="subject")
    wrong_questions: Mapped[List["WrongQuestion"]] = relationship(back_populates="subject")
    favorites: Mapped[List["FavoriteQuestion"]] = relationship(back_populates="subject")
    mock_exams: Mapped[List["MockExam"]] = relationship(back_populates="subject")
    papers: Mapped[List["Paper"]] = relationship(
        back_populates="subject",
        cascade="all, delete-orphan",
    )
