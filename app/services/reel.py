import logging
import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.reel import Reel
from app.models.follow import Follow
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.schemas.reel import ReelOut
from app.schemas.user import UserOut

# Configure your path where files will be saved
UPLOAD_PATH = Path("static/uploads")
UPLOAD_PATH.mkdir(parents=True, exist_ok=True)
logger = logging.getLogger(__name__)


async def save_reel_video(file: UploadFile) -> str:
    try:
        # Create reels subfolder
        reels_path = UPLOAD_PATH / "reels"
        reels_path.mkdir(parents=True, exist_ok=True)

        # Validate file type
        if not file.content_type.startswith("video/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file must be a video"
            )

        # Generate unique filename
        file_ext = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = reels_path / unique_filename

        # Save the file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Return a URL path (not system path)
        return f"/static/uploads/reels/{unique_filename}"
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save reel video: {e}"
        )


async def create_reel(
        user_id: int,
        video_file: UploadFile,
        caption: Optional[str] = None,
        db: AsyncSession = None
) -> Reel:
    # Save video to local storage
    video_url = await save_reel_video(video_file)

    # Create reel
    new_reel = Reel(
        video_url=video_url,
        caption=caption,
        owner_id=user_id
    )

    db.add(new_reel)
    await db.commit()
    await db.refresh(new_reel)
    return new_reel


async def get_user_reels(
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        db: AsyncSession = None
) -> list[ReelOut]:
    result = await db.execute(
        select(Reel)
        .options(selectinload(Reel.owner))
        .where(Reel.owner_id == user_id)
        .order_by(Reel.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    reels = result.scalars().all()
    return [ReelOut(
        **reel.__dict__,
        owner=UserOut.from_orm(reel.owner)
    ) for reel in reels]


async def get_following_reels(
        current_user_id: int,
        skip: int = 0,
        limit: int = 10,
        db: AsyncSession = None
) -> list[ReelOut]:
    following_query = select(Follow.following_id).where(
        Follow.follower_id == current_user_id
    )
    result = await db.execute(
        select(Reel)
        .options(selectinload(Reel.owner))
        .where(Reel.owner_id.in_(following_query))
        .order_by(Reel.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    reels = result.scalars().all()
    return [ReelOut(
        **reel.__dict__,
        owner=UserOut.from_orm(reel.owner)
    ) for reel in reels]


async def get_all_reels(skip, limit, db):
    result = await db.execute(
        select(Reel).options(selectinload(Reel.owner)).offset(skip).limit(limit)
    )
    reels = result.scalars().all()
    return [ReelOut(
        **reel.__dict__,
        owner=UserOut.from_orm(reel.owner)
    ) for reel in reels]

async def update_reel(
    reel_id: int,
    reel_update,
    user_id: Optional[int],
    db: AsyncSession,
    new_video: Optional[UploadFile] = None
):
    # Build the query
    from app.models.reel import Reel
    from app.schemas.reel import ReelUpdate

    if user_id is not None:
        query = select(Reel).where(Reel.id == reel_id, Reel.owner_id == user_id)
    else:
        query = select(Reel).where(Reel.id == reel_id)

    result = await db.execute(query)
    reel = result.scalars().first()

    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found or not permitted to update")

    # Update fields
    if hasattr(reel_update, "caption") and reel_update.caption is not None:
        reel.caption = reel_update.caption

    # Handle video update
    if new_video and new_video.filename:
        # Delete old video if exists
        if reel.video_url and os.path.exists(reel.video_url):
            try:
                os.remove(reel.video_url)
            except OSError as e:
                logger.error(f"Failed to delete old reel video: {e}")
        # Save new video
        reel.video_url = await save_reel_video(new_video)

    await db.commit()
    await db.refresh(reel)
    return reel


async def delete_reel(
        reel_id: int,
        user_id: Optional[int] = None,
        db: AsyncSession = None
) -> dict:
    # Build the query
    if user_id is not None:
        query = select(Reel).where(and_(
            Reel.id == reel_id,
            Reel.owner_id == user_id
        ))
    else:
        query = select(Reel).where(Reel.id == reel_id)

    result = await db.execute(query)
    reel = result.scalars().first()

    if not reel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reel not found or not permitted to delete"
        )

    # Delete the video file
    if reel.video_url and os.path.exists(reel.video_url):
        try:
            os.remove(reel.video_url)
        except OSError as e:
            logger.error(f"Failed to delete reel video: {e}")

    # Delete the database record
    await db.delete(reel)
    await db.commit()

    return {"detail": "Reel deleted successfully"}


async def get_reel_by_id_service(reel_id: int, db: AsyncSession):
    return await db.get(Reel, reel_id)