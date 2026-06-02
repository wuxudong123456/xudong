from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.sql import func
from backend.entity.base import Base


class MemoryFragment(Base):
    __tablename__ = "memory_fragments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    importance = Column(Float, default=0.5)
    memory_type = Column(String(20), default="fact")
    source_session_id = Column(String(100))
    chunk_id = Column(String(100))
    access_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
