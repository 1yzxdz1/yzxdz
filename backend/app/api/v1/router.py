from fastapi import APIRouter

from app.api.v1.routes import auth, chapters, favorites, mock_exams, papers, practice, questions, statistics, subjects, wrong_questions


api_router = APIRouter()
api_router.include_router(auth.router, tags=["Auth"])
api_router.include_router(subjects.router, tags=["Subjects"])
api_router.include_router(papers.router, tags=["Past Papers"])
api_router.include_router(chapters.router, tags=["Chapters"])
api_router.include_router(questions.router, tags=["Questions"])
api_router.include_router(practice.router, tags=["Practice"])
api_router.include_router(mock_exams.router, tags=["Mock Exams"])
api_router.include_router(statistics.router, tags=["Statistics"])
api_router.include_router(wrong_questions.router, tags=["Wrong Questions"])
api_router.include_router(favorites.router, tags=["Favorites"])
