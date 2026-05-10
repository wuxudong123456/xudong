from sqlalchemy import Column, Integer, String, DateTime, func
from core.database import Base

#定义ORM模型
class Teacher_Model(Base):
    __tablename__ = 'teacher'
    teacher_id = Column(Integer,primary_key=True,autoincrement=True,comment="老师编号")
    teacher_name = Column(String(50),nullable=False,comment="老师姓名")
    gender = Column(String(10),nullable=True,comment="性别")
    phone = Column(String(20),nullable=True,comment="联系电话")
    is_deleted = Column(Integer,nullable=False,default=0,comment="逻辑删除 0-未删 1-已删")
    create_time = Column(DateTime,default=func.now(),comment="创建时间")
    update_time = Column(DateTime,default=func.now(),onupdate=func.now(),comment="更新时间")




