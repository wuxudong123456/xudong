"""
权限相关实体模型 (RBAC)
"""
from sqlalchemy import Column, Integer, String
from backend.entity.base import Base


class Permission(Base):
    """权限定义表"""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID")
    code = Column(String(50), unique=True, nullable=False, comment="权限代码")
    name = Column(String(100), nullable=False, comment="权限名称")
    description = Column(String(255), default=None, comment="权限描述")
    module = Column(String(50), default=None, comment="所属模块")


class RolePermission(Base):
    """角色权限关联表"""
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID")
    role = Column(String(20), nullable=False, comment="角色")
    permission_code = Column(String(50), nullable=False, comment="权限代码")
