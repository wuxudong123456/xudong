"""就业服务模块（异步版本）
# 修改说明：
# 1. 使用 async/await 关键字
# 2. 调用异步 DAO 方法时使用 await
# 3. 保留原有业务逻辑判断
"""
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from dao.employee1 import EmploymentDao
from schemas.employee1 import EmploymentResponse, CreateEmployment, UpdateEmployment


class EmploymentService:
    """就业服务类（异步）"""

    @staticmethod
    async def get_all_service(
        db: AsyncSession,
        skip: int,
        limit: int,
        student_name: str,
        company_name: str,
        class_id: int
    ):
        """
        分页查询所有就业记录

        :param db: 异步数据库会话
        :param skip: 分页偏移量
        :param limit: 每页条数
        :param student_name: 学生姓名（模糊查询）
        :param company_name: 公司名称（模糊查询）
        :param class_id: 班级ID
        :return: 就业记录列表
        """
        return await EmploymentDao.get_all(
            db, skip, limit, student_name, company_name, class_id
        )

    @staticmethod
    async def get_by_salary_range_service(
        db: AsyncSession,
        salary_min: int,
        salary_max: int
    ):
        """
        按薪资区间查询就业记录

        :param db: 异步数据库会话
        :param salary_min: 最低薪资
        :param salary_max: 最高薪资
        :return: 薪资区间内的就业记录列表
        """
        emp_list = await EmploymentDao.get_by_salary_range(db, salary_min, salary_max)
        if not emp_list:
            raise HTTPException(404, "该薪资区间暂无就业信息")
        return emp_list

    @staticmethod
    async def get_statistics_service(db: AsyncSession):
        """
        获取就业统计数据

        :param db: 异步数据库会话
        :return: 包含薪资前五和班级平均薪资的统计数据
        """
        # 薪资前五
        top5 = await EmploymentDao.get_salary_top5(db)

        # 班级平均薪资
        class_avg_salary = await EmploymentDao.get_class_avg(db)

        # 把获取的class_avg_salary平均薪资遍历并添加到空列表中
        class_result = []
        for item in class_avg_salary:
            class_result.append({
                "class_id": item.class_id,
                "avg_salary": float(item.avg_salary) if item.avg_salary else 0
            })

        return {
            "salary_top5": [EmploymentResponse.model_validate(i).model_dump() for i in top5],
            "class_average_salary": class_result
        }

    @staticmethod
    async def get_student_no_service(db: AsyncSession, student_no: str):
        """
        通过学号查询就业记录

        :param db: 异步数据库会话
        :param student_no: 学生学号
        :return: 就业记录
        """
        emp = await EmploymentDao.get_student_no_by(db, student_no)
        if not emp:
            raise HTTPException(404, "学生不存在")
        return emp

    @staticmethod
    async def get_employment_id_service(db: AsyncSession, employment_id: int):
        """
        通过就业ID查询单条就业记录

        :param db: 异步数据库会话
        :param employment_id: 就业记录ID
        :return: 就业记录
        """
        return await EmploymentDao.get_employment_id_by(db, employment_id)

    @staticmethod
    async def create_employment_service(db: AsyncSession, data: CreateEmployment):
        """
        新增就业数据

        :param db: 异步数据库会话
        :param data: 就业数据
        :return: 创建的就业记录
        """
        exist = await EmploymentDao.get_student_no_by(db, data.student_no)
        if exist:
            raise HTTPException(409, "就业信息已存在")
        return await EmploymentDao.create_employment(db, data)

    @staticmethod
    async def update_employment_service(
        db: AsyncSession,
        employment_id: int,
        data: UpdateEmployment
    ):
        """
        修改就业数据

        :param db: 异步数据库会话
        :param employment_id: 就业记录ID
        :param data: 更新数据
        :return: 更新后的就业记录
        """
        emp = await EmploymentDao.get_employment_id_by(db, employment_id)
        if not emp:
            raise HTTPException(404, "就业记录不存在")
        await EmploymentDao.update_employment(db, employment_id, data)
        return await EmploymentDao.get_employment_id_by(db, employment_id)

    @staticmethod
    async def delete_employment_service(db: AsyncSession, employment_id: int):
        """
        逻辑删除就业记录

        :param db: 异步数据库会话
        :param employment_id: 就业记录ID
        :return: 删除结果
        """
        emp = await EmploymentDao.get_employment_id_by(db, employment_id)
        if not emp:
            raise HTTPException(404, "就业记录不存在")
        await EmploymentDao.delete_employment(db, employment_id)
        return {"code": 200, "message": "删除成功", "data": employment_id}

    @staticmethod
    async def restore_employment_service(db: AsyncSession, employment_id: int):
        """
        恢复逻辑删除的就业记录

        :param db: 异步数据库会话
        :param employment_id: 就业记录ID
        :return: 恢复后的就业记录
        """
        emp = await EmploymentDao.restore_employment(db, employment_id)
        if not emp:
            raise HTTPException(status_code=404, detail="就业信息不存在，无法恢复")
        return emp
