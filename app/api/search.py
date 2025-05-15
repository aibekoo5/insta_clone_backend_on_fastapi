from fastapi import APIRouter, Depends
from app.services.search import (
    search_users,
    search_posts,
    get_trending_posts,
    get_recommended_users
)
from app.services.auth import get_current_active_user
from app.models.user import User
from app.schemas.user import UserOut
from app.schemas.post import PostOut
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/users", response_model=list[UserOut])
async def search_users_by_query(
    query: str,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_async_session)
):
    return await search_users(query, skip, limit, db)

@router.get("/posts", response_model=list[PostOut])
async def search_posts_by_query(
    query: str,
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_async_session)
):
    return await search_posts(query, current_user.id, skip, limit, db)

@router.get("/trending", response_model=list[PostOut])
async def get_trending_posts_list(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_async_session)
):
    return await get_trending_posts(skip, limit, db)

@router.get("/recommended-users", response_model=list[UserOut])
async def get_recommended_users_list(
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 5,
    db: AsyncSession = Depends(get_async_session)
):
    return await get_recommended_users(current_user.id, skip, limit, db)