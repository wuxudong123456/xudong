"""
灯谜库实体模型
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from backend.entity.base import Base


class LanternRiddle(Base):
    __tablename__ = "lantern_riddles"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID")
    riddle_text = Column(String(500), nullable=False, comment="谜面")
    answer = Column(String(200), nullable=False, comment="谜底")
    hint = Column(String(500), default=None, comment="提示")
    difficulty = Column(String(20), default="easy", comment="难度: easy/medium/hard")
    category = Column(String(50), default=None, comment="类别: 人物/剧情/法宝/典故/歇后语")
    is_deleted = Column(Integer, default=0, comment="逻辑删除")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
