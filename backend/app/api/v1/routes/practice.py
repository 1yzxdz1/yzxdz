from fastapi import APIRouter

from app.api.v1.deps import CurrentUser, DBSession
from app.core.exceptions import NotFoundException
from app.core.response import success_response
from app.models import Question, StudyRecord
from app.schemas.practice import PracticeSubmitRequest, PracticeSubmitResponse
from app.services.evaluation import evaluate_question, upsert_wrong_question

router = APIRouter(prefix="/practice")


@router.post("/submit", summary="Placeholder practice submit endpoint")
def submit_practice(payload: PracticeSubmitRequest, db: DBSession, current_user: CurrentUser) -> dict:
    question = db.get(Question, payload.question_id)
    if not question:
        raise NotFoundException("Question not found")

    result = evaluate_question(question, payload.user_answer)
    db.add(
        StudyRecord(
            username=current_user.username,
            subject_id=question.subject_id,
            question_id=question.id,
            chapter_id=question.chapter_id,
            mode=payload.mode,
            user_answer=result["normalized_user_answer"],
            is_correct=result["is_correct"],
            score_obtained=result["score_obtained"],
            duration_seconds=payload.duration_seconds,
        )
    )
    upsert_wrong_question(
        db=db,
        username=current_user.username,
        question=question,
        user_answer=payload.user_answer,
        is_correct=result["is_correct"],
    )
    db.commit()

    data = PracticeSubmitResponse(
        question_id=question.id,
        is_correct=result["is_correct"],
        score_obtained=result["score_obtained"],
        correct_answer=result["normalized_correct_answer"],
        explanation=question.explanation,
    ).model_dump()
    return success_response(data=data, message="Practice submitted successfully.")
