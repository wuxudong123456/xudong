"""教师管理API模块（异步版本）
# 修改说明：
# 1. 使用 async/await 关键字
# 2. 调用异步 Service 方法时使用 await
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from core.database import get_db
from schemas.teacher import TeacherCreate, TeacherUpdate
from service.teacher import TeacherService

router = APIRouter(prefix="/teacher", tags=["老师管理模块"])


@router.get('/all', response_model=dict, summary="查询所有老师")
async def get_all_teachers(db: AsyncSession = Depends(get_db)):
    """
    查询所有教师信息

    :param db: 异步数据库会话
    :return: 教师列表
    """
    teachers = await TeacherService.get_all_teachers(db)
    return {"code": 200, "message": "查询成功", "data": teachers}


@router.post('/create', response_model=dict, summary="新增老师")
async def add_teacher(t: TeacherCreate, db: AsyncSession = Depends(get_db)):
    """
    新增教师信息

    :param t: 教师数据
    :param db: 异步数据库会话
    :return: 创建结果
    """
    result = await TeacherService.create_teacher(db, t)
    return {"code": 200, "message": "添加成功", "data": result}


@router.get('/check', response_model=dict, summary="条件查询老师（分页）")
async def list_teachers(
    teacher_name: Optional[str] = Query(None, description="教师姓名"),
    gender: Optional[str] = Query(None, description="性别"),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(10, description="每页条数", ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    分页查询教师列表，支持按姓名和性别筛选

    :param teacher_name: 教师姓名
    :param gender: 性别
    :param page: 页码
    :param page_size: 每页条数
    :param db: 异步数据库会话
    :return: 分页教师数据
    """
    total, data = await TeacherService.get_teachers(
        db, teacher_name, gender, page, page_size
    )
    return {
        "code": 200,
        "message": "查询成功",
        "total": total,
        "data": data,
        "page": page,
        "page_size": page_size
    }


@router.get('/check/{teacher_id}', response_model=dict, summary="查询单个老师")
async def get_teacher_by_id(teacher_id: int, db: AsyncSession = Depends(get_db)):
    """
    根据ID查询单个教师信息

    :param teacher_id: 教师ID
    :param db: 异步数据库会话
    :return: 教师信息
    """
    result = await TeacherService.get_teacher(db, teacher_id)
    return {"code": 200, "message": "查询成功", "data": result}


@router.put('/update/{teacher_id}', response_model=dict, summary="修改老师信息")
async def update_teacher_api(
    teacher_id: int,
    data: TeacherUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    修改教师信息

    :param teacher_id: 教师ID
    :param data: 更新数据
    :param db: 异步数据库会话
    :return: 修改结果
    """
    result = await TeacherService.update_teacher(db, teacher_id, data)
    return {"code": 200, "message": "修改成功", "data": result}


@router.delete('/delete/{teacher_id}', response_model=dict, summary="删除老师")
async def delete_teacher(teacher_id: int, db: AsyncSession = Depends(get_db)):
    """
    逻辑删除教师

    :param teacher_id: 教师ID
    :param db: 异步数据库会话
    :return: 删除结果
    """
    await TeacherService.delete_teacher(db, teacher_id)
    return {"code": 200, "message": "删除成功", "data": None}


@router.get('/deleted', response_model=dict, summary="查询已删除的老师")
async def list_deleted_teachers(
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(10, description="每页条数", ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    分页查询已删除的教师列表

    :param page: 页码
    :param page_size: 每页条数
    :param db: 异步数据库会话
    :return: 已删除教师数据
    """
    total, data = await TeacherService.get_deleted_teachers(db, page, page_size)
    return {
        "code": 200,
        "message": "查询成功",
        "total": total,
        "data": data,
        "page": page,
        "page_size": page_size
    }


@router.put('/restore/{teacher_id}', response_model=dict, summary="恢复老师")
async def restore_teacher_api(teacher_id: int, db: AsyncSession = Depends(get_db)):
    """
    恢复已删除的教师

    :param teacher_id: 教师ID
    :param db: 异步数据库会话
    :return: 恢复结果
    """
    result = await TeacherService.restore_teacher(db, teacher_id)
    return {"code": 200, "message": "恢复成功", "data": result}


@router.get('/stats', response_model=dict, summary="统计男女老师人数")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """
    统计男女教师人数

    :param db: 异步数据库会话
    :return: 统计数据
    """
    result = await TeacherService.get_stats(db)
    return {"code": 200, "message": "查询成功", "data": result}
