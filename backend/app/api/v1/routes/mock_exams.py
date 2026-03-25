from datetime import datetime

from fastapi import APIRouter
from sqlalchemy import func, select

from app.api.v1.deps import CurrentUser, DBSession
from app.core.exceptions import BadRequestException, NotFoundException
from app.core.response import success_response
from app.models import MockExam, MockExamAnswer, Question, StudyRecord, Subject
from app.schemas.mock_exam import MockExamGenerateRequest, MockExamGenerateResponse, MockExamSubmitRequest
from app.services.evaluation import build_question_payload, evaluate_question, upsert_wrong_question

router = APIRouter(prefix="/mock-exams")


@router.post("/generate", summary="Placeholder mock exam generate endpoint")
def generate_mock_exam(payload: MockExamGenerateRequest, db: DBSession, current_user: CurrentUser) -> dict:
    subject = db.get(Subject, payload.subject_id)
    if not subject:
        raise NotFoundException("Subject not found")

    questions = db.scalars(
        select(Question)
        .where(Question.subject_id == payload.subject_id)
        .order_by(func.random())
        .limit(payload.question_count)
    ).all()
    if not questions:
        raise BadRequestException("No questions available for this subject")

    mock_exam = MockExam(
        username=current_user.username,
        subject_id=subject.id,
        title=f"{subject.name} 模拟卷 {datetime.now().strftime('%Y%m%d%H%M%S')}",
        total_questions=len(questions),
        total_score=sum(question.score for question in questions),
        duration_minutes=subject.exam_duration_minutes,
        status="generated",
    )
    db.add(mock_exam)
    db.flush()

    for question in questions:
        db.add(
            MockExamAnswer(
                mock_exam_id=mock_exam.id,
                question_id=question.id,
                explanation_snapshot=question.explanation,
            )
        )

    db.commit()

    data = MockExamGenerateResponse(
        id=mock_exam.id,
        title=mock_exam.title,
        subject_id=mock_exam.subject_id,
        duration_minutes=mock_exam.duration_minutes,
        total_questions=mock_exam.total_questions,
        total_score=mock_exam.total_score,
        questions=[build_question_payload(question) for question in questions],
    ).model_dump()
    return success_response(data=data, message="Mock exam generated successfully.")


@router.post("/{mock_exam_id}/submit", summary="Placeholder mock exam submit endpoint")
def submit_mock_exam(mock_exam_id: int, payload: MockExamSubmitRequest, db: DBSession, current_user: CurrentUser) -> dict:
    mock_exam = db.get(MockExam, mock_exam_id)
    if not mock_exam:
        raise NotFoundException("Mock exam not found")
    if mock_exam.username != current_user.username:
        raise NotFoundException("Mock exam not found")
    if mock_exam.status == "submitted":
        raise BadRequestException("Mock exam already submitted")

    answer_map = {item.question_id: item.user_answer for item in payload.answers}
    mock_answers = db.scalars(
        select(MockExamAnswer).where(MockExamAnswer.mock_exam_id == mock_exam_id).order_by(MockExamAnswer.id)
    ).all()

    total_score = 0
    correct_count = 0
    answer_details = []

    for mock_answer in mock_answers:
        question = db.get(Question, mock_answer.question_id)
        user_answer = answer_map.get(mock_answer.question_id, [])
        result = evaluate_question(question, user_answer)

        mock_answer.user_answer = result["normalized_user_answer"]
        mock_answer.is_correct = result["is_correct"]
        mock_answer.obtained_score = result["score_obtained"]

        db.add(
            StudyRecord(
                username=current_user.username,
                subject_id=question.subject_id,
                question_id=question.id,
                chapter_id=question.chapter_id,
                mode="mock_exam",
                user_answer=result["normalized_user_answer"],
                is_correct=result["is_correct"],
                score_obtained=result["score_obtained"],
                duration_seconds=0,
            )
        )
        upsert_wrong_question(
            db=db,
            username=current_user.username,
            question=question,
            user_answer=user_answer,
            is_correct=result["is_correct"],
        )

        total_score += result["score_obtained"]
        if result["is_correct"]:
            correct_count += 1

        answer_details.append(
            {
                "question_id": question.id,
                "is_correct": result["is_correct"],
                "score_obtained": result["score_obtained"],
                "correct_answer": result["normalized_correct_answer"],
                "explanation": question.explanation,
            }
        )

    mock_exam.obtained_score = total_score
    mock_exam.correct_count = correct_count
    mock_exam.submitted_at = datetime.now()
    mock_exam.status = "submitted"
    db.commit()

    data = {
        "id": mock_exam.id,
        "subject_id": mock_exam.subject_id,
        "title": mock_exam.title,
        "total_questions": mock_exam.total_questions,
        "correct_count": correct_count,
        "total_score": mock_exam.total_score,
        "obtained_score": total_score,
        "accuracy_rate": round((correct_count / mock_exam.total_questions) * 100, 2) if mock_exam.total_questions else 0,
        "answers": answer_details,
    }
    return success_response(data=data, message="Mock exam submitted successfully.")
