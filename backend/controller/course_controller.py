"""课程管理接口控制层"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.dependencies import get_db, get_current_user, require_role
from backend.entity.user import User
from backend.service.course_service import CourseService
from backend.schema.course_schema import CourseCreate, CourseUpdate

router = APIRouter()


@router.get("/", summary="分页查询课程列表")
def list_courses(page: int = Query(1), size: int = Query(20, ge=1, le=100),
                 keyword: Optional[str] = Query(None),
                 db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = CourseService(db)
    return {"code": 200, "message": "查询成功", "data": service.list_courses(page, size, keyword)}


@router.post("/", summary="新增课程")
def create_course(data: CourseCreate, db: Session = Depends(get_db),
                  current_user: User = Depends(require_role("super_admin", "admin"))):
    service = CourseService(db)
    return {"code": 200, "message": "新增成功", "data": service.create(data.model_dump())}


@router.put("/{course_id}", summary="编辑课程")
def update_course(course_id: int, data: CourseUpdate, db: Session = Depends(get_db),
                  current_user: User = Depends(require_role("super_admin", "admin"))):
    service = CourseService(db)
    return {"code": 200, "message": "编辑成功", "data": service.update(course_id, data.model_dump(exclude_none=True))}


@router.delete("/{course_id}", summary="删除课程")
def delete_course(course_id: int, db: Session = Depends(get_db),
                  current_user: User = Depends(require_role("super_admin", "admin"))):
    service = CourseService(db)
    service.delete(course_id)
    return {"code": 200, "message": "删除成功", "data": None}
