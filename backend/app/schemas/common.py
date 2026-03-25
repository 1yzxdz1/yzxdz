from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict


T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = "success"
    data: Optional[T] = None

    model_config = ConfigDict(from_attributes=True)


class PaginationMeta(BaseModel):
    page: int = 1
    page_size: int = 10
    total: int = 0


class PaginatedData(BaseModel):
    items: list[Any]
    meta: PaginationMeta
