from fastapi import APIRouter, Depends, Response
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Body

from app.database import get_async_session
from app.schemas.user import UserCreate, UserOut, Token, LoginRequest
from app.services.auth import (authenticate_user, create_access_token, register_user)
from fastapi import HTTPException
from app.utils.password_reset import create_password_reset_token, send_password_reset_email
from app.schemas.user import PasswordResetRequest, PasswordResetConfirm
from app.models.user import User
from passlib.context import CryptContext
from sqlalchemy import select
from jose import JWTError, jwt
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register", response_model=UserOut)
async def register(user: UserCreate, db: AsyncSession = Depends(get_async_session)):
    return await register_user(user, db)


@router.post("/login", response_model=Token)
async def login(
    response: Response,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_async_session)
):
    user = await authenticate_user(login_data.email, login_data.password, db)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=True
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh")
async def refresh_token(
    refresh_token: str = Body(..., embed=True)
):
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired refresh token")

    # Optionally, you can check if the user still exists or if the refresh token is blacklisted, etc.
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": email},
        expires_delta=access_token_expires
    )

    # If you want to rotate refresh tokens, generate a new one here
    # For now, we return the same refresh token
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}



@router.post("/forgot-password/request")
async def request_password_reset(
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_async_session)
):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalars().first()
    if not user:
        # For security, don't reveal if user exists
        return {"message": "If the email exists, a reset link has been sent."}
    token = await create_password_reset_token(user.email)
    await send_password_reset_email(user.email, token)
    return {"message": "If the email exists, a reset link has been sent."}

@router.post("/reset-password/confirm")
async def confirm_password_reset(
    data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        payload = jwt.decode(data.token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = pwd_context.hash(data.new_password)
    await db.commit()
    await db.refresh(user)
    return {"message": "Password reset successful"}