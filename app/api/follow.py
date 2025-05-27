from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.follow import (
    follow_user,
    unfollow_user,
    get_followers,
    get_following
)
from app.services.auth import get_current_active_user
from app.models.user import User
from app.schemas.user import UserOut
from app.database import get_async_session
from sqlalchemy import select, func
from app.models.follow import Follow

router = APIRouter(prefix="/follow", tags=["Follow"])

@router.post("/{user_id}")
async def follow_a_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    return await follow_user(current_user.id, user_id, db)

@router.post("/{user_id}/unfollow")
async def unfollow_a_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    return await unfollow_user(current_user.id, user_id, db)

@router.get("/{user_id}/followers", response_model=list[UserOut])
async def get_user_followers(
    user_id: int,
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    return await get_followers(user_id, skip, limit, db, current_user_id=current_user.id)

@router.get("/{user_id}/following", response_model=list[UserOut])
async def get_user_following(
    user_id: int,
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    return await get_following(user_id, skip, limit, db, current_user_id=current_user.id)