"""
认证业务逻辑层
处理登录、Token签发/刷新、密码修改、用户管理
"""
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from backend.dao.user_dao import UserDAO
from backend.entity.user import User
from backend.utils.password_util import verify_password, hash_password
from backend.utils.jwt_util import create_access_token, create_refresh_token, decode_token


class AuthService:
    """认证服务"""

    def __init__(self, db: Session):
        self.db = db
        self.user_dao = UserDAO(db)

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        用户登录
        :param username: 用户名
        :param password: 明文密码
        :return: { access_token, refresh_token, user_info }
        登录账号示例:
          超级管理员: username="super_admin", password="admin123"
          管理员:     username="admin1",      password="123456"
          教师:       username="teacher1",    password="123456"
          学生:       username="student1",    password="123456"
        """
        # 1. 查询用户
        user = self.user_dao.get_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
            )
        # 2. 检查用户是否被禁用
        if user.status == 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账号已被禁用，请联系管理员",
            )
        # 3. 验证密码
        if not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
            )
        # 4. 发放Token
        access_token = create_access_token(user.id, user.role)
        refresh_token = create_refresh_token(user.id)
        # 5. 更新最后登录时间
        self.user_dao.update_login_time(user)
        # 6. 查询用户权限
        permissions = self.user_dao.get_user_permissions(user.role)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_info": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "real_name": user.real_name,
                "email": user.email,
                "phone": user.phone,
                "avatar": user.avatar,
                "permissions": permissions,
            },
        }

    def refresh_token(self, refresh_token_str: str) -> Dict[str, str]:
        """
        使用刷新令牌获取新的访问令牌
        :param refresh_token_str: 已签发的refresh token
        :return: { access_token, refresh_token }
        """
        payload = decode_token(refresh_token_str)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌",
            )
        user_id = int(payload.get("sub"))
        user = self.user_dao.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在",
            )
        new_access = create_access_token(user.id, user.role)
        new_refresh = create_refresh_token(user.id)
        return {"access_token": new_access, "refresh_token": new_refresh}

    def change_password(self, user: User, old_password: str, new_password: str):
        """
        修改当前用户密码
        :param user: 当前登录用户
        :param old_password: 旧密码(验证身份)
        :param new_password: 新密码(至少6位)
        """
        if not verify_password(old_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="旧密码错误",
            )
        if old_password == new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="新密码不能与旧密码相同",
            )
        if len(new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="新密码长度不能少于6位",
            )
        self.user_dao.change_password(user, hash_password(new_password))

    def get_user_info(self, user: User) -> Dict[str, Any]:
        """获取当前用户的完整信息(含权限)"""
        permissions = self.user_dao.get_user_permissions(user.role)
        return {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "real_name": user.real_name,
            "email": user.email,
            "phone": user.phone,
            "avatar": user.avatar,
            "permissions": permissions,
        }
