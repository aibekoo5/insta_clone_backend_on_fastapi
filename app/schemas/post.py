from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Optional
from datetime import datetime
from app.schemas.user import UserOut

class PostBase(BaseModel):
    caption: Optional[str] = Field(None, max_length=2000)
    is_private: bool = False

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    pass

class PostOut(PostBase):
    id: int
    image_url: Optional[HttpUrl]
    video_url: Optional[HttpUrl]
    owner_id: int
    created_at: datetime
    like_count: int = 0
    comment_count: int = 0
    owner: UserOut  # Make sure UserOut includes all required fields

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
