"""
用户数据访问层
继承 BaseDAO，提供用户特有的数据库操作
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from backend.entity.user import User
from backend.entity.permission import RolePermission


class UserDAO:
    """用户数据访问对象"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名查询用户
        :param username: 用户名，如 "admin1"
        :return: User对象或None
        """
        return (
            self.db.query(User)
            .filter(
                User.username == username,
                User.is_deleted == 0,
            )
            .first()
        )

    def get_by_id(self, user_id: int) -> Optional[User]:
        """根据ID查询用户"""
        return (
            self.db.query(User)
            .filter(User.id == user_id, User.is_deleted == 0)
            .first()
        )

    def get_user_permissions(self, role: str) -> List[str]:
        """
        获取角色对应的权限代码列表
        :param role: 角色名，如 "admin"
        :return: 权限代码列表，如 ["student:view", "student:create", ...]
        """
        rows = (
            self.db.query(RolePermission.permission_code)
            .filter(RolePermission.role == role)
            .all()
        )
        return [row[0] for row in rows]

    def create_user(self, username: str, password: str, role: str,
                    real_name: str = None) -> User:
        """创建新用户"""
        user = User(
            username=username,
            password=password,
            role=role,
            real_name=real_name,
            status=1,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_login_time(self, user: User):
        """更新最后登录时间"""
        from datetime import datetime
        user.last_login_time = datetime.now()
        self.db.commit()

    def change_password(self, user: User, new_password: str):
        """修改用户密码"""
        user.password = new_password
        self.db.commit()

    def list_users(self, page: int = 1, size: int = 20,
                   keyword: str = None, role: str = None) -> tuple:
        """分页查询用户列表"""
        query = self.db.query(User).filter(User.is_deleted == 0)
        if keyword:
            query = query.filter(
                User.username.like(f"%{keyword}%") |
                User.real_name.like(f"%{keyword}%")
            )
        if role:
            query = query.filter(User.role == role)
        total = query.count()
        items = query.offset((page - 1) * size).limit(size).all()
        return total, items
