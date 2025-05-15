import logging
from typing import Optional, List
from fastapi import UploadFile, HTTPException, status
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate, PostOut
from app.utils.file_upload import upload_file_to_s3, delete_file_from_s3
from sqlalchemy.orm import selectinload, load_only
from sqlalchemy.future import select
from app.models.post import Post


logger = logging.getLogger(__name__)

async def create_post(
    post_data: PostCreate,
    user_id: int,
    image_file: Optional[UploadFile] = None,
    video_file: Optional[UploadFile] = None,
    db: AsyncSession = None
):
    if image_file and (not hasattr(image_file, 'filename') or not image_file.filename):
        image_file = None
    if video_file and (not hasattr(video_file, 'filename') or not video_file.filename):
        video_file = None

    image_url = None
    video_url = None

    if image_file and image_file.filename:
        if not image_file.content_type.startswith("image/"):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file for image is not an image type"
            )
        image_url = await upload_file_to_s3(image_file, "posts/images")

    if video_file and video_file.filename:
        if not video_file.content_type.startswith("video/"):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file for video is not a video type"
            )
        video_url = await upload_file_to_s3(video_file, "posts/videos")

    db_post = Post(
        caption=post_data.caption,
        image_url=image_url,
        video_url=video_url,
        is_private=post_data.is_private,
        owner_id=user_id
    )

    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)

    return db_post


async def get_all_posts(
        current_user_id: int,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        include_private: bool = False
) -> List[PostOut]:
    # Build the query with proper relationship loading
    query = (
        select(Post)
        .where(
            (Post.is_private == False) |
            ((Post.owner_id == current_user_id) if include_private else False)
        )
        .options(selectinload(Post.owner))  # Eager load the owner relationship
        .order_by(Post.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    posts = result.scalars().unique().all()

    # Convert to dict first to avoid lazy-loading issues
    return [PostOut.model_validate(post, from_attributes=True) for post in posts]


async def get_posts_for_user(
        user_id: int,
        current_user_id: int,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10
) -> List[PostOut]:

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
            selectinload(Post.owner).load_only(
                User.id, User.username, User.email, User.profile_picture,
                User.bio, User.is_active, User.created_at
            ),
            selectinload(Post.comments)
        )
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    posts = result.scalars().unique().all()

    return [PostOut.model_validate(post, from_attributes=True) for post in posts]


async def get_post_by_id_service(post_id: int, db):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    return post


async def update_post(
        post_id: int,
        post_data: PostUpdate,
        user_id: int,
        db: AsyncSession
):
    # Get the post using async SQLAlchemy 2.0 syntax
    result = await db.execute(
        select(Post)
        .where(Post.id == post_id)
        .where(Post.owner_id == user_id)
    )
    db_post = result.scalars().first()

    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Update fields
    if post_data.caption is not None:
        db_post.caption = post_data.caption
    if post_data.is_private is not None:
        db_post.is_private = post_data.is_private

    # Commit changes
    await db.commit()
    await db.refresh(db_post)

    return db_post


async def delete_post(
        post_id: int,
        user_id: int,
        db: AsyncSession
) -> dict:
    # Get post from database
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # Verify ownership
    if post.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post"
        )

    # Delete associated media
    if post.image_url:
        await delete_file_from_s3(post.image_url)
    if post.video_url:
        await delete_file_from_s3(post.video_url)

    # Delete database record
    await db.delete(post)
    await db.commit()

    return {"message": "Post deleted successfully"}