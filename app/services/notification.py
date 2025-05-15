from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from app.models.comment import Comment

from app.models.notification import Notification
from sqlalchemy.orm import selectinload

async def create_notification(
    user_id: int,
    sender_id: int,
    notification_type: str,
    post_id: int = None,
    comment_id: int = None,
    db: AsyncSession = None
):
    valid_types = ['like', 'comment', 'follow']
    if notification_type not in valid_types:
        raise HTTPException(status_code=400, detail="Invalid notification type")

    new_notification = Notification(
        user_id=user_id,
        sender_id=sender_id,
        notification_type=notification_type,
        post_id=post_id,
        comment_id=comment_id
    )

    db.add(new_notification)
    await db.commit()
    await db.refresh(new_notification)
    return new_notification

async def get_user_notifications(user_id: int, skip: int = 0, limit: int = 10, db: AsyncSession = None):
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user_id)
        .options(
            selectinload(Notification.sender),
            selectinload(Notification.post),
            selectinload(Notification.comment).selectinload(Comment.replies)
        )
        .order_by(Notification.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    notifications = result.scalars().all()
    return notifications

async def mark_notification_as_read(notification_id: int, user_id: int, db: AsyncSession = None):
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id)
    )
    notification = result.scalars().first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    await db.commit()
    await db.refresh(notification)
    return notification

async def mark_all_notifications_as_read(user_id: int, db: AsyncSession = None):
    result = await db.execute(
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read == False)
        .values(is_read=True)
        .execution_options(synchronize_session="fetch")
    )
    await db.commit()
    return {"message": f"Marked {result.rowcount} notifications as read"}

async def get_unread_notification_count(user_id: int, db: AsyncSession = None):
    result = await db.execute(
        select(func.count()).select_from(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False
        )
    )
    count = result.scalar()
    return {"unread_count": count}