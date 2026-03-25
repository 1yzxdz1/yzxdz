from fastapi import APIRouter, Query
from sqlalchemy import func, select

from app.api.v1.deps import CurrentUser, DBSession
from app.core.response import success_response
from app.models import Question
from app.schemas.question import QuestionListResponse
from app.services.evaluation import build_question_payload, is_favorite_question

router = APIRouter(prefix="/questions")


@router.get("", summary="Placeholder questions endpoint")
def list_questions(
    db: DBSession,
    current_user: CurrentUser,
    subject_id: int | None = Query(default=None),
    chapter_id: int | None = Query(default=None),
    difficulty: str | None = Query(default=None),
    question_type: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
) -> dict:
    stmt = select(Question)
    count_stmt = select(func.count(Question.id))

    if subject_id:
        stmt = stmt.where(Question.subject_id == subject_id)
        count_stmt = count_stmt.where(Question.subject_id == subject_id)
    if chapter_id:
        stmt = stmt.where(Question.chapter_id == chapter_id)
        count_stmt = count_stmt.where(Question.chapter_id == chapter_id)
    if difficulty:
        stmt = stmt.where(Question.difficulty == difficulty)
        count_stmt = count_stmt.where(Question.difficulty == difficulty)
    if question_type:
        stmt = stmt.where(Question.question_type == question_type)
        count_stmt = count_stmt.where(Question.question_type == question_type)

    total = db.scalar(count_stmt) or 0
    questions = db.scalars(
        stmt.order_by(Question.id).offset((page - 1) * page_size).limit(page_size)
    ).all()

    items = [
        build_question_payload(
            question,
            is_favorite=is_favorite_question(db, current_user.username, question.id),
        )
        for question in questions
    ]
    data = QuestionListResponse(items=items, total=total).model_dump()
    return success_response(data=data)


@router.get("/random", summary="Placeholder random questions endpoint")
def random_questions(
    db: DBSession,
    current_user: CurrentUser,
    subject_id: int = Query(...),
    count: int = Query(default=10, ge=1, le=30),
    question_type: str | None = Query(default=None),
) -> dict:
    stmt = select(Question).where(Question.subject_id == subject_id)
    if question_type:
        stmt = stmt.where(Question.question_type == question_type)

    questions = db.scalars(stmt.order_by(func.random()).limit(count)).all()
    items = [
        build_question_payload(
            question,
            is_favorite=is_favorite_question(db, current_user.username, question.id),
        )
        for question in questions
    ]
    return success_response(data={"items": items, "total": len(items)})
