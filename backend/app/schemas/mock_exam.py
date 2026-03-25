from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.question import QuestionSchema


class MockExamGenerateRequest(BaseModel):
    subject_id: int
    question_count: int = 10


class MockExamSubmitItem(BaseModel):
    question_id: int
    user_answer: list[str] = Field(default_factory=list)


class MockExamSubmitRequest(BaseModel):
    answers: list[MockExamSubmitItem]


class MockExamGenerateResponse(BaseModel):
    id: int
    title: str
    subject_id: int
    duration_minutes: int
    total_questions: int
    total_score: int
    questions: list[QuestionSchema]
