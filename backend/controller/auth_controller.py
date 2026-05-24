"""
认证接口控制层
处理登录、Token刷新、获取用户信息、修改密码等HTTP请求
所有接口返回统一响应格式: { code, message, data }
"""
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from backend.dependencies import get_db, get_current_user
from backend.entity.user import User
from backend.service.auth_service import AuthService
from backend.schema import LoginRequest, ChangePasswordRequest

router = APIRouter()


@router.post("/login", summary="用户登录")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    用户登录接口
    请求示例:
    {
      "username": "super_admin",  // 超级管理员登录
      "password": "admin123"
    }
    其他预置账号:
    - 管理员: admin1 / 123456
    - 教师:   teacher1 / 123456
    - 学生:   student1 / 123456
    """
    service = AuthService(db)
    result = service.login(request.username, request.password)
    return {"code": 200, "message": "登录成功", "data": result}


@router.post("/refresh", summary="刷新Token")
def refresh_token(refresh_token: str = Body(..., embed=True), db: Session = Depends(get_db)):
    """使用刷新令牌获取新的访问令牌"""
    service = AuthService(db)
    result = service.refresh_token(refresh_token)
    return {"code": 200, "message": "Token刷新成功", "data": result}


@router.get("/me", summary="获取当前用户信息")
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取当前登录用户的详细信息(含权限列表)
    需要在 Header 中传递: Authorization: Bearer <token>
    """
    service = AuthService(db)
    result = service.get_user_info(current_user)
    return {"code": 200, "message": "success", "data": result}


@router.put("/me/password", summary="修改密码")
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    修改当前用户密码
    请求示例: {"old_password": "123456", "new_password": "654321"}
    """
    service = AuthService(db)
    service.change_password(current_user, request.old_password, request.new_password)
    return {"code": 200, "message": "密码修改成功", "data": None}
