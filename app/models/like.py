from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    reel_id = Column(Integer, ForeignKey("reels.id"), nullable=True)

    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")
    reel = relationship("Reel", back_populates="likes")