from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.schemas.user import UserOut


class CommentBase(BaseModel):
    content: str = Field(..., max_length=1000)


class CommentCreate(CommentBase):
    pass


# Simple schema without relationships
class CommentBrief(BaseModel):
    id: int
    content: str
    user_id: int
    post_id: Optional[int] = None
    reel_id: Optional[int] = None
    parent_id: Optional[int] = None
    created_at: datetime
    owner: UserOut

    model_config = ConfigDict(from_attributes=True)


# Output schema for comments with replies
class CommentOut(CommentBrief):
    replies: List[CommentBrief] = Field(default_factory=list)
