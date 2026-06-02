"""
用户实体模型 (扩展自现有users表)
"""
from sqlalchemy import Column, Integer, String, DateTime, SmallInteger
from backend.entity.base import Base, SoftDeleteMixin


class User(Base, SoftDeleteMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="用户ID")
    username = Column(String(255), nullable=False, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码(bcrypt加密)")
    role = Column(String(20), nullable=False, comment="角色: super_admin/admin/teacher/student")
    real_name = Column(String(50), default=None, comment="真实姓名")
    email = Column(String(100), default=None, comment="邮箱")
    phone = Column(String(20), default=None, comment="手机号")
    avatar = Column(String(255), default=None, comment="头像URL")
    status = Column(SmallInteger, default=1, nullable=False, comment="状态: 0=禁用 1=启用")
    last_login_time = Column(DateTime, default=None, comment="最后登录时间")
    create_time = Column(DateTime, default=None, comment="创建时间")
    update_time = Column(DateTime, default=None, comment="更新时间")
