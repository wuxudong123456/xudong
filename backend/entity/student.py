"""
学生实体模型
"""
from sqlalchemy import Column, Integer, String, Date
from backend.entity.base import Base, TimestampMixin, SoftDeleteMixin


class Student(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "student"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="学生编号")
    student_no = Column(String(50), unique=True, nullable=False, comment="学生编号(业务号)")
    class_id = Column(Integer, nullable=False, comment="班级ID")
    student_name = Column(String(50), nullable=False, comment="学生姓名")
    gender = Column(String(10), default=None, comment="性别")
    age = Column(Integer, default=None, comment="年龄")
    native_place = Column(String(100), default=None, comment="籍贯")
    graduate_school = Column(String(100), default=None, comment="毕业院校")
    major = Column(String(100), default=None, comment="专业")
    education = Column(String(50), default=None, comment="学历")
    admission_time = Column(Date, default=None, comment="入学时间")
    graduate_time = Column(Date, default=None, comment="毕业时间")
    advisor_id = Column(Integer, default=None, comment="顾问编号")
    job_open_time = Column(Date, default=None, comment="就业开放时间")
