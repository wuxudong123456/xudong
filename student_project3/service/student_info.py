"""学生服务模块，处理学生相关业务逻辑"""

from fastapi import HTTPException
from sqlalchemy.orm import Session
from dao.student_info import *
from schemas.student_info import StudentResponse, StudentUpdate


def get_student(db: Session, student_id: int) -> StudentResponse:
    """
    根据ID查询单个学生
    
    :param db: 数据库会话
    :param student_id: 学生ID
    :return: 学生信息
    :raises HTTPException: 当学生不存在时抛出404错误
    """
    stu = get_student_by_id(db=db, student_id=student_id)
    if not stu:
        raise HTTPException(status_code=404, detail="学生不存在")
    return stu


def get_students(
    db: Session, 
    student_name: str = None, 
    class_id: int = None, 
    page: int = 1, 
    page_size: int = 10
) -> tuple:
    """
    分页查询学生列表
    
    :param db: 数据库会话
    :param student_name: 学生姓名（模糊查询）
    :param class_id: 班级ID
    :param page: 页码
    :param page_size: 每页条数
    :return: (总数, 学生列表)
    :raises HTTPException: 当无数据时抛出404错误
    """
    total, data = get_student_list(
        db=db, 
        student_name=student_name, 
        class_id=class_id,
        page=page, 
        page_size=page_size
    )
    if total == 0:
        raise HTTPException(status_code=404, detail="暂无学生数据")
    return total, data


def update_student(db: Session, student_id: int, data: StudentUpdate) -> StudentResponse:
    """
    更新学生信息
    
    :param db: 数据库会话
    :param student_id: 学生ID
    :param data: 更新数据
    :return: 更新后的学生信息
    :raises HTTPException: 当学生不存在时抛出404错误
    """
    stu = update_student_by_id(db=db, student_id=student_id, data=data)
    if not stu:
        raise HTTPException(status_code=404, detail="学生不存在")
    return stu


def delete_student(db: Session, student_id: int) -> bool:
    """
    逻辑删除学生
    
    :param db: 数据库会话
    :param student_id: 学生ID
    :return: 删除是否成功
    :raises HTTPException: 当学生不存在时抛出404错误
    """
    success = delete_student_by_id(db=db, student_id=student_id)
    if not success:
        raise HTTPException(status_code=404, detail="学生不存在")
    return success


def restore_student(db: Session, student_id: int) -> bool:
    """
    恢复已删除的学生
    
    :param db: 数据库会话
    :param student_id: 学生ID
    :return: 恢复是否成功
    :raises HTTPException: 当学生不存在时抛出404错误
    """
    success = restore_student_by_id(db=db, student_id=student_id)
    if not success:
        raise HTTPException(status_code=404, detail="学生不存在")
    return success


def get_deleted_students(
    db: Session, 
    student_name: str = None,
    page: int = 1, 
    page_size: int = 10
) -> tuple:
    """
    分页查询已删除的学生列表
    
    :param db: 数据库会话
    :param student_name: 学生姓名（模糊查询）
    :param page: 页码
    :param page_size: 每页条数
    :return: (总数, 学生列表)
    :raises HTTPException: 当无数据时抛出404错误
    """
    total, data = get_deleted_student_list(
        db=db, 
        student_name=student_name, 
        page=page, 
        page_size=page_size
    )
    if total == 0:
        raise HTTPException(status_code=404, detail="暂无已删除学生数据")
    return total, data


def get_students_over_age(db: Session, age_threshold: int):
    """
    查询年龄超过指定阈值的学生
    
    :param db: 数据库会话
    :param age_threshold: 年龄阈值
    :return: 符合条件的学生列表
    :raises HTTPException: 当无数据时抛出404错误
    """
    students = get_students_by_age(db=db, age_threshold=age_threshold)
    if not students:
        raise HTTPException(status_code=404, detail="暂无符合条件的学生")
    return students


def get_student_gender_stats(db: Session, class_id: int = None):
    """
    统计班级学生性别分布
    
    :param db: 数据库会话
    :param class_id: 班级ID（可选，不传则统计所有班级）
    :return: 性别统计数据
    :raises HTTPException: 当无数据时抛出404错误
    """
    stats = get_gender_stats(db=db, class_id=class_id)
    if not stats:
        raise HTTPException(status_code=404, detail="暂无统计数据")
    return stats