from pydantic import BaseModel
from datetime import datetime
from app.schemas.user import UserOut
from typing import Optional

class StoryBase(BaseModel):
    pass

class StoryOut(StoryBase):
    id: int
    media_url: str
    owner_id: int
    created_at: datetime
    expires_at: datetime
    owner: UserOut

    class Config:
        from_attributes = True