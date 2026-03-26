from __future__ import annotations

from pydantic import BaseModel

from app.schemas.question import QuestionSchema


class PaperListSchema(BaseModel):
    id: int
    subject_id: int
    code: str
    year: int
    season: str
    title: str
    source_type: str
    description: str | None = None
    total_questions: int
    total_score: int
    duration_minutes: int


class PaperQuestionSchema(BaseModel):
    sort_order: int
    section_name: str | None = None
    score: int
    question: QuestionSchema


class PaperDetailSchema(PaperListSchema):
    questions: list[PaperQuestionSchema]
