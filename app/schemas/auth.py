from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class PasswordResetRequest(BaseModel):
    email: str


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str