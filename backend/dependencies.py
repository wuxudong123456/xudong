"""
依赖注入模块
提供 get_db, get_current_user, require_permission 等 FastAPI Depends 函数
"""
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from backend.config import settings
from backend.database import get_db as _get_db
from backend.entity.user import User

# HTTP Bearer Token 认证方案
security = HTTPBearer()


def get_db() -> Session:
    """
    获取数据库会话依赖
    使用方式: db: Session = Depends(get_db)
    """
    yield from _get_db()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    从JWT Token解析当前登录用户
    自动校验Token有效性、用户是否存在、是否被禁用
    使用方式: current_user: User = Depends(get_current_user)
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="登录已过期，请重新登录",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 解码JWT Token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = int(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception

    # 从数据库查询用户
    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == 0,
    ).first()

    if user is None:
        raise credentials_exception
    if user.status == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用，请联系管理员",
        )

    return user


def require_role(*roles: str):
    """
    角色权限校验依赖工厂
    使用方式: current_user: User = Depends(require_role("super_admin", "admin"))
    示例: 超级管理员和普通管理员可访问: require_role("super_admin", "admin")
    """

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足，无法访问该资源",
            )
        return current_user

    return role_checker
