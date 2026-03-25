from __future__ import annotations

from pydantic import BaseModel


class QuestionSchema(BaseModel):
    id: int
    subject_id: int
    chapter_id: int | None = None
    chapter: str
    question_type: str
    stem: str
    options: list[dict] | None = None
    answer: list[str]
    explanation: str | None = None
    difficulty: str
    tags: list[str] = []
    score: int
    is_favorite: bool = False


class QuestionListResponse(BaseModel):
    items: list[QuestionSchema]
    total: int
