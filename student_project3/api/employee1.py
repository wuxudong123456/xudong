"""就业管理API模块（异步版本）
# 修改说明：
# 1. 使用 async/await 关键字
# 2. 调用异步 Service 方法时使用 await
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from service.employee1 import EmploymentService
from schemas.employee1 import CreateEmployment, UpdateEmployment, EmploymentResponse
from core.database import get_db

router = APIRouter(prefix="/employment", tags=["就业模块"])


@router.get("/", response_model=dict)
async def get_all_api(
    skip: int = Query(0, description="分页偏移量"),
    limit: int = Query(10, description="每页条数"),
    student_name: str = Query(None, description="学生姓名"),
    company_name: str = Query(None, description="就业公司"),
    class_id: int = Query(None, description="班级ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    通过学生姓名模糊查询，就业公司模糊查询，班级id查询所有就业信息接口

    :param skip: 分页偏移量
    :param limit: 每页条数
    :param student_name: 学生姓名（模糊查询）
    :param company_name: 公司名称（模糊查询）
    :param class_id: 班级ID
    :param db: 异步数据库会话
    :return: 就业记录列表
    """
    total, items = await EmploymentService.get_all_service(
        db, skip, limit, student_name, company_name, class_id
    )
    return {
        "code": 200,
        "message": "查询成功",
        "total": total,
        "data": [EmploymentResponse.model_validate(item).model_dump() for item in items],
        "skip": skip,
        "limit": limit
    }


@router.get("/salary/range", response_model=dict)
async def get_emp_by_salary_range(
    salary_min: int = Query(..., description="最低薪资"),
    salary_max: int = Query(..., description="最高薪资"),
    db: AsyncSession = Depends(get_db)
):
    """
    按薪资区间查询就业信息

    :param salary_min: 最低薪资
    :param salary_max: 最高薪资
    :param db: 异步数据库会话
    :return: 薪资区间内的就业记录
    """
    emp_list = await EmploymentService.get_by_salary_range_service(db, salary_min, salary_max)
    return {
        "code": 200,
        "message": "查询成功",
        "data": [EmploymentResponse.model_validate(item).model_dump() for item in emp_list]
    }


@router.get("/statistics", response_model=dict)
async def get_employment_statistics(db: AsyncSession = Depends(get_db)):
    """
    就业统计接口

    :param db: 异步数据库会话
    :return: 统计数据
    """
    data = await EmploymentService.get_statistics_service(db)
    return {
        "code": 200,
        "message": "统计成功",
        "data": data
    }


@router.post("/", response_model=dict)
async def create_employment_api(data: CreateEmployment, db: AsyncSession = Depends(get_db)):
    """
    新增就业信息接口

    :param data: 就业数据
    :param db: 异步数据库会话
    :return: 创建结果
    """
    emp = await EmploymentService.create_employment_service(db, data)
    return {
        "code": 200,
        "message": "添加成功",
        "data": EmploymentResponse.model_validate(emp).model_dump()
    }


@router.get("/{student_no}", response_model=dict)
async def get_student_no_api(student_no: str, db: AsyncSession = Depends(get_db)):
    """
    通过学号查询单条信息接口

    :param student_no: 学号
    :param db: 异步数据库会话
    :return: 就业记录
    """
    emp = await EmploymentService.get_student_no_service(db, student_no)
    return {
        "code": 200,
        "message": "查询成功",
        "data": EmploymentResponse.model_validate(emp).model_dump()
    }


@router.put("/{employment_id}", response_model=dict)
async def update_employment_api(
    employment_id: int,
    data: UpdateEmployment,
    db: AsyncSession = Depends(get_db)
):
    """
    通过就业id查询并修改就业信息

    :param employment_id: 就业ID
    :param data: 更新数据
    :param db: 异步数据库会话
    :return: 修改结果
    """
    emp = await EmploymentService.update_employment_service(db, employment_id, data)
    return {
        "code": 200,
        "message": "修改成功",
        "data": EmploymentResponse.model_validate(emp).model_dump()
    }


@router.delete("/{employment_id}", response_model=dict)
async def delete_employment_api(employment_id: int, db: AsyncSession = Depends(get_db)):
    """
    通过就业id查询并删除学生就业信息

    :param employment_id: 就业ID
    :param db: 异步数据库会话
    :return: 删除结果
    """
    await EmploymentService.delete_employment_service(db, employment_id)
    return {"code": 200, "message": "删除成功", "data": None}


@router.put("/restore/{employment_id}", response_model=dict)
async def restore_employment_api(employment_id: int, db: AsyncSession = Depends(get_db)):
    """
    恢复删除的就业信息数据

    :param employment_id: 就业ID
    :param db: 异步数据库会话
    :return: 恢复结果
    """
    await EmploymentService.restore_employment_service(db, employment_id)
    return {"code": 200, "message": "恢复成功", "data": None}
