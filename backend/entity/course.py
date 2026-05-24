"""
课程信息实体模型
"""
from sqlalchemy import Column, Integer, String, Text
from backend.entity.base import Base, TimestampMixin, SoftDeleteMixin


class Course(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "course_info"

    course_id = Column(Integer, primary_key=True, autoincrement=True, comment="课程ID")
    course_name = Column(String(100), nullable=False, comment="课程名称")
    course_code = Column(String(50), unique=True, nullable=False, comment="课程代码")
    description = Column(Text, default=None, comment="课程描述")
    teacher_id = Column(Integer, default=None, comment="授课老师ID")
    class_id = Column(Integer, default=None, comment="关联班级ID")
    total_hours = Column(Integer, default=None, comment="总课时")
