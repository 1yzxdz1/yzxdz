from datetime import date, timedelta
from collections import Counter, defaultdict

from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.v1.deps import CurrentUser, DBSession
from app.core.response import success_response
from app.models import Chapter, MockExam, StudyRecord, WrongQuestion
from app.schemas.statistics import StatisticsOverviewSchema

router = APIRouter(prefix="/statistics")


@router.get("/overview", summary="Placeholder statistics endpoint")
def statistics_overview(db: DBSession, current_user: CurrentUser) -> dict:
    username = current_user.username
    records = db.scalars(
        select(StudyRecord)
        .where(StudyRecord.username == username)
        .order_by(StudyRecord.practiced_at.desc())
    ).all()
    wrong_questions = db.scalars(
        select(WrongQuestion)
        .options(selectinload(WrongQuestion.question))
        .where(WrongQuestion.username == username)
    ).all()
    mock_exams = db.scalars(
        select(MockExam).where(
            MockExam.username == username,
            MockExam.status == "submitted",
        )
    ).all()
    chapters = {chapter.id: chapter for chapter in db.scalars(select(Chapter)).all()}

    total_answered = len(records)
    correct_count = sum(1 for record in records if record.is_correct)
    wrong_count = sum(1 for item in wrong_questions if not item.resolved)
    total_study_minutes = sum(record.duration_seconds for record in records) // 60

    recent_records = [
        {
            "id": record.id,
            "subject_id": record.subject_id,
            "question_id": record.question_id,
            "mode": record.mode,
            "is_correct": record.is_correct,
            "score_obtained": record.score_obtained,
            "practiced_at": record.practiced_at.isoformat(),
        }
        for record in records[:8]
    ]

    today = date.today()
    trend_map = {today - timedelta(days=offset): {"date": (today - timedelta(days=offset)).isoformat(), "answered": 0, "correct": 0} for offset in range(6, -1, -1)}
    for record in records:
        day = record.practiced_at.date()
        if day in trend_map:
            trend_map[day]["answered"] += 1
            trend_map[day]["correct"] += 1 if record.is_correct else 0
    seven_day_trend = [trend_map[day] for day in sorted(trend_map.keys())]

    chapter_stats: dict[int, dict] = defaultdict(lambda: {"total": 0, "correct": 0})
    for record in records:
        if record.chapter_id:
            chapter_stats[record.chapter_id]["total"] += 1
            chapter_stats[record.chapter_id]["correct"] += 1 if record.is_correct else 0

    chapter_accuracy = []
    knowledge_mastery = []
    for chapter_id, stats in chapter_stats.items():
        chapter = chapters.get(chapter_id)
        accuracy = round((stats["correct"] / stats["total"]) * 100, 2) if stats["total"] else 0
        chapter_accuracy.append(
            {
                "chapter_id": chapter_id,
                "chapter_title": chapter.title if chapter else f"Chapter {chapter_id}",
                "total": stats["total"],
                "correct": stats["correct"],
                "accuracy_rate": accuracy,
            }
        )
        knowledge_mastery.append(
            {
                "name": chapter.title if chapter else f"Chapter {chapter_id}",
                "value": accuracy,
            }
        )

    weak_tag_counter = Counter()
    for item in wrong_questions:
        if item.question and item.question.tags:
            weak_tag_counter.update(item.question.tags)
    weak_tags = [{"tag": tag, "count": count} for tag, count in weak_tag_counter.most_common(6)]

    data = StatisticsOverviewSchema(
        total_answered=total_answered,
        accuracy_rate=round((correct_count / total_answered) * 100, 2) if total_answered else 0,
        wrong_count=wrong_count,
        completed_mock_exams=len(mock_exams),
        total_study_minutes=total_study_minutes,
        recent_records=recent_records,
        seven_day_trend=seven_day_trend,
        chapter_accuracy=chapter_accuracy,
        knowledge_mastery=knowledge_mastery,
        weak_tags=weak_tags,
    ).model_dump()
    return success_response(data=data)
