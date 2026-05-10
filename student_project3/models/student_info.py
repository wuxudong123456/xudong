from sqlalchemy import Column, Integer, String, Date
from core.database import Base
#学生信息表
class Student(Base):
    __tablename__ = "student_info"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="学生编号")
    student_no = Column(String(50), nullable=False, comment="学生编号（业务号）")
    class_id = Column(Integer, nullable=False, comment="班级ID")
    student_name = Column(String(50), nullable=False, comment="学生姓名")
    gender = Column(String(10), nullable=True, comment="性别")
    age = Column(Integer, nullable=True, comment="年龄")
    native_place = Column(String(100), nullable=True, comment="籍贯")
    graduate_school = Column(String(100), nullable=True, comment="毕业院校")
    major = Column(String(100), nullable=True, comment="专业")
    education = Column(String(50), nullable=True, comment="学历")
    admission_time = Column(Date, nullable=True, comment="入学时间")
    graduation_time = Column(Date, nullable=True, comment="毕业时间")
    advisor_id = Column(Integer, nullable=True, comment="顾问编号")
    is_deleted = Column(Integer, default=0, nullable=False, comment="逻辑删除 0-未删 1-删除")