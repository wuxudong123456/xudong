"""
JWT Token工具模块
负责生成和解析JWT访问令牌与刷新令牌
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt
from backend.config import settings


def create_access_token(user_id: int, role: str) -> str:
    """
    生成访问令牌 (Access Token)
    :param user_id: 用户ID
    :param role: 用户角色 (super_admin/admin/teacher/student)
    :return: JWT Token字符串
    默认有效期: 2小时 (由 JWT_ACCESS_TOKEN_EXPIRE_MINUTES 配置)
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,             # 用户ID
        "role": role,               # 用户角色
        "exp": expire,             # 过期时间
        "iat": datetime.utcnow(),  # 签发时间
        "type": "access",          # Token类型
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    """
    生成刷新令牌 (Refresh Token)
    :param user_id: 用户ID
    :return: JWT Refresh Token
    默认有效期: 7天 (由 JWT_REFRESH_TOKEN_EXPIRE_DAYS 配置)
    """
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    解码JWT Token，返回payload字典
    :param token: JWT Token字符串
    :return: payload字典，解析失败返回None
    """
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except Exception:
        return None
