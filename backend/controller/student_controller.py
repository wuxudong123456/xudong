"""
学生管理接口控制层
处理学生相关HTTP请求，实现增删改查、批量操作、Excel导入导出
"""
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.dependencies import get_db, get_current_user, require_role
from backend.entity.user import User
from backend.service.student_service import StudentService
from backend.schema.student_schema import StudentCreate, StudentUpdate, BatchDeleteRequest, StudentFilter

router = APIRouter()


@router.get("/", summary="分页查询学生列表")
def list_students(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页条数"),
    keyword: Optional[str] = Query(None, description="搜索关键词(学号/姓名)"),
    class_id: Optional[int] = Query(None, description="班级ID"),
    education: Optional[str] = Query(None, description="学历"),
    gender: Optional[str] = Query(None, description="性别"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    分页查询学生列表，支持多条件组合筛选
    需要权限: student:view
    """
    service = StudentService(db)
    result = service.list_students(page, size, keyword, class_id, education, gender)
    return {"code": 200, "message": "查询成功", "data": result}


@router.get("/{student_id}", summary="查询学生详情")
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """根据ID查询学生详细信息"""
    service = StudentService(db)
    result = service.get_student(student_id)
    return {"code": 200, "message": "查询成功", "data": result}


@router.post("/", summary="新增学生")
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super_admin", "admin")),
):
    """
    新增学生记录
    需要权限: super_admin 或 admin
    请求示例: {"student_no": "S2025001", "class_id": 1, "student_name": "张三"}
    """
    service = StudentService(db)
    result = service.create_student(student.model_dump())
    return {"code": 200, "message": "新增成功", "data": result}


@router.put("/{student_id}", summary="编辑学生")
def update_student(
    student_id: int,
    student: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super_admin", "admin")),
):
    """编辑学生信息，仅更新传入的非空字段"""
    service = StudentService(db)
    result = service.update_student(student_id, student.model_dump(exclude_none=True))
    return {"code": 200, "message": "编辑成功", "data": result}


@router.delete("/{student_id}", summary="删除学生")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super_admin", "admin")),
):
    """软删除学生(标记is_deleted=1)"""
    service = StudentService(db)
    service.delete_student(student_id)
    return {"code": 200, "message": "删除成功", "data": None}


@router.post("/batch-delete", summary="批量删除学生")
def batch_delete_students(
    request: BatchDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super_admin", "admin")),
):
    """批量软删除学生"""
    service = StudentService(db)
    count = service.batch_delete(request.ids)
    return {"code": 200, "message": f"成功删除 {count} 条记录", "data": {"deleted": count}}


@router.get("/export", summary="导出学生Excel")
def export_students(
    class_id: Optional[int] = Query(None, description="按班级导出"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """导出学生数据为Excel文件"""
    service = StudentService(db)
    excel_bytes = service.export_excel(class_id)
    return StreamingResponse(
        excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=students.xlsx"},
    )


@router.post("/import", summary="导入学生Excel")
async def import_students(
    file: UploadFile = File(..., description="Excel文件(.xlsx)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super_admin", "admin")),
):
    """
    从Excel批量导入学生
    表头顺序: 学号, 姓名, 性别, 年龄, 班级ID, 籍贯, 毕业院校, 专业, 学历
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        return {"code": 400, "message": "仅支持 .xlsx 或 .xls 格式文件", "data": None}
    service = StudentService(db)
    result = service.import_excel(file)
    return {
        "code": 200,
        "message": f"导入完成: 成功 {result['success']} 条, 失败 {result['fail']} 条",
        "data": result,
    }
