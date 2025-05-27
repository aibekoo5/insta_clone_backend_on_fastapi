import logging
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.story import Story
from app.models.follow import Follow
from app.models.story import Story
from sqlalchemy.ext.asyncio import AsyncSession

# Configure your path where files will be saved
UPLOAD_PATH = Path("static/uploads")
UPLOAD_PATH.mkdir(parents=True, exist_ok=True)
logger = logging.getLogger(__name__)


async def save_story_file(file: UploadFile) -> str:
    try:
        # Save to images subfolder for consistency
        images_path = UPLOAD_PATH / "stories"
        images_path.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        file_ext = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = images_path / unique_filename

        # Save the file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Return a URL path (not system path)
        return f"/static/uploads/stories/{unique_filename}"
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save story file: {e}"
        )


async def create_story(
        user_id: int,
        media_file: UploadFile,
        db: AsyncSession
) -> Story:
    # Validate file type
    if not media_file.content_type.startswith(("image/", "video/")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must be an image or video"
        )

    # Save file to local storage
    media_url = await save_story_file(media_file)

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


async def get_user_stories(
        user_id: int,
        db: AsyncSession
) -> list[Story]:
    """
    Get all active stories for a specific user
    """
    result = await db.execute(
        select(Story).where(
            Story.owner_id == user_id,
            Story.expires_at > datetime.utcnow()
        )
    )
    return result.scalars().all()


async def get_following_stories(
        current_user_id: int,
        db: AsyncSession
) -> list[Story]:
    """
    Get all active stories from users that the current user follows
    """
    # Get list of users that current user follows
    following_query = select(Follow.following_id).where(
        Follow.follower_id == current_user_id
    )

    result = await db.execute(
        select(Story).where(
            Story.expires_at > datetime.utcnow(),
            Story.owner_id.in_(following_query)
        ).order_by(Story.created_at.desc())
    )
    return result.scalars().all()

async def delete_story(
        story_id: int,
        user_id: int,
        db: AsyncSession
) -> dict:
    if user_id is None:
        # Admin: fetch by story_id only
        result = await db.execute(
            select(Story).where(Story.id == story_id)
        )
    else:
        # Regular user: fetch by story_id and owner_id
        result = await db.execute(
            select(Story).where(
                Story.id == story_id,
                Story.owner_id == user_id
            )
        )
    story = result.scalars().first()

    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found or not owned by user"
        )

    # Delete the media file
    if story.media_url and os.path.exists(story.media_url):
        try:
            os.remove(story.media_url)
        except OSError as e:
            logger.error(f"Failed to delete story file: {e}")

    # Delete the database record
    await db.delete(story)
    await db.commit()

    return {"message": f"Story {story_id} deleted successfully"}


async def cleanup_expired_stories(db: AsyncSession) -> int:
    """
    Clean up expired stories and their media files
    Returns number of stories deleted
    """
    # Get all expired stories
    result = await db.execute(
        select(Story).where(
            Story.expires_at <= datetime.utcnow()
        )
    )
    expired_stories = result.scalars().all()

    deleted_count = 0

    for story in expired_stories:
        # Delete the media file
        if story.media_url and os.path.exists(story.media_url):
            try:
                os.remove(story.media_url)
            except OSError as e:
                logger.error(f"Failed to delete expired story file: {e}")

        # Delete the database record
        await db.delete(story)
        deleted_count += 1

    if deleted_count > 0:
        await db.commit()

    return deleted_count


async def get_story_by_id_service(story_id: int, db: AsyncSession):
    return await db.get(Story, story_id)