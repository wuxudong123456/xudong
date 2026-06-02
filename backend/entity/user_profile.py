from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.sql import func
from backend.entity.base import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, unique=True)
    nickname = Column(String(50))
    preferred_topics = Column(String(500))
    personality_tags = Column(String(500))
    interaction_count = Column(Integer, default=0)
    last_emotion = Column(String(50))
    last_active_time = Column(DateTime)
    proactive_preference = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
