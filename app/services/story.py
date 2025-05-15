from datetime import datetime, timedelta
from fastapi import UploadFile, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.models.story import Story
from app.models.user import User
from app.models.follow import Follow
from app.database import get_async_session
from app.utils.file_upload import upload_file_to_s3

async def create_story(user_id: int, media_file: UploadFile, db: AsyncSession):
    # Upload media to storage
    media_url = await upload_file_to_s3(media_file, "stories")

    # Create story (expires in 24 hours)
    new_story = Story(
        media_url=media_url,
        owner_id=user_id,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )

    db.add(new_story)
    await db.commit()
    await db.refresh(new_story)
    return new_story

async def get_user_stories(user_id: int, db: AsyncSession):
    result = await db.execute(
        select(Story).where(
            Story.owner_id == user_id,
            Story.expires_at > datetime.utcnow()
        )
    )
    return result.scalars().all()

async def get_following_stories(current_user_id: int, db: AsyncSession):
    subquery = select(Follow.following_id).where(Follow.follower_id == current_user_id)
    result = await db.execute(
        select(Story).where(
            Story.expires_at > datetime.utcnow(),
            Story.owner_id.in_(subquery)
        )
    )
    return result.scalars().all()


async def delete_story(story_id: int, user_id: int, db: AsyncSession):
    result = await db.execute(
        select(Story).where(Story.id == story_id, Story.owner_id == user_id)
    )
    story = result.scalars().first()
    if not story:
        return {"error": "Story not found or not owned by user"}
    await db.delete(story)
    await db.commit()
    return {"message": f"Deleted story {story_id}"}