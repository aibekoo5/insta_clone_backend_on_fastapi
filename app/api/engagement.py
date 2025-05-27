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
    delete_comment,
    create_reel_comment,
    reply_to_reel_comment,
    get_comments_for_reel,
    get_reel_comment_replies,
    delete_reel_comment
)
from app.services.auth import get_current_active_user
from app.models.user import User
from app.database import get_async_session
from app.services.like import like_reel, unlike_reel

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

@router.post("/reels/{reel_id}/like")
async def like_a_reel(
    reel_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    return await like_reel(reel_id, current_user.id, db)

@router.post("/reels/{reel_id}/unlike")
async def unlike_a_reel(
    reel_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    return await unlike_reel(reel_id, current_user.id, db)

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
    response = []
    for comment in comments:
        # Fetch owner for top-level comment
        owner_result = await db.execute(select(User).where(User.id == comment.user_id))
        owner = owner_result.scalars().first()
        comment_out = CommentOut(
            id=comment.id,
            content=comment.content,
            user_id=comment.user_id,
            post_id=comment.post_id,
            parent_id=comment.parent_id,
            created_at=comment.created_at,
            owner=owner,  # Add this line
            replies=[
                CommentBrief(
                    id=reply.id,
                    content=reply.content,
                    user_id=reply.user_id,
                    post_id=reply.post_id,
                    parent_id=reply.parent_id,
                    created_at=reply.created_at,
                    owner=(await db.execute(select(User).where(User.id == reply.user_id))).scalars().first()  # Add owner for reply
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


@router.post("/reels/{reel_id}/comments", response_model=CommentBrief)
async def create_new_reel_comment(
    reel_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    comment = await create_reel_comment(
        reel_id=reel_id,
        user_id=current_user.id,
        content=comment_data.content,
        db=db
    )
    return CommentBrief.model_validate(comment, from_attributes=True)

@router.post("/reels/{reel_id}/comments/{comment_id}/reply", response_model=CommentBrief)
async def reply_to_reel_comment_endpoint(
    reel_id: int,
    comment_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    comment = await reply_to_reel_comment(
        reel_id=reel_id,
        parent_id=comment_id,
        user_id=current_user.id,
        content=comment_data.content,
        db=db
    )
    return CommentBrief.model_validate(comment, from_attributes=True)

@router.get("/reels/{reel_id}/comments", response_model=List[CommentOut])
async def get_reel_comments(
    reel_id: int,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_async_session)
):
    result = await get_comments_for_reel(reel_id, skip, limit, db)
    comments = result["comments"]
    replies_by_parent = result["replies_by_parent"]
    response = []
    for comment in comments:
        comment_out = CommentOut(
            id=comment.id,
            content=comment.content,
            user_id=comment.user_id,
            reel_id=comment.reel_id,
            parent_id=comment.parent_id,
            created_at=comment.created_at,
            replies=[
                CommentBrief(
                    id=reply.id,
                    content=reply.content,
                    user_id=reply.user_id,
                    reel_id=reply.reel_id,
                    parent_id=reply.parent_id,
                    created_at=reply.created_at,
                )
                for reply in replies_by_parent.get(comment.id, [])
            ]
        )
        response.append(comment_out)
    return response

@router.get("/reels/comments/{comment_id}/replies", response_model=Dict)
async def get_reel_comment_replies_list(
    comment_id: int,
    skip: int = 0,
    limit: int = 5,
    db: AsyncSession = Depends(get_async_session)
):
    result = await get_reel_comment_replies(comment_id, skip, limit, db)
    return {
        "replies": [CommentBrief.model_validate(r, from_attributes=True) for r in result["replies"]],
        "total": result["total"],
        "skip": result["skip"],
        "limit": result["limit"]
    }

@router.delete("/reels/comments/{comment_id}")
async def delete_a_reel_comment(
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    if current_user.is_admin:
        return await delete_reel_comment(comment_id, None, db)
    return await delete_reel_comment(comment_id, current_user.id, db)