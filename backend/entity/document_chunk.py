"""
文档切片实体模型 (RAG文本分块)
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from backend.entity.base import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID")
    chunk_id = Column(String(100), unique=True, nullable=False, comment="向量库中的chunk ID")
    document_name = Column(String(255), nullable=False, comment="文档名称")
    chapter = Column(Integer, default=None, comment="章节号")
    chunk_text = Column(Text, nullable=False, comment="文本片段")
    chunk_index = Column(Integer, nullable=False, comment="片段序号")
    token_count = Column(Integer, default=None, comment="token数量")
    is_deleted = Column(Integer, default=0, comment="逻辑删除")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
