from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class FavoriteQuestion(TimestampMixin, Base):
    __tablename__ = "favorite_questions"
    __table_args__ = (UniqueConstraint("username", "question_id", name="uq_favorite_user_question"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False, index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False, index=True)

    subject: Mapped["Subject"] = relationship(back_populates="favorites")
    question: Mapped["Question"] = relationship(back_populates="favorites")
