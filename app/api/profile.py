from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate
from app.services.auth import get_current_active_user
from app.database import get_async_session
from passlib.context import CryptContext
from app.utils.file_upload import upload_file_to_s3
from fastapi import Body

router = APIRouter(prefix="/profile", tags=["Profile"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/me", response_model=UserOut)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user)
):
    return current_user

@router.put("/me", response_model=UserOut)
async def edit_my_profile(
    username: str = Form(None),
    email: str = Form(None),
    full_name: str = Form(None),
    bio: str = Form(None),
    profile_picture: UploadFile = File(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    # Update text fields
    if username is not None:
        current_user.username = username
    if email is not None:
        current_user.email = email
    if full_name is not None:
        current_user.full_name = full_name
    if bio is not None:
        current_user.bio = bio
    # Handle profile picture upload
    if profile_picture is not None:
        url = await upload_file_to_s3(profile_picture, "profile_pictures")
        current_user.profile_picture = url
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.put("/change-password")
async def change_password(
    old_password: str = Body(...),
    new_password: str = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    # Verify old password
    if not pwd_context.verify(old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    # Hash new password and update
    current_user.hashed_password = pwd_context.hash(new_password)
    await db.commit()
    await db.refresh(current_user)
    return {"detail": "Password changed successfully"}