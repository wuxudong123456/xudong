"""就业管理接口控制层"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.dependencies import get_db, get_current_user, require_role
from backend.entity.user import User
from backend.service.employment_service import EmploymentService
from backend.schema.employment_schema import EmploymentCreate, EmploymentUpdate

router = APIRouter()


@router.get("/", summary="分页查询就业列表")
def list_employments(
    page: int = Query(1), size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None), class_id: Optional[int] = Query(None),
    student_no: Optional[str] = Query(None),
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    service = EmploymentService(db)
    return {"code": 200, "message": "查询成功", "data": service.list_employments(page, size, keyword, class_id, student_no)}


@router.get("/stats", summary="就业统计")
def employment_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = EmploymentService(db)
    return {"code": 200, "message": "查询成功", "data": service.get_stats()}


@router.post("/", summary="新增就业记录")
def create_employment(data: EmploymentCreate, db: Session = Depends(get_db),
                      current_user: User = Depends(require_role("super_admin", "admin"))):
    service = EmploymentService(db)
    return {"code": 200, "message": "新增成功", "data": service.create(data.model_dump())}


@router.put("/{emp_id}", summary="编辑就业记录")
def update_employment(emp_id: int, data: EmploymentUpdate, db: Session = Depends(get_db),
                      current_user: User = Depends(require_role("super_admin", "admin"))):
    service = EmploymentService(db)
    return {"code": 200, "message": "编辑成功", "data": service.update(emp_id, data.model_dump(exclude_none=True))}


@router.delete("/{emp_id}", summary="删除就业记录")
def delete_employment(emp_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(require_role("super_admin", "admin"))):
    service = EmploymentService(db)
    service.delete(emp_id)
    return {"code": 200, "message": "删除成功", "data": None}
