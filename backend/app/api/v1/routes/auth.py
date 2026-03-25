from fastapi import APIRouter, Depends
from sqlalchemy import delete, select

from app.api.v1.deps import CurrentUser, DBSession, security
from app.core.response import success_response
from app.models import AuthToken, User
from app.schemas.auth import AuthResponseSchema, LoginRequest, RegisterRequest, UserInfoSchema
from app.services.auth import create_token, create_user, verify_password

router = APIRouter(prefix="/auth")


@router.post("/register", summary="Register a new user")
def register(payload: RegisterRequest, db: DBSession) -> dict:
    user = create_user(db, payload.username, payload.password, payload.nickname)
    token = create_token(db, user)
    db.commit()
    db.refresh(user)
    data = AuthResponseSchema(
        token=token.token,
        user=UserInfoSchema(id=user.id, username=user.username, nickname=user.nickname),
    ).model_dump()
    return success_response(data=data, message="Register successfully.")


@router.post("/login", summary="Login")
def login(payload: LoginRequest, db: DBSession) -> dict:
    user = db.scalar(select(User).where(User.username == payload.username))
    if not user or not verify_password(payload.password, user.password_hash):
        return {"code": 400, "message": "Invalid username or password", "data": None}

    token = create_token(db, user)
    db.commit()
    data = AuthResponseSchema(
        token=token.token,
        user=UserInfoSchema(id=user.id, username=user.username, nickname=user.nickname),
    ).model_dump()
    return success_response(data=data, message="Login successfully.")


@router.get("/me", summary="Current user")
def me(current_user: CurrentUser) -> dict:
    user = current_user
    data = UserInfoSchema(id=user.id, username=user.username, nickname=user.nickname).model_dump()
    return success_response(data=data)


@router.post("/logout", summary="Logout")
def logout(db: DBSession, current_user: CurrentUser, credentials=Depends(security)) -> dict:
    db.execute(delete(AuthToken).where(AuthToken.token == credentials.credentials))
    db.commit()
    return success_response(data=None, message="Logout successfully.")
