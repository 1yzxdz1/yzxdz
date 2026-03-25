from __future__ import annotations

from pydantic import BaseModel


class StatisticsOverviewSchema(BaseModel):
    total_answered: int
    accuracy_rate: float
    wrong_count: int
    completed_mock_exams: int
    total_study_minutes: int
    recent_records: list[dict]
    seven_day_trend: list[dict]
    chapter_accuracy: list[dict]
    knowledge_mastery: list[dict]
    weak_tags: list[dict]
