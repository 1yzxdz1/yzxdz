from fastapi import APIRouter, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.v1.deps import CurrentUser, DBSession
from app.core.exceptions import NotFoundException
from app.core.response import success_response
from app.models import Paper, PaperQuestion
from app.schemas.paper import PaperDetailSchema, PaperListSchema, PaperQuestionSchema
from app.services.evaluation import build_question_payload

router = APIRouter(prefix="/papers")


@router.get("", summary="List past papers")
def list_papers(
    db: DBSession,
    current_user: CurrentUser,
    subject_id: int | None = Query(default=None),
) -> dict:
    stmt = select(Paper).order_by(Paper.year.desc(), Paper.id.desc())
    if subject_id:
        stmt = stmt.where(Paper.subject_id == subject_id)

    papers = db.scalars(stmt).all()
    data = [
        PaperListSchema(
            id=paper.id,
            subject_id=paper.subject_id,
            code=paper.code,
            year=paper.year,
            season=paper.season,
            title=paper.title,
            source_type=paper.source_type,
            description=paper.description,
            total_questions=paper.total_questions,
            total_score=paper.total_score,
            duration_minutes=paper.duration_minutes,
        ).model_dump()
        for paper in papers
    ]
    return success_response(data=data)


@router.get("/{paper_id}", summary="Get past paper detail")
def get_paper_detail(paper_id: int, db: DBSession, current_user: CurrentUser) -> dict:
    paper = db.scalar(
        select(Paper)
        .where(Paper.id == paper_id)
        .options(selectinload(Paper.paper_questions).selectinload(PaperQuestion.question))
    )
    if not paper:
        raise NotFoundException("Paper not found")

    questions = []
    for item in sorted(paper.paper_questions, key=lambda value: value.sort_order):
        questions.append(
            PaperQuestionSchema(
                sort_order=item.sort_order,
                section_name=item.section_name,
                score=item.score_override or item.question.score,
                question=build_question_payload(item.question),
            ).model_dump()
        )

    data = PaperDetailSchema(
        id=paper.id,
        subject_id=paper.subject_id,
        code=paper.code,
        year=paper.year,
        season=paper.season,
        title=paper.title,
        source_type=paper.source_type,
        description=paper.description,
        total_questions=paper.total_questions,
        total_score=paper.total_score,
        duration_minutes=paper.duration_minutes,
        questions=questions,
    ).model_dump()
    return success_response(data=data)
