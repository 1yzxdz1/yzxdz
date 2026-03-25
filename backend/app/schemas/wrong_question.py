from __future__ import annotations

from pydantic import BaseModel

from app.schemas.question import QuestionSchema


class WrongQuestionItemSchema(BaseModel):
    id: int
    username: str
    subject_id: int
    question_id: int
    resolved: bool
    wrong_count: int
    last_user_answer: list[str]
    question: QuestionSchema
