from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.follow import Follow
from app.models.user import User
from app.services.notification import create_notification

async def follow_user(follower_id: int, following_id: int, db: AsyncSession):
    follower = await db.get(User, follower_id)
    following = await db.get(User, following_id)

    if not follower or not following:
        raise HTTPException(status_code=404, detail="User not found")

    if follower_id == following_id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    existing_follow = await db.execute(
        select(Follow).where(
            Follow.follower_id == follower_id,
            Follow.following_id == following_id
        )
    )
    if existing_follow.scalars().first():
        raise HTTPException(status_code=400, detail="Already following this user")

    new_follow = Follow(follower_id=follower_id, following_id=following_id)
    db.add(new_follow)
    await db.commit()

    await create_notification(
        user_id=following_id,
        sender_id=follower_id,
        notification_type="follow",
        db=db
    )

    return {"message": f"Now following user {following_id}"}

async def unfollow_user(follower_id: int, following_id: int, db: AsyncSession):
    result = await db.execute(
        select(Follow).where(
            Follow.follower_id == follower_id,
            Follow.following_id == following_id
        )
    )
    follow = result.scalars().first()
    if not follow:
        raise HTTPException(status_code=404, detail="Follow relationship not found")

    await db.delete(follow)
    await db.commit()
    return {"message": f"Unfollowed user {following_id}"}

async def get_followers(user_id: int, skip: int = 0, limit: int = 10, db: AsyncSession = None):
    result = await db.execute(
        select(User).join(Follow, Follow.follower_id == User.id)
        .where(Follow.following_id == user_id)
        .offset(skip).limit(limit)
    )
    return result.scalars().all()

async def get_following(user_id: int, skip: int = 0, limit: int = 10, db: AsyncSession = None):
    result = await db.execute(
        select(User).join(Follow, Follow.following_id == User.id)
        .where(Follow.follower_id == user_id)
        .offset(skip).limit(limit)
    )
    return result.scalars().all()