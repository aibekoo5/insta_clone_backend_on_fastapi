import logging
import os
import uuid
from typing import Optional, List
from fastapi import UploadFile, HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pathlib import Path

from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate, PostOut
from app.utils.file_upload import handle_file_upload, delete_file
from app.models.like import Like

logger = logging.getLogger(__name__)


async def create_post(
        post_data: PostCreate,
        user_id: int,
        db: AsyncSession,
        image_file: Optional[UploadFile] = None,
        video_file: Optional[UploadFile] = None
) -> Post:
    """
    Create a new post with optional image and video files
    """
    try:
        # Handle image upload
        image_path = await handle_file_upload(image_file, 'image')

        # Handle video upload
        video_path = await handle_file_upload(video_file, 'video')

        # Create the post
        db_post = Post(
            caption=post_data.caption,
            image_url=image_path,
            video_url=video_path,
            is_private=post_data.is_private,
            owner_id=user_id
        )

        db.add(db_post)
        await db.commit()
        await db.refresh(db_post)
        return db_post

    except Exception as e:
        # Clean up any uploaded files if there was an error
        if image_path:
            await delete_file(image_path)
        if video_path:
            await delete_file(video_path)
        raise e


async def get_all_posts(
        current_user_id: int,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        include_private: bool = False
) -> List[PostOut]:
    query = (
        select(Post)
        .where(
            (Post.is_private == False) |
            ((Post.owner_id == current_user_id) if include_private else False)
        )
        .options(selectinload(Post.owner))
        .order_by(Post.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    posts = result.scalars().unique().all()
    # Fetch all liked post IDs for current user
    post_ids = [post.id for post in posts]
    liked_ids = set()
    if post_ids:
        like_result = await db.execute(select(Like.post_id).where(Like.post_id.in_(post_ids), Like.user_id == current_user_id))
        liked_ids = set(row[0] for row in like_result.all())
    post_outs = []
    for post in posts:
        post_dict = PostOut.model_validate(post, from_attributes=True).dict()
        post_dict["is_liked_by_current_user"] = post.id in liked_ids
        post_outs.append(PostOut(**post_dict))
    return post_outs


async def get_posts_for_user(
        user_id: int,
        current_user_id: int,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10
) -> List[PostOut]:
    """
    Get posts for a specific user that the current user is allowed to see
    """
    query = (
        select(Post)
        .where(
            Post.owner_id == user_id,
            or_(
                Post.is_private == False,
                Post.owner_id == current_user_id
            )
        )
        .options(
            selectinload(Post.owner),
            selectinload(Post.comments)
        )
        .order_by(Post.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    posts = result.scalars().unique().all()

    return [PostOut.model_validate(post, from_attributes=True) for post in posts]


async def get_post_by_id_service(
        post_id: int,
        db: AsyncSession
) -> Optional[Post]:
    """
    Get a single post by ID
    """
    result = await db.execute(
        select(Post)
        .where(Post.id == post_id)
        .options(selectinload(Post.owner))
    )
    return result.scalars().first()


async def update_post(
    post_id: int,
    post_data: PostUpdate,
    user_id: Optional[int],
    db: AsyncSession,
    new_image: Optional[UploadFile] = None,
    new_video: Optional[UploadFile] = None,
) -> Post:
    # Get the existing post
    query = select(Post).where(Post.id == post_id)
    if user_id is not None:
        query = query.where(Post.owner_id == user_id)
    result = await db.execute(query)
    db_post = result.scalars().first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    # ... update logic ...
    await db.commit()
    await db.refresh(db_post)
    # Eagerly load owner relationship
    result = await db.execute(
        select(Post).options(selectinload(Post.owner)).where(Post.id == db_post.id)
    )
    db_post_with_owner = result.scalars().first()
    return db_post_with_owner


async def delete_post(
    post_id: int,
    user_id: Optional[int],
    db: AsyncSession
) -> dict:
    # Get post from database
    result = await db.execute(
        select(Post)
        .where(Post.id == post_id)
    )
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # Verify ownership
    if user_id is not None and post.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post"
        )

    # Delete associated files from desktop
    if post.image_url:
        await delete_file(post.image_url)
    if post.video_url:
        await delete_file(post.video_url)

    # Delete post from database
    await db.delete(post)
    await db.commit()

    return {"message": "Post deleted successfully"}