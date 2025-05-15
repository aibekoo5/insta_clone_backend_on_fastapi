from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.like import Like
from app.models.post import Post
from app.services.notification import create_notification

async def like_post(post_id: int, user_id: int, db: AsyncSession):
    # Check if post exists
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Check if user already liked the post
    result = await db.execute(
        select(Like).where(Like.post_id == post_id, Like.user_id == user_id)
    )
    existing_like = result.scalars().first()

    if existing_like:
        raise HTTPException(status_code=400, detail="Post already liked")

    # Create new like
    new_like = Like(post_id=post_id, user_id=user_id)
    db.add(new_like)

    # Update post like count
    result = await db.execute(select(Like).where(Like.post_id == post_id))
    post.like_count = len(result.scalars().all())

    if post.owner_id != user_id:
        await create_notification(
            user_id=post.owner_id,
            sender_id=user_id,
            notification_type="like",
            post_id=post_id,
            db=db
        )

    await db.commit()

    return {"message": "Post liked successfully"}

async def unlike_post(post_id: int, user_id: int, db: AsyncSession):
    # Check if like exists
    result = await db.execute(
        select(Like).where(Like.post_id == post_id, Like.user_id == user_id)
    )
    like = result.scalars().first()

    if not like:
        raise HTTPException(status_code=404, detail="Like not found")

    await db.delete(like)

    # Update post like count
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    if post:
        result = await db.execute(select(Like).where(Like.post_id == post_id))
        post.like_count = len(result.scalars().all())

    await db.commit()

    return {"message": "Post unliked successfully"}