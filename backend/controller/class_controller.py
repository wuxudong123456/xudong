"""班级管理接口控制层"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.dependencies import get_db, get_current_user, require_role
from backend.entity.user import User
from backend.service.class_service import ClassService
from backend.schema.class_schema import ClassCreate, ClassUpdate

router = APIRouter()


@router.get("/", summary="分页查询班级列表")
def list_classes(
    page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None, description="班级名称搜索"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ClassService(db)
    result = service.list_classes(page, size, keyword)
    return {"code": 200, "message": "查询成功", "data": result}


@router.get("/{class_id}", summary="查询班级详情")
def get_class(class_id: int, db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):
    service = ClassService(db)
    return {"code": 200, "message": "查询成功", "data": service.get_class(class_id)}


@router.post("/", summary="新增班级")
def create_class(cls: ClassCreate, db: Session = Depends(get_db),
                 current_user: User = Depends(require_role("super_admin", "admin"))):
    service = ClassService(db)
    return {"code": 200, "message": "新增成功", "data": service.create_class(cls.model_dump())}


@router.put("/{class_id}", summary="编辑班级")
def update_class(class_id: int, cls: ClassUpdate, db: Session = Depends(get_db),
                 current_user: User = Depends(require_role("super_admin", "admin"))):
    service = ClassService(db)
    return {"code": 200, "message": "编辑成功",
            "data": service.update_class(class_id, cls.model_dump(exclude_none=True))}


@router.delete("/{class_id}", summary="删除班级")
def delete_class(class_id: int, db: Session = Depends(get_db),
                 current_user: User = Depends(require_role("super_admin", "admin"))):
    service = ClassService(db)
    service.delete_class(class_id)
    return {"code": 200, "message": "删除成功", "data": None}


@router.get("/{class_id}/students", summary="查询班级学生")
def get_class_students(class_id: int, page: int = Query(1), size: int = Query(20),
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    service = ClassService(db)
    return {"code": 200, "message": "查询成功",
            "data": service.get_class_students(class_id, page, size)}
