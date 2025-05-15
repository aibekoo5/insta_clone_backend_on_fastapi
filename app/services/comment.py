from fastapi import HTTPException
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.models.post import Post
from app.services.notification import create_notification


async def create_comment(post_id: int, user_id: int, content: str, parent_id: int = None, db: AsyncSession = None):
    """Create a new comment or reply to a comment."""
    if db is None:
        raise ValueError("Database session is required")

    # Check if post exists
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # If it's a reply, check if parent comment exists
    if parent_id:
        result = await db.execute(select(Comment).where(Comment.id == parent_id))
        parent_comment = result.scalars().first()
        if not parent_comment:
            raise HTTPException(status_code=404, detail="Parent comment not found")

    # Create new comment
    new_comment = Comment(
        content=content,
        user_id=user_id,
        post_id=post_id,
        parent_id=parent_id
    )

    db.add(new_comment)

    # Increment comment_count on the post
    # Only increment for top-level comments (not replies)
    if parent_id is None:
        await db.execute(
            update(Post)
            .where(Post.id == post_id)
            .values(comment_count=Post.comment_count + 1)
        )

    await db.commit()
    await db.refresh(new_comment)

    if post.owner_id != user_id:
        await create_notification(
            user_id=post.owner_id,
            sender_id=user_id,
            notification_type="comment",
            post_id=post_id,
            comment_id=new_comment.id,
            db=db
        )
    # Optionally, notify parent comment owner if it's a reply and not self
    if parent_id and parent_comment.user_id != user_id:
        await create_notification(
            user_id=parent_comment.user_id,
            sender_id=user_id,
            notification_type="comment",
            post_id=post_id,
            comment_id=new_comment.id,
            db=db
        )

    return new_comment


async def get_comments_for_post(post_id: int, skip: int = 0, limit: int = 10, db: AsyncSession = None):
    """Get all top-level comments for a post with pagination."""
    if db is None:
        raise ValueError("Database session is required")

    # Get top-level comments (no parent_id)
    result = await db.execute(
        select(Comment)
        .where(Comment.post_id == post_id, Comment.parent_id == None)
        .order_by(Comment.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    comments = result.scalars().all()

    # Get comment IDs
    comment_ids = [comment.id for comment in comments]

    # Get all replies for these comments in a single query
    replies = []
    if comment_ids:
        result = await db.execute(
            select(Comment)
            .where(Comment.parent_id.in_(comment_ids))
            .order_by(Comment.created_at.asc())
        )
        replies = result.scalars().all()

    # Group replies by parent_id
    replies_by_parent = {}
    for reply in replies:
        if reply.parent_id not in replies_by_parent:
            replies_by_parent[reply.parent_id] = []
        replies_by_parent[reply.parent_id].append(reply)

    # Return both comments and their grouped replies
    return {
        "comments": comments,
        "replies_by_parent": replies_by_parent
    }


async def get_comment_replies(comment_id: int, skip: int = 0, limit: int = 10, db: AsyncSession = None):
    """Get all replies to a specific comment with pagination."""
    if db is None:
        raise ValueError("Database session is required")

    # Get replies for the specific comment
    result = await db.execute(
        select(Comment)
        .where(Comment.parent_id == comment_id)
        .order_by(Comment.created_at.asc())
        .offset(skip)
        .limit(limit)
    )
    replies = result.scalars().all()

    # Get total count
    result = await db.execute(
        select(func.count())
        .where(Comment.parent_id == comment_id)
    )
    total_count = result.scalar()

    return {
        "replies": replies,
        "total": total_count,
        "skip": skip,
        "limit": limit
    }


async def delete_comment(comment_id: int, user_id: int, db: AsyncSession = None):
    """Delete a comment if it belongs to the user."""
    if db is None:
        raise ValueError("Database session is required")

    result = await db.execute(
        select(Comment)
        .where(Comment.id == comment_id, Comment.user_id == user_id)
    )
    comment = result.scalars().first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found or you don't have permission to delete it")

    # Decrement comment_count on the post if it's a top-level comment
    if comment.parent_id is None:
        await db.execute(
            update(Post)
            .where(Post.id == comment.post_id)
            .values(comment_count=Post.comment_count - 1)
        )

    await db.delete(comment)
    await db.commit()
    return {"message": "Comment deleted successfully"}
