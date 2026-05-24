"""
SQLAlchemy 实体基类模块
所有ORM模型继承自统一的 Base、TimestampMixin 和 SoftDeleteMixin
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, SmallInteger
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类"""
    pass


class TimestampMixin:
    """
    时间戳混入类
    自动记录创建时间和更新时间
    """
    create_time = Column(
        DateTime,
        default=datetime.now,
        comment="创建时间"
    )
    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间"
    )


class SoftDeleteMixin:
    """
    软删除混入类
    is_deleted: 0=未删除, 1=已删除
    所有查询需自动过滤 is_deleted=0
    """
    is_deleted = Column(
        SmallInteger,
        default=0,
        nullable=False,
        comment="逻辑删除: 0=未删除, 1=已删除"
    )
