from fastapi import APIRouter, Query
from sqlalchemy import select

from app.api.v1.deps import CurrentUser, DBSession
from app.core.response import success_response
from app.models import Chapter
from app.schemas.chapter import ChapterSchema

router = APIRouter(prefix="/chapters")


@router.get("", summary="Placeholder chapters endpoint")
def list_chapters(db: DBSession, current_user: CurrentUser, subject_id: int | None = Query(default=None)) -> dict:
    stmt = select(Chapter).order_by(Chapter.subject_id, Chapter.sort_order)
    if subject_id:
        stmt = stmt.where(Chapter.subject_id == subject_id)
    chapters = db.scalars(stmt).all()
    data = [ChapterSchema.model_validate(chapter).model_dump() for chapter in chapters]
    return success_response(data=data)
