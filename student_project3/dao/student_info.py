"""学生数据访问模块（异步版本）
# 修改说明：
# 1. 使用 AsyncSession 替代 Session
# 2. 所有数据库操作使用 await session.execute() 或 await session.scalars()
# 3. 保持 @staticmethod 风格
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from sqlalchemy.orm import selectinload
from models.student_info import Student
from schemas.student_info import StudentCreate, StudentUpdate


class StudentDao:
    """学生数据访问类（异步）"""

    @staticmethod
    async def create_student(db: AsyncSession, data: StudentCreate):
        """
        创建学生记录

        :param db: 异步数据库会话
        :param data: 学生数据
        :return: 创建的学生对象
        """
        db_stu = Student(**data.model_dump())
        db.add(db_stu)
        await db.commit()
        await db.refresh(db_stu)
        return db_stu

    @staticmethod
    async def get_student_by_id(db: AsyncSession, student_id: int):
        """
        根据ID查询学生

        :param db: 异步数据库会话
        :param student_id: 学生ID
        :return: 学生对象或None
        """
        stmt = select(Student).where(
            Student.id == student_id,
            Student.is_deleted == 0
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_student_list(
        db: AsyncSession,
        student_name: str = None,
        class_id: int = None,
        page: int = 1,
        page_size: int = 10
    ) -> tuple:
        """
        分页查询学生列表

        :param db: 异步数据库会话
        :param student_name: 学生姓名（模糊查询）
        :param class_id: 班级ID
        :param page: 页码
        :param page_size: 每页条数
        :return: (总数, 学生列表)
        """
        # 构建基础查询
        stmt = select(Student).where(Student.is_deleted == 0)

        if student_name:
            stmt = stmt.where(Student.student_name.contains(student_name))
        if class_id:
            stmt = stmt.where(Student.class_id == class_id)

        # 查询总数
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar()

        # 分页查询
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(stmt)
        data = result.scalars().all()

        return total, data

    @staticmethod
    async def update_student_by_id(db: AsyncSession, student_id: int, data: StudentUpdate):
        """
        根据ID更新学生信息

        :param db: 异步数据库会话
        :param student_id: 学生ID
        :param data: 更新数据
        :return: 更新后的学生对象或None
        """
        stmt = select(Student).where(
            Student.id == student_id,
            Student.is_deleted == 0
        )
        result = await db.execute(stmt)
        stu = result.scalar_one_or_none()

        if not stu:
            return None

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(stu, key, value)

        await db.commit()
        await db.refresh(stu)
        return stu

    @staticmethod
    async def delete_student_by_id(db: AsyncSession, student_id: int) -> bool:
        """
        逻辑删除学生

        :param db: 异步数据库会话
        :param student_id: 学生ID
        :return: 是否删除成功
        """
        stmt = select(Student).where(
            Student.id == student_id,
            Student.is_deleted == 0
        )
        result = await db.execute(stmt)
        stu = result.scalar_one_or_none()

        if not stu:
            return False

        stu.is_deleted = 1
        await db.commit()
        return True

    @staticmethod
    async def restore_student_by_id(db: AsyncSession, student_id: int) -> bool:
        """
        恢复已删除的学生

        :param db: 异步数据库会话
        :param student_id: 学生ID
        :return: 是否恢复成功
        """
        stmt = select(Student).where(
            Student.id == student_id,
            Student.is_deleted == 1
        )
        result = await db.execute(stmt)
        stu = result.scalar_one_or_none()

        if not stu:
            return False

        stu.is_deleted = 0
        await db.commit()
        return True

    @staticmethod
    async def get_deleted_student_list(
        db: AsyncSession,
        student_name: str = None,
        page: int = 1,
        page_size: int = 10
    ) -> tuple:
        """
        分页查询已删除的学生列表

        :param db: 异步数据库会话
        :param student_name: 学生姓名（模糊查询）
        :param page: 页码
        :param page_size: 每页条数
        :return: (总数, 学生列表)
        """
        stmt = select(Student).where(Student.is_deleted == 1)

        if student_name:
            stmt = stmt.where(Student.student_name.contains(student_name))

        # 查询总数
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar()

        # 分页查询
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(stmt)
        data = result.scalars().all()

        return total, data

    @staticmethod
    async def get_students_by_age(db: AsyncSession, age_threshold: int):
        """
        查询年龄超过指定阈值的学生

        :param db: 异步数据库会话
        :param age_threshold: 年龄阈值
        :return: 学生列表
        """
        stmt = select(Student).where(
            Student.is_deleted == 0,
            Student.age > age_threshold
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_gender_stats(db: AsyncSession, class_id: int = None):
        """
        统计班级学生性别分布

        :param db: 异步数据库会话
        :param class_id: 班级ID（可选）
        :return: 性别统计列表
        """
        stmt = select(
            Student.class_id.label("班级"),
            func.count(Student.id).label('班级总人数'),
            func.sum(case((Student.gender == "男", 1), else_=0)).label("男生人数"),
            func.sum(case((Student.gender == "女", 1), else_=0)).label("女生人数")
        ).where(Student.is_deleted == 0)

        if class_id:
            stmt = stmt.where(Student.class_id == class_id)

        stmt = stmt.group_by(Student.class_id)
        result = await db.execute(stmt)

        return [{
            "班级": item.班级,
            "班级总人数": item.班级总人数,
            "男生人数": item.男生人数,
            "女生人数": item.女生人数
        } for item in result.all()]
