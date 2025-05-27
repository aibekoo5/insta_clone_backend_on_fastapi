from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from app.models.comment import Comment
from typing import Optional

from app.models.notification import Notification
from sqlalchemy.orm import selectinload
from app.schemas.post import PostOut
from app.schemas.notification import NotificationOut
from app.schemas.reel import ReelOut
from app.schemas.comment import CommentOut
from app.schemas.user import UserOut



async def create_notification(
    user_id: int,
    sender_id: int,
    notification_type: str,
    post_id: Optional[int] = None,
    reel_id: Optional[int] = None,
    comment_id: Optional[int] = None,
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
        reel_id=reel_id,
        comment_id=comment_id
    )

    db.add(new_notification)
    await db.commit()
    await db.refresh(new_notification)
    return new_notification

async def get_user_notifications(
    user_id: int, skip: int, limit: int, db: AsyncSession
) -> list[dict]:
    result = await db.execute(
        select(Notification)
        .options(
            selectinload(Notification.sender),
            selectinload(Notification.post).selectinload(PostOut.owner), # Eager load post and its owner
            selectinload(Notification.reel).selectinload(ReelOut.owner), # Eager load reel and its owner
            selectinload(Notification.comment).selectinload(Comment.owner) # Eager load comment and its owner
        )
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    notifications = result.scalars().all()

    notifications_out = []
    for notif in notifications:
        sender_out = UserOut.from_orm(notif.sender)
        post_out = PostOut.from_orm(notif.post) if notif.post else None
        if post_out and notif.post.owner: # Ensure post owner is also converted
            post_out.owner = UserOut.from_orm(notif.post.owner)
        reel_out = ReelOut.from_orm(notif.reel) if notif.reel else None
        if reel_out and notif.reel.owner: # Ensure reel owner is also converted
            reel_out.owner = UserOut.from_orm(notif.reel.owner)
        comment_out = CommentOut.from_orm(notif.comment) if notif.comment else None
        if comment_out and notif.comment.owner: # Ensure comment owner is also converted
            comment_out.owner = UserOut.from_orm(notif.comment.owner)

        # Construct the NotificationOut object with converted Pydantic models
        notification_data = {
            "id": notif.id,
            "user_id": notif.user_id,
            "notification_type": notif.notification_type,
            "is_read": notif.is_read,
            "created_at": notif.created_at,
            "sender_id": notif.sender_id,
            "sender": sender_out,
            "post_id": notif.post_id,
            "post": post_out,
            "reel_id": notif.reel_id,
            "reel": reel_out,
            "comment_id": notif.comment_id,
            "comment": comment_out,
        }
        notifications_out.append(NotificationOut(**notification_data).model_dump())

    return notifications_out
    

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