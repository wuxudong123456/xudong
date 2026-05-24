"""
成绩实体模型
"""
from sqlalchemy import Column, Integer, String, Numeric
from backend.entity.base import Base, TimestampMixin, SoftDeleteMixin


class Score(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "score"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="成绩ID")
    student_no = Column(String(50), nullable=False, comment="学生编号")
    exam_order = Column(Integer, nullable=False, comment="考核序次")
    score = Column(Numeric(5, 2), default=None, comment="成绩")
