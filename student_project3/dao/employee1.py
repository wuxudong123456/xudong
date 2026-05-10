"""就业数据访问模块（异步版本）
# 修改说明：
# 1. 使用 AsyncSession 替代 Session
# 2. 所有数据库操作使用 await session.execute() 或 await session.scalars()
# 3. 使用 SQLAlchemy 2.0 select() 语法
# 4. 保持 @staticmethod 风格
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models.employee1 import Employment
from schemas.employee1 import CreateEmployment, UpdateEmployment


class EmploymentDao:
    """就业数据访问类（异步）"""

    @staticmethod
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        student_name: str = None,
        company_name: str = None,
        class_id: int = None
    ):
        """
        查询所有就业记录

        :param db: 异步数据库会话
        :param skip: 分页偏移量
        :param limit: 每页条数
        :param student_name: 学生姓名（模糊查询）
        :param company_name: 公司名称（模糊查询）
        :param class_id: 班级ID
        :return: (总数, 就业记录列表)
        """
        stmt = select(Employment).where(Employment.is_deleted == 0)

        if student_name:
            stmt = stmt.where(Employment.student_name.like(f"%{student_name}%"))
        if company_name:
            stmt = stmt.where(Employment.company_name.like(f"%{company_name}%"))
        if class_id is not None:
            stmt = stmt.where(Employment.class_id == class_id)

        # 查询总数
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar()

        # 分页查询
        stmt = stmt.offset(skip * limit).limit(limit)
        result = await db.execute(stmt)
        items = result.scalars().all()

        return total, items

    @staticmethod
    async def get_by_salary_range(db: AsyncSession, salary_min: int, salary_max: int):
        """
        按薪资区间查询

        :param db: 异步数据库会话
        :param salary_min: 最低薪资
        :param salary_max: 最高薪资
        :return: 就业记录列表
        """
        stmt = select(Employment).where(
            Employment.salary.between(salary_min, salary_max),
            Employment.is_deleted == 0
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_salary_top5(db: AsyncSession):
        """
        薪资top5

        :param db: 异步数据库会话
        :return: 薪资前五列表
        """
        stmt = select(Employment).where(
            Employment.is_deleted == 0,
            Employment.salary.isnot(None)
        ).order_by(Employment.salary.desc()).limit(5)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_class_avg(db: AsyncSession):
        """
        班级平均薪资

        :param db: 异步数据库会话
        :return: 班级平均薪资列表
        """
        stmt = select(
            Employment.class_id,
            func.avg(Employment.salary).label("avg_salary")
        ).where(
            Employment.is_deleted == 0,
            Employment.salary.isnot(None)
        ).group_by(Employment.class_id)
        result = await db.execute(stmt)
        return result.all()

    @staticmethod
    async def get_student_no_by(db: AsyncSession, student_no: str):
        """
        通过学号查询就业记录

        :param db: 异步数据库会话
        :param student_no: 学号
        :return: 就业记录
        """
        stmt = select(Employment).where(
            Employment.student_no == student_no,
            Employment.is_deleted == 0
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_employment_id_by(db: AsyncSession, employment_id: int):
        """
        通过就业id查询单条就业记录

        :param db: 异步数据库会话
        :param employment_id: 就业ID
        :return: 就业记录
        """
        stmt = select(Employment).where(
            Employment.employment_id == employment_id,
            Employment.is_deleted == 0
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_employment(db: AsyncSession, data: CreateEmployment):
        """
        新增就业数据

        :param db: 异步数据库会话
        :param data: 就业数据
        :return: 创建的就业记录
        """
        emp = Employment(**data.model_dump())
        db.add(emp)
        await db.commit()
        await db.refresh(emp)
        return emp

    @staticmethod
    async def update_employment(db: AsyncSession, employment_id: int, data: UpdateEmployment):
        """
        修改就业数据

        :param db: 异步数据库会话
        :param employment_id: 就业ID
        :param data: 更新数据
        """
        stmt = select(Employment).where(
            Employment.employment_id == employment_id,
            Employment.is_deleted == 0
        )
        result = await db.execute(stmt)
        emp = result.scalar_one_or_none()

        if emp:
            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(emp, key, value)
            await db.commit()

    @staticmethod
    async def delete_employment(db: AsyncSession, employment_id: int):
        """
        逻辑删除就业记录

        :param db: 异步数据库会话
        :param employment_id: 就业ID
        :return: 就业ID
        """
        stmt = select(Employment).where(Employment.employment_id == employment_id)
        result = await db.execute(stmt)
        emp = result.scalar_one_or_none()

        if emp:
            emp.is_deleted = 1
            await db.commit()

        return employment_id

    @staticmethod
    async def restore_employment(db: AsyncSession, employment_id: int):
        """
        恢复逻辑删除的数据

        :param db: 异步数据库会话
        :param employment_id: 就业ID
        :return: 恢复后的就业记录
        """
        stmt = select(Employment).where(Employment.employment_id == employment_id)
        result = await db.execute(stmt)
        emp = result.scalar_one_or_none()

        if not emp:
            return None

        emp.is_deleted = 0
        await db.commit()
        await db.refresh(emp)
        return emp
