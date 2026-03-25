from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ChapterSchema(BaseModel):
    id: int
    subject_id: int
    code: str | None = None
    title: str
    outline: str | None = None
    sort_order: int
    estimated_minutes: int

    model_config = ConfigDict(from_attributes=True)
