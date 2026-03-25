from __future__ import annotations

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=50)
    nickname: str | None = Field(default=None, max_length=80)


class LoginRequest(BaseModel):
    username: str
    password: str


class UserInfoSchema(BaseModel):
    id: int
    username: str
    nickname: str | None = None


class AuthResponseSchema(BaseModel):
    token: str
    user: UserInfoSchema
