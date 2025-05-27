from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.schemas.user import UserOut


class ReelBase(BaseModel):
    caption: Optional[str] = Field(None, max_length=2000)

class ReelCreate(ReelBase):
    pass

class ReelUpdate(BaseModel):
    caption: Optional[str] = None

class ReelOut(ReelBase):
    id: int
    video_url: str
    owner_id: int
    created_at: datetime
    owner: UserOut
    like_count: int
    comment_count: int
    is_liked_by_current_user: Optional[bool] = None

    class Config:
        from_attributes = True