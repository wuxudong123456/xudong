"""班级管理API模块（异步版本）
# 修改说明：
# 1. 使用 async/await 关键字
# 2. 调用异步 Service 方法时使用 await
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from core.database import get_db
from schemas.class_info_schemas import ClassCreate, ClassUpdate
from service.class_info_service import ClassInfoService

class_router = APIRouter(prefix="/class", tags=["班级管理"])


@class_router.get("/all", response_model=dict, summary="获取所有班级")
async def get_all_classinfo_api(db: AsyncSession = Depends(get_db)):
    """
    获取所有班级信息

    :param db: 异步数据库会话
    :return: 班级列表
    """
    res = await ClassInfoService.get_all_classinfo_service(db)
    return {"code": 200, "message": "查询成功", "data": res}


@class_router.get("/one/{class_id}", response_model=dict, summary="查询单个班级")
async def get_one_class_api(class_id: int, db: AsyncSession = Depends(get_db)):
    """
    根据ID查询单个班级信息

    :param class_id: 班级ID
    :param db: 异步数据库会话
    :return: 班级信息
    """
    res = await ClassInfoService.get_one_classinfo_service(db, class_id)
    return {"code": 200, "message": "查询成功", "data": res}


@class_router.post("/add", response_model=dict, summary="添加班级")
async def add_class_api(cls: ClassCreate, db: AsyncSession = Depends(get_db)):
    """
    添加班级信息

    :param cls: 班级数据
    :param db: 异步数据库会话
    :return: 创建结果
    """
    result = await ClassInfoService.post_add_class_service(db, cls)
    return {"code": 200, "message": "添加成功", "data": result}


@class_router.put("/update/{class_id}", response_model=dict, summary="修改班级")
async def put_update_class(
    class_id: int,
    update_data: ClassUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    修改班级信息

    :param class_id: 班级ID
    :param update_data: 更新数据
    :param db: 异步数据库会话
    :return: 修改结果
    """
    result = await ClassInfoService.put_update_class_service(db, class_id, update_data)
    return {"code": 200, "message": "修改成功", "data": result}


@class_router.delete("/delete/{class_id}", response_model=dict, summary="删除班级")
async def delete_class_api(class_id: int, db: AsyncSession = Depends(get_db)):
    """
    逻辑删除班级

    :param class_id: 班级ID
    :param db: 异步数据库会话
    :return: 删除结果
    """
    await ClassInfoService.delete_class_service(db, class_id)
    return {"code": 200, "message": "删除成功", "data": None}


@class_router.put("/restore/{class_id}", response_model=dict, summary="恢复班级")
async def restore_class_api(class_id: int, db: AsyncSession = Depends(get_db)):
    """
    恢复已删除的班级

    :param class_id: 班级ID
    :param db: 异步数据库会话
    :return: 恢复结果
    """
    result = await ClassInfoService.restore_class_service(db, class_id)
    return {"code": 200, "message": "恢复成功", "data": result}


@class_router.get("/count/month", response_model=dict, summary="统计每月班级数")
async def count_class_month(
    month: Optional[str] = Query(None, description="月份（格式：YYYY-MM）"),
    db: AsyncSession = Depends(get_db)
):
    """
    统计每个月的班级数量

    :param month: 月份（可选）
    :param db: 异步数据库会话
    :return: 统计数据
    """
    result = await ClassInfoService.count_class_month_service(db, month=month)
    return {"code": 200, "message": "查询成功", "data": result}


@class_router.get("/class_by_lecturer_id/{lecturer_id}", response_model=dict, summary="按讲师ID查询班级")
async def get_class_by_lecturer_id_api(lecturer_id: int, db: AsyncSession = Depends(get_db)):
    """
    根据讲师ID查询其授课的班级

    :param lecturer_id: 讲师ID
    :param db: 异步数据库会话
    :return: 班级列表
    """
    result = await ClassInfoService.get_class_by_lecturer_id_service(db, lecturer_id)
    return {"code": 200, "message": "查询成功", "data": result}
