from fastapi import APIRouter
from sqlalchemy import select

from app.api.v1.deps import CurrentUser, DBSession
from app.core.exceptions import NotFoundException
from app.core.response import success_response
from app.models import FavoriteQuestion, Question
from app.schemas.favorite import FavoriteCreateRequest

router = APIRouter(prefix="/favorites")


@router.post("", summary="Placeholder favorite create endpoint")
def create_favorite(payload: FavoriteCreateRequest, db: DBSession, current_user: CurrentUser) -> dict:
    question = db.get(Question, payload.question_id)
    if not question:
        raise NotFoundException("Question not found")

    existing = db.scalar(
        select(FavoriteQuestion).where(
            FavoriteQuestion.username == current_user.username,
            FavoriteQuestion.question_id == payload.question_id,
        )
    )
    if existing:
        return success_response(data={"question_id": payload.question_id}, message="Question already favorited.")

    db.add(
        FavoriteQuestion(
            username=current_user.username,
            subject_id=question.subject_id,
            question_id=question.id,
        )
    )
    db.commit()
    return success_response(data={"question_id": payload.question_id}, message="Favorite created successfully.")


@router.delete("/{question_id}", summary="Placeholder favorite delete endpoint")
def delete_favorite(question_id: int, db: DBSession, current_user: CurrentUser) -> dict:
    favorite = db.scalar(
        select(FavoriteQuestion).where(
            FavoriteQuestion.username == current_user.username,
            FavoriteQuestion.question_id == question_id,
        )
    )
    if not favorite:
        raise NotFoundException("Favorite not found")

    db.delete(favorite)
    db.commit()
    return success_response(data={"question_id": question_id}, message="Favorite deleted successfully.")
