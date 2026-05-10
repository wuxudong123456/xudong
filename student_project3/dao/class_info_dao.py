"""班级数据访问模块（异步版本）
# 修改说明：
# 1. 使用 AsyncSession 替代 Session
# 2. 所有数据库操作使用 await session.execute() 或 await session.scalars()
# 3. 使用 SQLAlchemy 2.0 select() 语法
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from models.class_info_models import ClassInfo
from schemas.class_info_schemas import ClassUpdate


class ClassInfoDao:
    """班级数据访问类（异步）"""

    @staticmethod
    async def get_all_classinfo(db: AsyncSession):
        """
        查询所有班级信息

        :param db: 异步数据库会话
        :return: 班级列表
        """
        stmt = select(ClassInfo).where(ClassInfo.is_deleted == 0)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_one_classinfo(db: AsyncSession, class_id: int):
        """
        查询单个班级信息

        :param db: 异步数据库会话
        :param class_id: 班级ID
        :return: 班级对象
        """
        stmt = select(ClassInfo).where(
            ClassInfo.class_id == class_id,
            ClassInfo.is_deleted == 0
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def post_add_class(cls: ClassUpdate, db: AsyncSession):
        """
        添加班级

        :param cls: 班级数据
        :param db: 异步数据库会话
        :return: 新增的班级对象
        """
        new_class = ClassInfo(**cls.model_dump())
        db.add(new_class)
        await db.commit()
        await db.refresh(new_class)
        return new_class

    @staticmethod
    async def put_update_classinfo(class_id: int, update_data, db: AsyncSession):
        """
        修改班级信息

        :param class_id: 班级ID
        :param update_data: 更新数据
        :param db: 异步数据库会话
        :return: 更新后的班级对象
        """
        # 查询数据库里的真实班级对象
        stmt = select(ClassInfo).where(
            ClassInfo.class_id == class_id,
            ClassInfo.is_deleted == 0
        )
        result = await db.execute(stmt)
        class_obj = result.scalar_one_or_none()

        if not class_obj:
            return None

        # 用前端数据更新数据库对象
        for k, v in update_data.model_dump(exclude_unset=True).items():
            setattr(class_obj, k, v)

        await db.commit()
        await db.refresh(class_obj)
        return class_obj

    @staticmethod
    async def delete_class(class_id: int, db: AsyncSession):
        """
        逻辑删除班级

        :param class_id: 班级ID
        :param db: 异步数据库会话
        :return: 删除结果
        """
        stmt = select(ClassInfo).where(ClassInfo.class_id == class_id)
        result = await db.execute(stmt)
        cls = result.scalar_one_or_none()

        if cls:
            cls.is_deleted = 1
            await db.commit()

        return {"msg": "删除成功"}

    @staticmethod
    async def restore_class(class_id: int, db: AsyncSession):
        """
        恢复逻辑删除数据

        :param class_id: 班级ID
        :param db: 异步数据库会话
        :return: 恢复结果
        """
        stmt = select(ClassInfo).where(ClassInfo.class_id == class_id)
        result = await db.execute(stmt)
        cls = result.scalar_one_or_none()

        if cls:
            cls.is_deleted = 0
            await db.commit()

        return {"msg": "恢复数据成功"}

    @staticmethod
    async def count_class_month(db: AsyncSession, month: str = None):
        """
        按年月统计每个月开班的班级数量

        :param db: 异步数据库会话
        :param month: 月份（可选）
        :return: 统计结果列表
        """
        # 基础查询
        stmt = select(
            func.DATE_FORMAT(ClassInfo.start_time, "%Y-%m").label("month"),
            func.count(ClassInfo.class_id).label("count"),
            func.group_concat(ClassInfo.class_name).label("class_names")
        ).where(ClassInfo.is_deleted == 0)

        # 如果传了月份，过滤
        if month:
            month_filter = month.strip('"').strip("'")
            stmt = stmt.where(
                func.DATE_FORMAT(ClassInfo.start_time, "%Y-%m") == month_filter
            )

        # 分组 + 排序
        stmt = stmt.group_by(func.DATE_FORMAT(ClassInfo.start_time, "%Y-%m")).order_by("month")
        result = await db.execute(stmt)

        return [{
            "month": row.month,
            "count": row.count,
            "class_names": row.class_names.split(",")
        } for row in result.all()]

    @staticmethod
    async def get_class_by_lecturer_id(db: AsyncSession, lecturer_id: int):
        """
        按上课老师id查他的上课班级名

        :param db: 异步数据库会话
        :param lecturer_id: 授课老师ID
        :return: 班级名称列表
        """
        stmt = select(ClassInfo.class_name).where(
            ClassInfo.lecturer_id == lecturer_id,
            ClassInfo.is_deleted == 0
        )
        result = await db.execute(stmt)
        return [row[0] for row in result.all()]
