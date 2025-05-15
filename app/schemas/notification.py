from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.schemas.user import UserOut
from app.schemas.post import PostOut
from app.schemas.comment import CommentOut
from typing import Optional

class NotificationBase(BaseModel):
    notification_type: str
    is_read: bool

class NotificationOut(NotificationBase):
    id: int
    user_id: int
    sender_id: int
    post_id: Optional[int]
    comment_id: Optional[int]
    created_at: datetime
    sender: UserOut
    post: Optional[PostOut]
    comment: Optional[CommentOut]

    model_config = ConfigDict(from_attributes=True)