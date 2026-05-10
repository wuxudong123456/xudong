from sqlalchemy import Column,String,Integer,Date
from core.database import Base

#创建基类
class Employment(Base):
    __tablename__ = "employment"
    employment_id = Column(Integer,primary_key=True,autoincrement=True,comment="就业id")
    student_no = Column(String(100), unique=True,comment="学号")
    student_name = Column(String(100),comment="学生姓名")
    class_id = Column(Integer,comment="班级id")
    job_open_time = Column(Date,comment="就业开放时间")
    offer_send_time = Column(Date,comment="offer获取时间")
    company_name = Column(String(100),comment="公司名称")
    salary = Column(Integer,comment="薪资")
    is_deleted = Column(Integer, default=0, comment="0未删除 1已删除")

