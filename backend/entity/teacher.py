"""
老师实体模型
"""
from sqlalchemy import Column, Integer, String
from backend.entity.base import Base, TimestampMixin, SoftDeleteMixin


class Teacher(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "teacher"

    teacher_id = Column(Integer, primary_key=True, autoincrement=True, comment="老师编号")
    teacher_name = Column(String(50), nullable=False, comment="老师姓名")
    gender = Column(String(10), default=None, comment="性别")
    phone = Column(String(20), default=None, comment="联系电话")
    identity = Column(String(20), default=None, comment="身份: 班主任/授课老师/助教/顾问")
