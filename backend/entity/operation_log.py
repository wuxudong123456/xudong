"""
操作日志实体模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, BigInteger
from sqlalchemy.sql import func
from backend.entity.base import Base


class OperationLog(Base):
    __tablename__ = "operation_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="日志ID")
    user_id = Column(Integer, default=None, comment="操作用户ID")
    username = Column(String(255), default=None, comment="操作用户名")
    module = Column(String(50), default=None, comment="操作模块")
    action = Column(String(50), default=None, comment="操作类型: CREATE/UPDATE/DELETE/EXPORT/IMPORT/LOGIN")
    target_type = Column(String(50), default=None, comment="目标类型")
    target_id = Column(String(50), default=None, comment="目标ID")
    detail = Column(Text, default=None, comment="操作详情JSON")
    ip_address = Column(String(50), default=None, comment="IP地址")
    user_agent = Column(String(500), default=None, comment="浏览器UA")
    create_time = Column(DateTime, default=func.now(), comment="操作时间")
