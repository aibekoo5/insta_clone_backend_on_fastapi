from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.reel import Reel
from app.models.follow import Follow
from app.utils.file_upload import upload_file_to_s3

async def create_reel(user_id: int, video_file: UploadFile, caption: str = None, db: AsyncSession = None):
    # Upload video to storage
    video_url = await upload_file_to_s3(video_file, "reels")

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

    
async def get_user_reels(user_id: int, skip: int = 0, limit: int = 10, db: AsyncSession = None):
    result = await db.execute(
        select(Reel).where(Reel.owner_id == user_id).offset(skip).limit(limit)
    )
    reels = result.scalars().all()
    return reels

async def get_following_reels(current_user_id: int, skip: int = 0, limit: int = 10, db: AsyncSession = None):
    subquery = select(Follow.following_id).where(Follow.follower_id == current_user_id)
    result = await db.execute(
        select(Reel).where(Reel.owner_id.in_(subquery)).offset(skip).limit(limit)
    )
    reels = result.scalars().all()
    return reels


async def delete_reel(reel_id: int, user_id: int = None, db: AsyncSession = None):
    from fastapi import HTTPException, status
    from sqlalchemy import and_

    # Build the query: if user_id is provided, only allow deleting own reel
    if user_id is not None:
        result = await db.execute(
            select(Reel).where(and_(Reel.id == reel_id, Reel.owner_id == user_id))
        )
    else:
        # Admin can delete any reel
        result = await db.execute(
            select(Reel).where(Reel.id == reel_id)
        )
    reel = result.scalars().first()
    if not reel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reel not found or not permitted to delete")

    await db.delete(reel)
    await db.commit()
    return {"detail": "Reel deleted successfully"}
