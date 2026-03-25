from __future__ import annotations

from pydantic import BaseModel, Field


class PracticeSubmitRequest(BaseModel):
    question_id: int
    user_answer: list[str] = Field(default_factory=list)
    mode: str = "chapter_practice"
    duration_seconds: int = 0


class PracticeSubmitResponse(BaseModel):
    question_id: int
    is_correct: bool
    score_obtained: int
    correct_answer: list[str]
    explanation: str | None = None
