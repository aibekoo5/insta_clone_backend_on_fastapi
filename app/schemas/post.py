from pydantic import BaseModel, Field, AnyUrl, field_validator
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
    image_url: Optional[AnyUrl] = None
    video_url: Optional[AnyUrl] = None
    owner_id: int
    created_at: datetime
    like_count: int = 0
    comment_count: int = 0
    owner: UserOut
    is_liked_by_current_user: Optional[bool] = None

    @field_validator('image_url', 'video_url', mode='before')
    def convert_path_to_url(cls, value):
        if value and isinstance(value, str):
            if value.startswith('/'):
                return f"http://localhost:8000{value}"  # Adjust with your actual domain
            return value
        return value
