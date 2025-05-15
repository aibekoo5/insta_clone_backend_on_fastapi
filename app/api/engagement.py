from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentOut, CommentBrief
from app.services.like import like_post, unlike_post
from app.services.comment import (
    create_comment,
    get_comments_for_post,
    get_comment_replies,
    delete_comment
)
from app.services.auth import get_current_active_user
from app.models.user import User
from app.database import get_async_session

router = APIRouter(prefix="/engagement", tags=["Engagement"])

@router.post("/posts/{post_id}/like")
async def like_a_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    return await like_post(post_id, current_user.id, db)

@router.post("/posts/{post_id}/unlike")
async def unlike_a_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    return await unlike_post(post_id, current_user.id, db)



@router.post("/posts/{post_id}/comments", response_model=CommentBrief)
async def create_new_comment(
        post_id: int,
        comment_data: CommentCreate,
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    comment = await create_comment(
        post_id=post_id,
        user_id=current_user.id,
        content=comment_data.content,
        db=db
    )
    return CommentBrief.model_validate(comment, from_attributes=True)


@router.post("/comments/{comment_id}/reply", response_model=CommentBrief)
async def reply_to_comment(
        comment_id: int,
        comment_data: CommentCreate,
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    # Get parent comment to infer post_id
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    parent_comment = result.scalars().first()
    if not parent_comment:
        raise HTTPException(status_code=404, detail="Parent comment not found")

    comment = await create_comment(
        post_id=parent_comment.post_id,
        user_id=current_user.id,
        content=comment_data.content,
        parent_id=comment_id,
        db=db
    )
    return CommentBrief.model_validate(comment, from_attributes=True)



@router.get("/posts/{post_id}/comments", response_model=List[CommentOut])
async def get_post_comments(
        post_id: int,
        skip: int = 0,
        limit: int = 10,
        db: AsyncSession = Depends(get_async_session)
):
    result = await get_comments_for_post(post_id, skip, limit, db)
    comments = result["comments"]
    replies_by_parent = result["replies_by_parent"]

    # Manually construct the response
    response = []
    for comment in comments:
        comment_out = CommentOut(
            id=comment.id,
            content=comment.content,
            user_id=comment.user_id,
            post_id=comment.post_id,
            parent_id=comment.parent_id,
            created_at=comment.created_at,
            replies=[
                CommentBrief(
                    id=reply.id,
                    content=reply.content,
                    user_id=reply.user_id,
                    post_id=reply.post_id,
                    parent_id=reply.parent_id,
                    created_at=reply.created_at,
                )
                for reply in replies_by_parent.get(comment.id, [])
            ]
        )
        response.append(comment_out)

    return response



@router.get("/comments/{comment_id}/replies", response_model=Dict)
async def get_comment_replies_list(
        comment_id: int,
        skip: int = 0,
        limit: int = 5,
        db: AsyncSession = Depends(get_async_session)
):
    result = await get_comment_replies(comment_id, skip, limit, db)

    return {
        "replies": [CommentBrief.model_validate(r, from_attributes=True) for r in result["replies"]],
        "total": result["total"],
        "skip": result["skip"],
        "limit": result["limit"]
    }


@router.delete("/comments/{comment_id}")
async def delete_a_comment(
        comment_id: int,
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_async_session)
):
    if current_user.is_admin:
        return await delete_comment(comment_id, None, db)
    return await delete_comment(comment_id, current_user.id, db)
