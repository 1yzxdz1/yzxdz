from __future__ import annotations

from pydantic import BaseModel


class FavoriteCreateRequest(BaseModel):
    question_id: int
