"""
公共 Pydantic Schema 定义
统一请求/响应模型
"""
from typing import Optional, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class PageRequest(BaseModel):
    """分页请求参数"""
    page: int = Field(default=1, ge=1, description="页码，从1开始")
    size: int = Field(default=20, ge=1, le=100, description="每页条数，最大100")


class ApiResponse(BaseModel):
    """统一API响应格式"""
    code: int = Field(default=200, description="状态码: 200=成功, 4xx=客户端错误, 500=服务器错误")
    message: str = Field(default="success", description="响应消息")
    data: Any = Field(default=None, description="响应数据")


class PageResponse(BaseModel):
    """分页响应格式"""
    items: List[Any] = Field(default=[], description="数据列表")
    total: int = Field(default=0, description="总记录数")
    page: int = Field(default=1, description="当前页码")
    size: int = Field(default=20, description="每页条数")
    pages: int = Field(default=0, description="总页数")


# ==========================================
# 认证相关 Schema
# ==========================================

class LoginRequest(BaseModel):
    """
    登录请求
    示例: {"username": "admin1", "password": "123456"}
    """
    username: str = Field(..., min_length=1, max_length=255, description="用户名")
    password: str = Field(..., min_length=1, max_length=255, description="密码")


class TokenResponse(BaseModel):
    """登录成功返回的Token"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    user_info: dict = Field(default={}, description="用户基本信息")


class UserInfo(BaseModel):
    """用户信息"""
    id: int
    username: str
    role: str
    real_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    permissions: List[str] = Field(default=[], description="用户拥有的权限列表")


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码，至少6位")
