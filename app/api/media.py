from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.story import (
    create_story,
    get_user_stories,
    get_following_stories,
    delete_story
)
from app.services.reel import (
    create_reel,
    get_user_reels,
    get_following_reels
)
from app.services.auth import get_current_active_user
from app.models.user import User
from app.database import get_async_session
from app.services.reel import delete_reel
from fastapi import Form
from app.schemas.reel import ReelUpdate
from app.services.reel import update_reel
from app.services.reel import get_all_reels

router = APIRouter(prefix="/media", tags=["Media"])

@router.post("/stories")
async def upload_story(
    media: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    return await create_story(current_user.id, media, db)

@router.get("/stories/me")
async def get_my_stories(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    return await get_user_stories(current_user.id, db)

@router.get("/stories/following")
async def get_stories_from_following(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    return await get_following_stories(current_user.id, db)


@router.delete("/stories/{story_id}")
async def remove_story(
    story_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    if current_user.is_admin:
        return await delete_story(story_id, None, db)
    return await delete_story(story_id, current_user.id, db)


@router.post("/reels")
async def upload_reel(
    video: UploadFile = File(...),
    caption: str = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    return await create_reel(current_user.id, video, caption, db)


@router.get("/reels/following")
async def get_reels_from_following(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    return await get_following_reels(current_user.id, skip, limit, db)

@router.get("/reels/{user_id}")
async def get_user_reels_endpoint(
    user_id: int,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_async_session)
):
    return await get_user_reels(user_id, skip, limit, db)

@router.get("/reels")
async def get_all_reels_endpoint(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_async_session)
):
    return await get_all_reels(skip, limit, db)

@router.put("/reels/{reel_id}")
async def update_reel_endpoint(
    reel_id: int,
    caption: str = Form(None),
    video: UploadFile = File(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    reel_update = ReelUpdate(caption=caption)
    # Only allow owner or admin to update
    user_id = None if current_user.is_admin else current_user.id
    return await update_reel(reel_id, reel_update, user_id, db, new_video=video)


@router.delete("/reels/{reel_id}")
async def delete_reel_(
    reel_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    if current_user.is_admin:
        return await delete_reel(reel_id, None, db)
    from app.services.reel import delete_reel as service_delete_reel
    return await service_delete_reel(reel_id, current_user.id, db)