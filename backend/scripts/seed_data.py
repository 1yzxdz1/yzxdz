from __future__ import annotations

import argparse
from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import (
    Chapter,
    FavoriteQuestion,
    MockExam,
    MockExamAnswer,
    Paper,
    PaperQuestion,
    Question,
    StudyRecord,
    Subject,
    WrongQuestion,
)
from scripts.seed_catalog import SUBJECTS_SEED
from scripts.seed_papers_catalog import PAST_PAPER_SEED


QUESTION_TYPE_ORDER = ["single_choice", "multiple_choice", "true_false", "short_answer"]


def reset_database() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def question_score(question_type: str) -> int:
    if question_type == "short_answer":
        return 5
    if question_type == "multiple_choice":
        return 3
    return 2


def paper_target_counts(total_count: int) -> dict[str, int]:
    single_count = max(7, round(total_count * 0.4))
    multiple_count = max(4, round(total_count * 0.2))
    judge_count = max(3, round(total_count * 0.2))
    short_count = max(2, total_count - single_count - multiple_count - judge_count)
    return {
        "single_choice": single_count,
        "multiple_choice": multiple_count,
        "true_false": judge_count,
        "short_answer": short_count,
    }


def select_questions_for_paper(questions: list[Question], paper_index: int, total_count: int = 18) -> list[Question]:
    grouped: dict[str, list[Question]] = {question_type: [] for question_type in QUESTION_TYPE_ORDER}
    for question in questions:
        grouped.setdefault(question.question_type, [])
        grouped[question.question_type].append(question)

    for items in grouped.values():
        items.sort(key=lambda item: (item.chapter_id or 0, item.id))

    selected: list[Question] = []
    selected_ids: set[int] = set()
    targets = paper_target_counts(total_count)

    for question_type in QUESTION_TYPE_ORDER:
        bucket = grouped.get(question_type, [])
        if not bucket:
            continue
        start = (paper_index * max(1, len(bucket) // 2)) % len(bucket)
        rotated = bucket[start:] + bucket[:start]
        for item in rotated:
            current_count = len([question for question in selected if question.question_type == question_type])
            if current_count >= targets[question_type]:
                break
            if item.id not in selected_ids:
                selected.append(item)
                selected_ids.add(item.id)

    if len(selected) < total_count:
        ordered_all = sorted(questions, key=lambda item: (item.chapter_id or 0, item.id))
        start = (paper_index * max(1, len(ordered_all) // 3)) % len(ordered_all) if ordered_all else 0
        rotated_all = ordered_all[start:] + ordered_all[:start]
        for item in rotated_all:
            if len(selected) >= total_count:
                break
            if item.id not in selected_ids:
                selected.append(item)
                selected_ids.add(item.id)

    return selected[:total_count]


def seed_subjects() -> None:
    with SessionLocal() as db:
        for subject_payload in SUBJECTS_SEED:
            subject = Subject(
                level=subject_payload["level"],
                name=subject_payload["name"],
                code=subject_payload["code"],
                exam_duration_minutes=subject_payload["exam_duration_minutes"],
                description=subject_payload["description"],
                recommended_path=subject_payload["recommended_path"],
                is_active=True,
            )
            db.add(subject)
            db.flush()

            for index, chapter_payload in enumerate(subject_payload["chapters"], start=1):
                chapter = Chapter(
                    subject_id=subject.id,
                    title=chapter_payload["title"],
                    code=chapter_payload["code"],
                    outline=chapter_payload["outline"],
                    sort_order=index,
                    estimated_minutes=chapter_payload["estimated_minutes"],
                )
                db.add(chapter)
                db.flush()

                for question_payload in chapter_payload["questions"]:
                    db.add(
                        Question(
                            subject_id=subject.id,
                            chapter_id=chapter.id,
                            chapter=chapter.title,
                            question_type=question_payload["question_type"],
                            stem=question_payload["stem"],
                            options=question_payload["options"],
                            answer=question_payload["answer"],
                            explanation=question_payload["explanation"],
                            difficulty=question_payload["difficulty"],
                            tags=question_payload["tags"],
                            score=question_score(question_payload["question_type"]),
                        )
                    )

        db.commit()


def _find_subject(db, subject_payload: dict) -> Subject | None:
    return db.query(Subject).filter(Subject.code == subject_payload["code"]).one_or_none()


def _find_chapter(db, subject_id: int, chapter_payload: dict) -> Chapter | None:
    query = db.query(Chapter).filter(Chapter.subject_id == subject_id)
    if chapter_payload.get("code"):
        return query.filter(Chapter.code == chapter_payload["code"]).one_or_none()
    return query.filter(Chapter.title == chapter_payload["title"]).one_or_none()


def _find_question(db, subject_id: int, chapter_id: int | None, question_payload: dict) -> Question | None:
    return (
        db.query(Question)
        .filter(
            Question.subject_id == subject_id,
            Question.chapter_id == chapter_id,
            Question.question_type == question_payload["question_type"],
            Question.stem == question_payload["stem"],
        )
        .one_or_none()
    )


def append_subjects() -> dict[str, int]:
    stats = {
        "subjects_created": 0,
        "subjects_updated": 0,
        "chapters_created": 0,
        "chapters_updated": 0,
        "questions_created": 0,
        "questions_updated": 0,
    }

    with SessionLocal() as db:
        for subject_payload in SUBJECTS_SEED:
            subject = _find_subject(db, subject_payload)
            if subject is None:
                subject = Subject(
                    level=subject_payload["level"],
                    name=subject_payload["name"],
                    code=subject_payload["code"],
                    exam_duration_minutes=subject_payload["exam_duration_minutes"],
                    description=subject_payload["description"],
                    recommended_path=subject_payload["recommended_path"],
                    is_active=True,
                )
                db.add(subject)
                db.flush()
                stats["subjects_created"] += 1
            else:
                subject.level = subject_payload["level"]
                subject.name = subject_payload["name"]
                subject.exam_duration_minutes = subject_payload["exam_duration_minutes"]
                subject.description = subject_payload["description"]
                subject.recommended_path = subject_payload["recommended_path"]
                subject.is_active = True
                stats["subjects_updated"] += 1

            for index, chapter_payload in enumerate(subject_payload["chapters"], start=1):
                chapter = _find_chapter(db, subject.id, chapter_payload)
                if chapter is None:
                    chapter = Chapter(
                        subject_id=subject.id,
                        title=chapter_payload["title"],
                        code=chapter_payload["code"],
                        outline=chapter_payload["outline"],
                        sort_order=index,
                        estimated_minutes=chapter_payload["estimated_minutes"],
                    )
                    db.add(chapter)
                    db.flush()
                    stats["chapters_created"] += 1
                else:
                    chapter.title = chapter_payload["title"]
                    chapter.code = chapter_payload["code"]
                    chapter.outline = chapter_payload["outline"]
                    chapter.sort_order = index
                    chapter.estimated_minutes = chapter_payload["estimated_minutes"]
                    stats["chapters_updated"] += 1

                for question_payload in chapter_payload["questions"]:
                    question = _find_question(db, subject.id, chapter.id, question_payload)
                    if question is None:
                        db.add(
                            Question(
                                subject_id=subject.id,
                                chapter_id=chapter.id,
                                chapter=chapter.title,
                                question_type=question_payload["question_type"],
                                stem=question_payload["stem"],
                                options=question_payload["options"],
                                answer=question_payload["answer"],
                                explanation=question_payload["explanation"],
                                difficulty=question_payload["difficulty"],
                                tags=question_payload["tags"],
                                score=question_score(question_payload["question_type"]),
                            )
                        )
                        stats["questions_created"] += 1
                    else:
                        question.chapter = chapter.title
                        question.options = question_payload["options"]
                        question.answer = question_payload["answer"]
                        question.explanation = question_payload["explanation"]
                        question.difficulty = question_payload["difficulty"]
                        question.tags = question_payload["tags"]
                        question.score = question_score(question_payload["question_type"])
                        stats["questions_updated"] += 1

        db.commit()

    return stats


def seed_papers() -> dict[str, int]:
    stats = {
        "papers_created": 0,
        "papers_updated": 0,
        "paper_questions_created": 0,
    }

    section_name_map = {
        "single_choice": "单选题",
        "multiple_choice": "多选题",
        "true_false": "判断题",
        "short_answer": "简答题",
    }

    with SessionLocal() as db:
        subjects = db.query(Subject).all()
        for subject in subjects:
            paper_payloads = PAST_PAPER_SEED.get(subject.code, [])
            if not paper_payloads:
                continue

            question_pool = (
                db.query(Question)
                .filter(Question.subject_id == subject.id)
                .order_by(Question.chapter_id.asc(), Question.id.asc())
                .all()
            )

            for paper_index, paper_payload in enumerate(paper_payloads):
                selected_questions = select_questions_for_paper(question_pool, paper_index=paper_index, total_count=18)
                total_score = sum(question.score for question in selected_questions)
                paper = db.query(Paper).filter(Paper.code == paper_payload["code"]).one_or_none()

                if paper is None:
                    paper = Paper(
                        subject_id=subject.id,
                        code=paper_payload["code"],
                        year=paper_payload["year"],
                        season=paper_payload["season"],
                        title=paper_payload["title"],
                        source_type="past_paper",
                        description=paper_payload["description"],
                        total_questions=len(selected_questions),
                        total_score=total_score,
                        duration_minutes=subject.exam_duration_minutes,
                    )
                    db.add(paper)
                    db.flush()
                    stats["papers_created"] += 1
                else:
                    paper.subject_id = subject.id
                    paper.year = paper_payload["year"]
                    paper.season = paper_payload["season"]
                    paper.title = paper_payload["title"]
                    paper.source_type = "past_paper"
                    paper.description = paper_payload["description"]
                    paper.total_questions = len(selected_questions)
                    paper.total_score = total_score
                    paper.duration_minutes = subject.exam_duration_minutes
                    db.query(PaperQuestion).filter(PaperQuestion.paper_id == paper.id).delete()
                    stats["papers_updated"] += 1

                for sort_order, question in enumerate(selected_questions, start=1):
                    db.add(
                        PaperQuestion(
                            paper_id=paper.id,
                            question_id=question.id,
                            sort_order=sort_order,
                            section_name=section_name_map.get(question.question_type, "综合题"),
                            score_override=question.score,
                        )
                    )
                    stats["paper_questions_created"] += 1

        db.commit()

    return stats


def print_summary(extra_stats: dict[str, int] | None = None) -> None:
    with SessionLocal() as db:
        summary = {
            "subjects": db.query(Subject).count(),
            "chapters": db.query(Chapter).count(),
            "questions": db.query(Question).count(),
            "papers": db.query(Paper).count(),
            "paper_questions": db.query(PaperQuestion).count(),
            "study_records": db.query(StudyRecord).count(),
            "wrong_questions": db.query(WrongQuestion).count(),
            "favorite_questions": db.query(FavoriteQuestion).count(),
            "mock_exams": db.query(MockExam).count(),
            "mock_exam_answers": db.query(MockExamAnswer).count(),
        }

        subject_rows = db.query(Subject).all()
        subject_breakdown = []
        for subject in subject_rows:
            chapter_count = db.query(Chapter).filter(Chapter.subject_id == subject.id).count()
            question_count = db.query(Question).filter(Question.subject_id == subject.id).count()
            paper_count = db.query(Paper).filter(Paper.subject_id == subject.id).count()
            subject_breakdown.append((subject.name, chapter_count, question_count, paper_count))

    print("Seed completed successfully.")
    print(f"Database file: {Path(settings.sqlite_db_path).resolve()}")
    for key, value in summary.items():
        print(f"{key}: {value}")
    if extra_stats:
        print("Import breakdown:")
        for key, value in extra_stats.items():
            print(f"- {key}: {value}")
    print("Subject breakdown:")
    for name, chapter_count, question_count, paper_count in subject_breakdown:
        print(f"- {name}: chapters={chapter_count}, questions={question_count}, papers={paper_count}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed NCRE review data.")
    parser.add_argument(
        "--mode",
        choices=["reset", "append"],
        default="reset",
        help="reset: rebuild database from scratch; append: incrementally import/update subjects, chapters and questions without clearing user data.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    extra_stats: dict[str, int] | None = None
    Base.metadata.create_all(bind=engine)

    if args.mode == "reset":
        reset_database()
        seed_subjects()
        extra_stats = seed_papers()
    else:
        extra_stats = append_subjects()
        extra_stats.update(seed_papers())

    print_summary(extra_stats=extra_stats)


if __name__ == "__main__":
    main()
