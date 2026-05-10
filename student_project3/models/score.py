# 成绩表模型
from sqlalchemy import Column, Integer, String, Float, UniqueConstraint
from core.database import Base

class Score_DB(Base):
    __tablename__ = 'score'  # 数据库表名

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True, comment='成绩id')
    student_no = Column(String(50), nullable=False, comment="学生编号")
    exam_order = Column(Integer, nullable=False, comment="考核序次")
    score = Column(Float, nullable=False, comment="成绩")
    is_deleted = Column(Integer, nullable=False, default=0, comment="逻辑删除 0-未删除，1-已删除")

    # 联合唯一约束：同一个学生同一场考试只能有一条成绩
    __table_args__ = (
        UniqueConstraint('student_no', 'exam_order', name='uk_student_exam'),
    )