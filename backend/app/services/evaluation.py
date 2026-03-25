from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import FavoriteQuestion, Question, WrongQuestion


def normalize_answers(answers: list[str] | None) -> list[str]:
    if not answers:
        return []
    normalized = [str(item).strip().upper() for item in answers if str(item).strip()]
    return sorted(normalized)


def evaluate_question(question: Question, user_answer: list[str] | None) -> dict[str, Any]:
    normalized_user = normalize_answers(user_answer)
    normalized_correct = normalize_answers(question.answer)

    if question.question_type == "short_answer":
        text = " ".join(normalized_user)
        reference = " ".join(normalized_correct)
        is_correct = bool(text) and (text == reference or text in reference or reference in text)
    else:
        is_correct = normalized_user == normalized_correct

    return {
        "normalized_user_answer": normalized_user,
        "normalized_correct_answer": normalized_correct,
        "is_correct": is_correct,
        "score_obtained": question.score if is_correct else 0,
    }


def build_question_payload(question: Question, is_favorite: bool = False) -> dict[str, Any]:
    return {
        "id": question.id,
        "subject_id": question.subject_id,
        "chapter_id": question.chapter_id,
        "chapter": question.chapter,
        "question_type": question.question_type,
        "stem": question.stem,
        "options": question.options,
        "answer": question.answer,
        "explanation": question.explanation,
        "difficulty": question.difficulty,
        "tags": question.tags or [],
        "score": question.score,
        "is_favorite": is_favorite,
    }


def is_favorite_question(db: Session, username: str, question_id: int) -> bool:
    stmt = select(FavoriteQuestion).where(
        FavoriteQuestion.username == username,
        FavoriteQuestion.question_id == question_id,
    )
    return db.scalar(stmt) is not None


def upsert_wrong_question(
    db: Session,
    username: str,
    question: Question,
    user_answer: list[str] | None,
    is_correct: bool,
) -> None:
    stmt = select(WrongQuestion).where(
        WrongQuestion.username == username,
        WrongQuestion.question_id == question.id,
    )
    wrong_record = db.scalar(stmt)

    if is_correct:
        if wrong_record:
            wrong_record.resolved = True
            wrong_record.last_user_answer = normalize_answers(user_answer)
        return

    if wrong_record:
        wrong_record.resolved = False
        wrong_record.wrong_count += 1
        wrong_record.last_user_answer = normalize_answers(user_answer)
        return

    db.add(
        WrongQuestion(
            username=username,
            subject_id=question.subject_id,
            question_id=question.id,
            last_user_answer=normalize_answers(user_answer),
            resolved=False,
            wrong_count=1,
        )
    )
