"""
问答对实体模型 (RAG知识库)
"""
from sqlalchemy import Column, Integer, String, Text, SmallInteger, DateTime
from sqlalchemy.sql import func
from backend.entity.base import Base


class QAPair(Base):
    __tablename__ = "qa_pairs"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID")
    question = Column(Text, nullable=False, comment="问题")
    answer = Column(Text, nullable=False, comment="答案")
    source_chapter = Column(Integer, default=None, comment="来源章节")
    tags = Column(String(500), default=None, comment="标签JSON")
    is_verified = Column(SmallInteger, default=0, comment="是否已验证")
    is_deleted = Column(SmallInteger, default=0, comment="逻辑删除")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
