from __future__ import annotations

from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import Chapter, FavoriteQuestion, MockExam, MockExamAnswer, Question, StudyRecord, Subject, WrongQuestion
from scripts.seed_catalog import SUBJECTS_SEED


def reset_database() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def question_score(question_type: str) -> int:
    if question_type == "short_answer":
        return 5
    if question_type == "multiple_choice":
        return 3
    return 2


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


def print_summary() -> None:
    with SessionLocal() as db:
        summary = {
            "subjects": db.query(Subject).count(),
            "chapters": db.query(Chapter).count(),
            "questions": db.query(Question).count(),
            "study_records": db.query(StudyRecord).count(),
            "wrong_questions": db.query(WrongQuestion).count(),
            "favorite_questions": db.query(FavoriteQuestion).count(),
            "mock_exams": db.query(MockExam).count(),
            "mock_exam_answers": db.query(MockExamAnswer).count(),
        }

    print("Seed completed successfully.")
    print(f"Database file: {Path(settings.sqlite_db_path).resolve()}")
    for key, value in summary.items():
        print(f"{key}: {value}")


def main() -> None:
    reset_database()
    seed_subjects()
    print_summary()


if __name__ == "__main__":
    main()
