"""
对话历史实体模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, BigInteger
from sqlalchemy.sql import func
from backend.entity.base import Base


class ConversationHistory(Base):
    __tablename__ = "conversation_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="ID")
    user_id = Column(Integer, nullable=False, comment="用户ID")
    session_id = Column(String(100), nullable=False, comment="会话ID")
    role = Column(String(20), nullable=False, comment="角色: user/assistant/system")
    content = Column(Text, nullable=False, comment="消息内容")
    agent_type = Column(String(50), default=None, comment="处理的Agent类型")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
