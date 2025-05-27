from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate
from app.services.auth import get_current_active_user
from app.database import get_async_session
from app.models.post import Post
from app.schemas.post import PostOut, PostUpdate
from app.services.post import get_post_by_id_service, update_post, delete_post
from app.schemas.reel import ReelOut, ReelUpdate  # adjust import paths as needed
from app.models.reel import Reel
from app.services.reel import get_reel_by_id_service, update_reel
from app.schemas.story import StoryOut
from app.models.story import Story
from app.services.story import get_story_by_id_service, delete_story
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/admin", tags=["Admin User Management"])

def admin_required(current_user: User = Depends(get_current_active_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user

@router.get("/users", response_model=list[UserOut])
async def list_users(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_async_session), _: User = Depends(admin_required)):
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/users/{user_id}", response_model=UserOut)
async def get_user(user_id: int, db: AsyncSession = Depends(get_async_session), _: User = Depends(admin_required)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}", response_model=UserOut)
async def update_user(user_id: int, user_update: UserUpdate, db: AsyncSession = Depends(get_async_session), _: User = Depends(admin_required)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_async_session), _: User = Depends(admin_required)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.commit()
    return {"detail": "User deleted"}



@router.get("/posts", response_model=list[PostOut])
async def admin_list_posts(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_async_session),
    _: User = Depends(admin_required)
):
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.owner))
        .offset(skip)
        .limit(limit)
    )
    posts = result.scalars().unique().all()
    return [PostOut.model_validate(post, from_attributes=True) for post in posts]

@router.get("/posts/{post_id}", response_model=PostOut)
async def admin_get_post(post_id: int, db: AsyncSession = Depends(get_async_session), _: User = Depends(admin_required)):
    post = await get_post_by_id_service(post_id, db)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.put("/posts/{post_id}", response_model=PostOut)
async def admin_update_post(post_id: int, post_update: PostUpdate, db: AsyncSession = Depends(get_async_session), _: User = Depends(admin_required)):
    post = await update_post(post_id, post_update, None, db)
    return post

@router.delete("/posts/{post_id}")
async def admin_delete_post(post_id: int, db: AsyncSession = Depends(get_async_session), _: User = Depends(admin_required)):
    result = await delete_post(post_id, None, db)
    return result

# --- Admin Reel Management (example, adjust as needed) ---

@router.get("/reels", response_model=list[ReelOut])
async def admin_list_reels(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_async_session),
    _: User = Depends(admin_required)
):
    result = await db.execute(
        select(Reel)
        .options(selectinload(Reel.owner))
        .offset(skip)
        .limit(limit)
    )
    reels = result.scalars().unique().all()
    return [ReelOut.model_validate(reel, from_attributes=True) for reel in reels]

@router.get("/reels/{reel_id}", response_model=ReelOut)
async def admin_get_reel(reel_id: int, db: AsyncSession = Depends(get_async_session), _: User = Depends(admin_required)):
    reel = await get_reel_by_id_service(reel_id, db)
    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found")
    return reel

@router.put("/reels/{reel_id}", response_model=ReelOut)
async def admin_update_reel(reel_id: int, reel_update: ReelUpdate, db: AsyncSession = Depends(get_async_session), _: User = Depends(admin_required)):
    reel = await update_reel(reel_id, reel_update, None, db)
    # Fetch the updated reel with owner relationship loaded
    from sqlalchemy.future import select
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Reel).options(selectinload(Reel.owner)).where(Reel.id == reel.id)
    )
    reel_with_owner = result.scalars().first()
    return ReelOut.model_validate(reel_with_owner, from_attributes=True)

@router.delete("/reels/{reel_id}")
async def admin_delete_reel(reel_id: int, db: AsyncSession = Depends(get_async_session), _: User = Depends(admin_required)):
    from app.services.reel import delete_reel
    result = await delete_reel(reel_id, None, db)
    return result

# --- Admin Story Management (example, adjust as needed) ---

@router.get("/stories", response_model=list[StoryOut])
async def admin_list_stories(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_async_session), _: User = Depends(admin_required)):
    result = await db.execute(
        select(Story)
        .options(selectinload(Story.owner))
        .offset(skip)
        .limit(limit)
    )
    stories = result.scalars().unique().all()
    return [StoryOut.model_validate(story, from_attributes=True) for story in stories]

@router.get("/stories/{story_id}", response_model=StoryOut)
async def admin_get_story(story_id: int, db: AsyncSession = Depends(get_async_session), _: User = Depends(admin_required)):
    story = await get_story_by_id_service(story_id, db)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story

@router.delete("/stories/{story_id}")
async def admin_delete_story(story_id: int, db: AsyncSession = Depends(get_async_session), _: User = Depends(admin_required)):
    result = await delete_story(story_id, None, db)
    return result
