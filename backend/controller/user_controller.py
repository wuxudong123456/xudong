"""
用户管理接口控制层
提供用户CRUD、角色管理、状态变更等接口
仅超级管理员和管理员可访问
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from backend.dependencies import get_db, get_current_user, require_role
from backend.entity.user import User
from backend.dao.user_dao import UserDAO
from backend.utils.password_util import hash_password

router = APIRouter()


class UserCreateRequest(BaseModel):
    """创建用户请求体"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    role: str = Field(..., description="角色: super_admin/admin/teacher/student")
    real_name: Optional[str] = Field(None, description="真实姓名")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")


class UserUpdateRequest(BaseModel):
    """更新用户请求体"""
    real_name: Optional[str] = Field(None, description="真实姓名")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    role: Optional[str] = Field(None, description="角色")
    status: Optional[int] = Field(None, description="状态: 1启用 0禁用")


class ResetPasswordRequest(BaseModel):
    """重置密码请求体"""
    new_password: str = Field(..., description="新密码")


@router.get("/", summary="分页查询用户列表")
def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None, description="用户名/姓名搜索"),
    role: Optional[str] = Query(None, description="角色筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super_admin", "admin")),
):
    """查询用户列表，支持关键词搜索和角色筛选"""
    dao = UserDAO(db)
    total, users = dao.list_users(page, size, keyword, role)
    items = [{
        "id": u.id,
        "username": u.username,
        "role": u.role,
        "real_name": u.real_name,
        "email": u.email,
        "phone": u.phone,
        "status": u.status,
        "last_login_time": u.last_login_time.isoformat() if u.last_login_time else None,
        "create_time": u.create_time.isoformat() if u.create_time else None,
    } for u in users]
    return {
        "code": 200,
        "message": "查询成功",
        "data": {"items": items, "total": total, "page": page, "size": size},
    }


@router.post("/", summary="创建用户")
def create_user(
    req: UserCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super_admin")),
):
    """创建新用户，仅超级管理员可操作"""
    dao = UserDAO(db)
    # 检查用户名是否已存在
    existing = dao.get_by_username(req.username)
    if existing:
        return {"code": 400, "message": "用户名已存在", "data": None}
    hashed = hash_password(req.password)
    user = dao.create_user(req.username, hashed, req.role, req.real_name)
    if req.email:
        user.email = req.email
    if req.phone:
        user.phone = req.phone
    db.commit()
    return {"code": 200, "message": "创建用户成功", "data": {"id": user.id}}


@router.put("/{user_id}", summary="更新用户信息")
def update_user(
    user_id: int,
    req: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super_admin", "admin")),
):
    """更新用户信息（角色、状态、联系方式等）"""
    dao = UserDAO(db)
    user = dao.get_by_id(user_id)
    if not user:
        return {"code": 404, "message": "用户不存在", "data": None}
    update_data = req.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    db.commit()
    return {"code": 200, "message": "更新成功", "data": None}


@router.put("/{user_id}/reset-password", summary="重置用户密码")
def reset_password(
    user_id: int,
    req: ResetPasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super_admin")),
):
    """重置指定用户的密码，仅超级管理员可操作"""
    dao = UserDAO(db)
    user = dao.get_by_id(user_id)
    if not user:
        return {"code": 404, "message": "用户不存在", "data": None}
    user.password = hash_password(req.new_password)
    db.commit()
    return {"code": 200, "message": "密码重置成功", "data": None}


@router.delete("/{user_id}", summary="删除用户（软删除）")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super_admin")),
):
    """软删除用户，仅超级管理员可操作"""
    dao = UserDAO(db)
    user = dao.get_by_id(user_id)
    if not user:
        return {"code": 404, "message": "用户不存在", "data": None}
    if user.role == "super_admin":
        return {"code": 400, "message": "不能删除超级管理员", "data": None}
    user.is_deleted = 1
    db.commit()
    return {"code": 200, "message": "删除成功", "data": None}
