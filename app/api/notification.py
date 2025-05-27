from fastapi import APIRouter, Depends
from app.services.notification import (
    get_user_notifications,
    mark_notification_as_read,
    mark_all_notifications_as_read,
    get_unread_notification_count
)
from app.services.auth import get_current_active_user
from app.models.user import User
from app.schemas.notification import NotificationOut
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session
from app.schemas.user import UserOut

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", response_model=list[NotificationOut])
async def get_my_notifications(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    notifications = await get_user_notifications(current_user.id, skip, limit, db)
    return [NotificationOut(**n) for n in notifications]

    
@router.post("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    return await mark_notification_as_read(notification_id, current_user.id, db)

@router.post("/read-all")
async def mark_all_as_read(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    return await mark_all_notifications_as_read(current_user.id, db)

@router.get("/unread-count")
async def get_my_unread_count(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    return await get_unread_notification_count(current_user.id, db)