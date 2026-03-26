from fastapi import APIRouter
from sqlalchemy import func, select

from app.api.v1.deps import CurrentUser, DBSession
from app.core.exceptions import NotFoundException
from app.core.response import success_response
from app.models import MockExam, Paper, Question, StudyRecord, Subject, WrongQuestion
from app.schemas.subject import ChapterOutlineSchema, PaperSummarySchema, SubjectDetailSchema, SubjectListSchema

router = APIRouter(prefix="/subjects")


@router.get("", summary="Placeholder subjects endpoint")
def list_subjects(db: DBSession, current_user: CurrentUser) -> dict:
    subjects = db.scalars(select(Subject).order_by(Subject.level, Subject.id)).all()
    data = [SubjectListSchema.model_validate(subject).model_dump() for subject in subjects]
    return success_response(data=data)


@router.get("/{subject_id}", summary="Placeholder subject detail endpoint")
def get_subject(subject_id: int, db: DBSession, current_user: CurrentUser) -> dict:
    subject = db.get(Subject, subject_id)
    if not subject:
        raise NotFoundException("Subject not found")

    username = current_user.username
    total_questions = db.scalar(select(func.count(Question.id)).where(Question.subject_id == subject_id)) or 0
    total_records = (
        db.scalar(
            select(func.count(StudyRecord.id)).where(
                StudyRecord.subject_id == subject_id,
                StudyRecord.username == username,
            )
        )
        or 0
    )
    correct_records = (
        db.scalar(
            select(func.count(StudyRecord.id)).where(
                StudyRecord.subject_id == subject_id,
                StudyRecord.username == username,
                StudyRecord.is_correct.is_(True),
            )
        )
        or 0
    )
    wrong_count = (
        db.scalar(
            select(func.count(WrongQuestion.id)).where(
                WrongQuestion.subject_id == subject_id,
                WrongQuestion.username == username,
            )
        )
        or 0
    )
    completed_mock_exams = (
        db.scalar(
            select(func.count(MockExam.id)).where(
                MockExam.subject_id == subject_id,
                MockExam.username == username,
                MockExam.status == "submitted",
            )
        )
        or 0
    )
    statistics = {
        "total_questions": total_questions,
        "total_answered": total_records,
        "accuracy_rate": round((correct_records / total_records) * 100, 2) if total_records else 0,
        "wrong_count": wrong_count,
        "completed_mock_exams": completed_mock_exams,
    }
    papers = db.scalars(
        select(Paper)
        .where(Paper.subject_id == subject_id)
        .order_by(Paper.year.desc(), Paper.id.desc())
    ).all()

    data = SubjectDetailSchema(
        id=subject.id,
        level=subject.level,
        name=subject.name,
        code=subject.code,
        exam_duration_minutes=subject.exam_duration_minutes,
        description=subject.description,
        recommended_path=subject.recommended_path,
        chapters=[ChapterOutlineSchema.model_validate(chapter) for chapter in subject.chapters],
        statistics=statistics,
        papers=[PaperSummarySchema.model_validate(paper) for paper in papers],
    ).model_dump()
    return success_response(data=data)
