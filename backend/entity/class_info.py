"""
班级信息实体模型
"""
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from backend.entity.base import Base, TimestampMixin, SoftDeleteMixin


class ClassInfo(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "class_info"

    class_id = Column(Integer, primary_key=True, autoincrement=True, comment="班级编号")
    class_name = Column(String(50), nullable=False, comment="班级名称")
    start_time = Column(Date, default=None, comment="开课时间")
    close_time = Column(Date, default=None, comment="闭班时间")
    head_teacher_id = Column(Integer, default=None, comment="班主任ID")
    lecturer_id = Column(Integer, default=None, comment="授课老师ID")
