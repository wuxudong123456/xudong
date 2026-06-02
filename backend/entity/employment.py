"""
就业信息实体模型
"""
from sqlalchemy import Column, Integer, String, Date
from backend.entity.base import Base, TimestampMixin, SoftDeleteMixin


class Employment(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "employment"

    employment_id = Column(Integer, primary_key=True, autoincrement=True, comment="就业ID")
    student_no = Column(String(50), nullable=False, unique=True, comment="学生编号")
    student_name = Column(String(50), nullable=False, comment="学生姓名(冗余)")
    class_id = Column(Integer, nullable=False, comment="班级ID(冗余)")
    offer_send_time = Column(Date, default=None, comment="offer下发时间")
    company_name = Column(String(100), default=None, comment="就业公司")
    offer_job = Column(String(50), default=None, comment="offer岗位")
    final_choice = Column(Integer, default=None, comment="是否最终选择: 0=否 1=是")
    salary = Column(Integer, default=None, comment="就业薪资")
