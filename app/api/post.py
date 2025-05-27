from fastapi import APIRouter, Depends, UploadFile, File, Form
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.schemas.post import PostCreate, PostUpdate, PostOut
from app.services.post import (
    create_post,
    get_posts_for_user,
    update_post, delete_post, get_all_posts, get_post_by_id_service
)
from app.services.auth import get_current_active_user, get_current_admin_user
from app.models.user import User


router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("/", response_model=PostOut)
async def create_new_post(
        caption: str = Form(...),
        is_private: bool = Form(False),
        image: Optional[UploadFile] = File(None),
        video: Optional[UploadFile] = File(None),
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    if not image and not video:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="You must provide either an image or a video."
        )
    post_data = PostCreate(caption=caption, is_private=is_private)
    return await create_post(
        post_data=post_data,
        user_id=current_user.id,
        db=db,
        image_file=image,
        video_file=video
    )


@router.get("/", response_model=List[PostOut])
async def read_all_posts(
        current_user: User = Depends(get_current_active_user),
        skip: int = 0,
        limit: int = 10,
        include_private: bool = False,
        db: AsyncSession = Depends(get_async_session)
):
    return await get_all_posts(
        current_user_id=current_user.id,
        db=db,
        skip=skip,
        limit=limit,
        include_private=include_private
    )



@router.get("/{user_id}", response_model=List[PostOut])
async def read_user_posts(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_async_session)
):
    return await get_posts_for_user(
        user_id=user_id,
        current_user_id=current_user.id,
        db=db,
        skip=skip,
        limit=limit
    )


@router.get("/post/{post_id}", response_model=PostOut)
async def get_post_by_id(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    post = await get_post_by_id_service(post_id, db)  # You need to implement this service
    if not post:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.put("/{post_id}", response_model=PostOut)
async def update_existing_post(
    post_id: int,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    if current_user.is_admin:
        return await update_post(post_id, post_data, None, db)
    return await update_post(post_id, post_data, current_user.id, db)

@router.delete("/{post_id}", response_model=dict)
async def delete_existing_post(
        post_id: int,
        current_user: User = Depends(get_current_admin_user),
        db: AsyncSession = Depends(get_async_session)
):
    if current_user.is_admin:
        return await delete_post(
            post_id=post_id,
            user_id=None,
            db=db
        )
    return await delete_post(
        post_id=post_id,
        user_id=current_user.id,
        db=db
    )