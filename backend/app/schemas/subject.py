from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SubjectListSchema(BaseModel):
    id: int
    level: str
    name: str
    code: str
    exam_duration_minutes: int
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ChapterOutlineSchema(BaseModel):
    id: int
    code: str | None = None
    title: str
    outline: str | None = None
    sort_order: int
    estimated_minutes: int

    model_config = ConfigDict(from_attributes=True)


class SubjectDetailSchema(SubjectListSchema):
    recommended_path: str | None = None
    chapters: list[ChapterOutlineSchema]
    statistics: dict
