from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import Token, LoginRequest, PasswordResetRequest, PasswordChangeRequest
from app.core.auth import authenticate_user, create_access_token, get_password_reset_token
from app.config.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login_for_access_token(
    login_request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(db, login_request.username, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/password-reset")
async def reset_password_request(
    reset_request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    # 获取密码重置token
    token = await get_password_reset_token(db, reset_request.email)
    # 这里应该发送邮件，包含重置链接
    return {"message": "Password reset email sent"}