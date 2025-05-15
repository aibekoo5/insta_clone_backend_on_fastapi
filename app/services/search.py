from sqlalchemy import or_, func
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.post import Post
from app.models.follow import Follow
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


async def search_users(query: str, skip: int = 0, limit: int = 10, db: AsyncSession = None):
    users = await db.execute(
        select(User).where(
            or_(
                User.username.ilike(f"%{query}%"),
                User.full_name.ilike(f"%{query}%")
            ),
            User.is_active == True
        ).offset(skip).limit(limit)
    )
    return users.scalars().all()


async def search_posts(query: str, current_user_id: int, skip: int = 0, limit: int = 10, db: AsyncSession = None):
    posts = await db.execute(
        select(Post)
        .options(selectinload(Post.owner))
        .join(User)
        .where(
            Post.caption.ilike(f"%{query}%"),
            (Post.is_private == False) | (Post.owner_id == current_user_id) |
            (Post.owner_id.in_(
                select(Follow.following_id).where(Follow.follower_id == current_user_id)
            ))
        )
        .offset(skip).limit(limit)
    )
    return posts.scalars().all()

async def get_trending_posts(skip: int = 0, limit: int = 10, db: AsyncSession = None):
    trending_posts = await db.execute(
        select(Post)
        .options(selectinload(Post.owner))
        .order_by(Post.like_count.desc())
        .offset(skip).limit(limit)
    )
    return trending_posts.scalars().all()

async def get_recommended_users(current_user_id: int, skip: int = 0, limit: int = 5, db: AsyncSession = None):
    subquery = select(Follow.following_id).where(Follow.follower_id == current_user_id)
    recommended = await db.execute(
        select(User)
        .join(Follow, Follow.following_id == User.id)
        .where(
            Follow.follower_id.in_(subquery),
            User.id.notin_(subquery),
            User.id != current_user_id,
            User.is_active == True
        )
        .group_by(User.id)
        .order_by(func.count(Follow.follower_id).desc())
        .offset(skip).limit(limit)
    )
    return recommended.scalars().all()