"""学生管理API模块"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from schemas.student_info import StudentCreate, StudentUpdate, StudentResponse
from service.student_info import (
    get_student,
    get_students,
    update_student,
    delete_student,
    restore_student,
    get_deleted_students,
    get_students_over_age,
    get_student_gender_stats,
    create_student
)

router = APIRouter(prefix="/students", tags=["学生管理"])


@router.post("/create", response_model=dict, summary="新增学生")
def add_student(s: StudentCreate, db: Session = Depends(get_db)):
    """
    新增学生信息
    
    :param s: 学生数据
    :param db: 数据库会话
    :return: 创建结果
    """
    result = create_student(db, s)
    return {"code": 200, "message": "添加成功", "data": result}


@router.get("/check", response_model=dict, summary="分页查询学生列表")
def list_students(
    student_name: Optional[str] = Query(None, description="学生姓名（模糊查询）"),
    class_id: Optional[int] = Query(None, description="班级ID"),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(10, description="每页条数", ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    分页查询学生列表，支持按姓名和班级筛选
    
    :param student_name: 学生姓名（模糊查询）
    :param class_id: 班级ID
    :param page: 页码
    :param page_size: 每页条数
    :param db: 数据库会话
    :return: 分页学生数据
    """
    total, data = get_students(db, student_name, class_id, page, page_size)
    return {
        "code": 200,
        "message": "查询成功",
        "total": total,
        "data": [StudentResponse.model_validate(item).model_dump() for item in data],
        "page": page,
        "page_size": page_size
    }


@router.get("/check/{student_id}", response_model=dict, summary="查询单个学生")
def get_one_student(student_id: int, db: Session = Depends(get_db)):
    """
    根据ID查询单个学生信息
    
    :param student_id: 学生ID
    :param db: 数据库会话
    :return: 学生信息
    """
    result = get_student(db, student_id)
    return {"code": 200, "message": "查询成功", "data": result}


@router.put("/update/{student_id}", response_model=dict, summary="更新学生信息")
def update_student_info(student_id: int, s: StudentUpdate, db: Session = Depends(get_db)):
    """
    更新学生信息
    
    :param student_id: 学生ID
    :param s: 更新数据
    :param db: 数据库会话
    :return: 更新结果
    """
    result = update_student(db, student_id, s)
    return {"code": 200, "message": "修改成功", "data": result}


@router.delete("/delete/{student_id}", response_model=dict, summary="删除学生")
def remove_student(student_id: int, db: Session = Depends(get_db)):
    """
    逻辑删除学生
    
    :param student_id: 学生ID
    :param db: 数据库会话
    :return: 删除结果
    """
    delete_student(db, student_id)
    return {"code": 200, "message": "删除成功", "data": None}


@router.put("/restore/{student_id}", response_model=dict, summary="恢复学生")
def restore_student_info(student_id: int, db: Session = Depends(get_db)):
    """
    恢复已删除的学生
    
    :param student_id: 学生ID
    :param db: 数据库会话
    :return: 恢复结果
    """
    restore_student(db, student_id)
    return {"code": 200, "message": "恢复成功", "data": None}


@router.get("/check_is_deleted", response_model=dict, summary="查询已删除学生")
def check_deleted_students(
    student_name: Optional[str] = Query(None, description="学生姓名（模糊查询）"),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(10, description="每页条数", ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    分页查询已删除的学生列表
    
    :param student_name: 学生姓名（模糊查询）
    :param page: 页码
    :param page_size: 每页条数
    :param db: 数据库会话
    :return: 已删除学生数据
    """
    total, data = get_deleted_students(db, student_name, page, page_size)
    return {
        "code": 200,
        "message": "查询成功",
        "total": total,
        "data": data,
        "page": page,
        "page_size": page_size
    }


@router.get("/check_age", response_model=dict, summary="查询超过指定年龄的学生")
def check_student_age(
    age_threshold: int = Query(..., description="年龄阈值"),
    db: Session = Depends(get_db)
):
    """
    查询年龄超过指定阈值的学生
    
    :param age_threshold: 年龄阈值
    :param db: 数据库会话
    :return: 符合条件的学生列表
    """
    result = get_students_over_age(db, age_threshold)
    return {"code": 200, "message": "查询成功", "data": result}


@router.get("/check_gender", response_model=dict, summary="统计班级性别分布")
def check_student_gender(
    class_id: Optional[int] = Query(None, description="班级ID"),
    db: Session = Depends(get_db)
):
    """
    统计班级学生性别分布
    
    :param class_id: 班级ID（可选，不传则统计所有班级）
    :param db: 数据库会话
    :return: 性别统计数据
    """
    result = get_student_gender_stats(db, class_id)
    return {"code": 200, "message": "查询成功", "data": result}