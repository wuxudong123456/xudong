"""教师数据访问模块（异步版本）
# 修改说明：
# 1. 使用 AsyncSession 替代 Session
# 2. 所有数据库操作使用 await session.execute() 或 await session.scalars()
# 3. 使用 SQLAlchemy 2.0 select() 语法
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models.teacher import Teacher_Model
from schemas.teacher import TeacherCreate, TeacherUpdate


class TeacherDao:
    """教师数据访问类（异步）"""

    @staticmethod
    async def create_teacher(db: AsyncSession, t: TeacherCreate):
        """
        新增老师

        :param db: 异步数据库会话
        :param t: 教师数据
        :return: 创建的教师对象
        """
        db_tea = Teacher_Model(**t.model_dump())
        db.add(db_tea)
        await db.commit()
        await db.refresh(db_tea)
        return db_tea

    @staticmethod
    async def update_teacher(db: AsyncSession, teacher_id: int, data: TeacherUpdate):
        """
        更新老师

        :param db: 异步数据库会话
        :param teacher_id: 教师ID
        :param data: 更新数据
        :return: 更新后的教师对象
        """
        stmt = select(Teacher_Model).where(
            Teacher_Model.teacher_id == teacher_id,
            Teacher_Model.is_deleted == 0
        )
        result = await db.execute(stmt)
        tea = result.scalar_one_or_none()

        if not tea:
            return None

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(tea, key, value)

        await db.commit()
        await db.refresh(tea)
        return tea

    @staticmethod
    async def delete_teacher(db: AsyncSession, teacher_id: int):
        """
        逻辑删除老师

        :param db: 异步数据库会话
        :param teacher_id: 教师ID
        :return: 是否删除成功
        """
        stmt = select(Teacher_Model).where(Teacher_Model.teacher_id == teacher_id)
        result = await db.execute(stmt)
        tea = result.scalar_one_or_none()

        if not tea:
            return False

        tea.is_deleted = 1
        await db.commit()
        return True

    @staticmethod
    async def get_all_teachers(db: AsyncSession):
        """
        查询所有老师信息

        :param db: 异步数据库会话
        :return: 教师列表
        """
        stmt = select(Teacher_Model).where(Teacher_Model.is_deleted == 0)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_teacher_by_id(db: AsyncSession, teacher_id: int):
        """
        根据 ID 查询老师

        :param db: 异步数据库会话
        :param teacher_id: 教师ID
        :return: 教师对象
        """
        stmt = select(Teacher_Model).where(
            Teacher_Model.teacher_id == teacher_id,
            Teacher_Model.is_deleted == 0
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_teacher_by_conditions(
        db: AsyncSession,
        teacher_name=None,
        gender=None,
        page=1,
        page_size=10
    ):
        """
        条件查询 + 分页

        :param db: 异步数据库会话
        :param teacher_name: 教师姓名
        :param gender: 性别
        :param page: 页码
        :param page_size: 每页条数
        :return: (总数, 教师列表)
        """
        stmt = select(Teacher_Model).where(Teacher_Model.is_deleted == 0)

        if teacher_name:
            stmt = stmt.where(Teacher_Model.teacher_name.like(f"%{teacher_name}%"))
        if gender:
            stmt = stmt.where(Teacher_Model.gender == gender)

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
    async def get_deleted_teachers(db: AsyncSession, page=1, page_size=10):
        """
        查询所有被删除的老师

        :param db: 异步数据库会话
        :param page: 页码
        :param page_size: 每页条数
        :return: (总数, 教师列表)
        """
        stmt = select(Teacher_Model).where(Teacher_Model.is_deleted == 1)

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
    async def restore_teacher(db: AsyncSession, teacher_id: int):
        """
        恢复已删除老师

        :param db: 异步数据库会话
        :param teacher_id: 教师ID
        :return: 恢复后的教师对象
        """
        stmt = select(Teacher_Model).where(
            Teacher_Model.teacher_id == teacher_id,
            Teacher_Model.is_deleted == 1
        )
        result = await db.execute(stmt)
        tea = result.scalar_one_or_none()

        if not tea:
            return None

        tea.is_deleted = 0
        await db.commit()
        await db.refresh(tea)
        return tea

    @staticmethod
    async def get_teacher_stats(db: AsyncSession):
        """
        统计男女老师人数

        :param db: 异步数据库会话
        :return: 统计数据
        """
        stmt = select(
            Teacher_Model.gender,
            func.count(Teacher_Model.teacher_id)
        ).where(
            Teacher_Model.is_deleted == 0
        ).group_by(Teacher_Model.gender)

        result = await db.execute(stmt)

        stats = {"male_count": 0, "female_count": 0, "total": 0}
        for gender, count in result.all():
            stats['total'] += count
            if gender == '男':
                stats['male_count'] = count
            elif gender == '女':
                stats['female_count'] = count

        return stats
