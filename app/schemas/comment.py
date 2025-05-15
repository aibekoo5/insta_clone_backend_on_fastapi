from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class CommentBase(BaseModel):
    content: str = Field(..., max_length=1000)


class CommentCreate(CommentBase):
    pass


# Simple schema without relationships
class CommentBrief(BaseModel):
    id: int
    content: str
    user_id: int
    post_id: int
    parent_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Output schema for comments with replies
class CommentOut(CommentBrief):
    replies: List[CommentBrief] = Field(default_factory=list)
