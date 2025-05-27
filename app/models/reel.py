from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Reel(Base):
    __tablename__ = "reels"

    id = Column(Integer, primary_key=True, index=True)
    video_url = Column(String(255), nullable=False)
    caption = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    like_count = Column(Integer, default=0, nullable=False)
    comment_count = Column(Integer, default=0, nullable=False)

    owner = relationship("User", back_populates="reels")
    likes = relationship("Like", back_populates="reel", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="reel", cascade="all, delete-orphan")