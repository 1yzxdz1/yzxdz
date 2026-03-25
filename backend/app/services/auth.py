from __future__ import annotations

from datetime import datetime, timedelta
import hashlib
import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestException
from app.models import AuthToken, User


TOKEN_TTL_DAYS = 7


def hash_password(password: str, salt: str | None = None) -> str:
    actual_salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        actual_salt.encode("utf-8"),
        100_000,
    ).hex()
    return f"{actual_salt}${digest}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        salt, stored_digest = password_hash.split("$", 1)
    except ValueError:
        return False
    computed_hash = hash_password(password, salt)
    return secrets.compare_digest(computed_hash, f"{salt}${stored_digest}")


def create_user(db: Session, username: str, password: str, nickname: str | None = None) -> User:
    existing = db.scalar(select(User).where(User.username == username))
    if existing:
        raise BadRequestException("Username already exists")

    user = User(
        username=username,
        password_hash=hash_password(password),
        nickname=nickname or username,
    )
    db.add(user)
    db.flush()
    return user


def create_token(db: Session, user: User) -> AuthToken:
    token = AuthToken(
        user_id=user.id,
        token=secrets.token_urlsafe(32),
        expires_at=datetime.utcnow() + timedelta(days=TOKEN_TTL_DAYS),
    )
    db.add(token)
    db.flush()
    return token


def get_user_by_token(db: Session, token: str) -> User | None:
    stmt = (
        select(AuthToken)
        .where(
            AuthToken.token == token,
            AuthToken.expires_at > datetime.utcnow(),
        )
    )
    token_record = db.scalar(stmt)
    if not token_record:
        return None
    return token_record.user
