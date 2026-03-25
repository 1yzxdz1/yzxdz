from fastapi import APIRouter, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.v1.deps import CurrentUser, DBSession
from app.core.response import success_response
from app.models import WrongQuestion
from app.services.evaluation import build_question_payload

router = APIRouter(prefix="/wrong-questions")


@router.get("", summary="Placeholder wrong questions endpoint")
def list_wrong_questions(
    db: DBSession,
    current_user: CurrentUser,
    subject_id: int | None = Query(default=None),
    chapter_id: int | None = Query(default=None),
) -> dict:
    stmt = (
        select(WrongQuestion)
        .options(selectinload(WrongQuestion.question))
        .where(WrongQuestion.username == current_user.username)
        .order_by(WrongQuestion.updated_at.desc())
    )
    if subject_id:
        stmt = stmt.where(WrongQuestion.subject_id == subject_id)

    wrong_questions = db.scalars(stmt).all()
    if chapter_id:
        wrong_questions = [item for item in wrong_questions if item.question and item.question.chapter_id == chapter_id]

    data = [
        {
            "id": item.id,
            "username": item.username,
            "subject_id": item.subject_id,
            "question_id": item.question_id,
            "resolved": item.resolved,
            "wrong_count": item.wrong_count,
            "last_user_answer": item.last_user_answer,
            "question": build_question_payload(item.question),
        }
        for item in wrong_questions
    ]
    return success_response(data=data)
