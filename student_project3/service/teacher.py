"""教师服务模块（异步版本）
# 修改说明：
# 1. 使用 async/await 关键字
# 2. 调用异步 DAO 方法时使用 await
# 3. 保留原有业务逻辑判断
"""
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from dao.teacher import TeacherDao
from models.teacher import Teacher_Model
from schemas.teacher import TeacherCreate, TeacherUpdate


class TeacherService:
    """教师服务类（异步）"""

    @staticmethod
    async def get_all_teachers(db: AsyncSession):
        """
        查询所有老师

        :param db: 异步数据库会话
        :return: 教师列表
        """
        teachers = await TeacherDao.get_all_teachers(db)
        if not teachers:
            raise HTTPException(status_code=404, detail="数据库中暂无老师数据")
        return teachers

    @staticmethod
    async def get_teacher(db: AsyncSession, teacher_id: int):
        """
        按id查询老师

        :param db: 异步数据库会话
        :param teacher_id: 教师ID
        :return: 教师对象
        """
        tea = await TeacherDao.get_teacher_by_id(db, teacher_id)
        if not tea:
            raise HTTPException(status_code=404, detail="老师不存在")
        return tea

    @staticmethod
    async def get_teachers(
        db: AsyncSession,
        teacher_name=None,
        gender=None,
        page=1,
        page_size=10
    ):
        """
        按条件查询老师

        :param db: 异步数据库会话
        :param teacher_name: 教师姓名
        :param gender: 性别
        :param page: 页码
        :param page_size: 每页条数
        :return: (总数, 教师列表)
        """
        total, data = await TeacherDao.get_teacher_by_conditions(
            db, teacher_name, gender, page, page_size
        )
        if total == 0:
            raise HTTPException(status_code=404, detail="未找到符合条件的老师")
        return total, data

    @staticmethod
    async def create_teacher(db: AsyncSession, t: TeacherCreate):
        """
        新增老师

        :param db: 异步数据库会话
        :param t: 教师数据
        :return: 创建的教师对象
        """
        return await TeacherDao.create_teacher(db, t)

    @staticmethod
    async def update_teacher(db: AsyncSession, teacher_id: int, data: TeacherUpdate):
        """
        修改老师信息

        :param db: 异步数据库会话
        :param teacher_id: 教师ID
        :param data: 更新数据
        :return: 更新后的教师对象
        """
        tea = await TeacherDao.update_teacher(db, teacher_id, data)
        if not tea:
            raise HTTPException(status_code=404, detail="老师不存在，无法更新")
        return tea

    @staticmethod
    async def delete_teacher(db: AsyncSession, teacher_id: int):
        """
        删除老师

        :param db: 异步数据库会话
        :param teacher_id: 教师ID
        :return: 删除结果
        """
        stmt = select(Teacher_Model).where(Teacher_Model.teacher_id == teacher_id)
        result = await db.execute(stmt)
        tea = result.scalar_one_or_none()

        if not tea:
            raise HTTPException(status_code=404, detail="老师ID不存在")
        if tea.is_deleted == 1:
            raise HTTPException(status_code=400, detail="老师已被删除，无需重复删除")

        success = await TeacherDao.delete_teacher(db, teacher_id)
        if not success:
            raise HTTPException(status_code=500, detail="删除操作失败")
        return {"message": "删除成功"}

    @staticmethod
    async def get_deleted_teachers(db: AsyncSession, page=1, page_size=10):
        """
        查询被删除老师信息

        :param db: 异步数据库会话
        :param page: 页码
        :param page_size: 每页条数
        :return: (总数, 教师列表)
        """
        total, data = await TeacherDao.get_deleted_teachers(db, page, page_size)
        if total == 0:
            raise HTTPException(status_code=404, detail="未找到已删除的老师")
        return total, data

    @staticmethod
    async def restore_teacher(db: AsyncSession, teacher_id: int):
        """
        恢复老师

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
            raise HTTPException(status_code=404, detail="老师不存在或未被删除")

        restored_tea = await TeacherDao.restore_teacher(db, teacher_id)
        if not restored_tea:
            raise HTTPException(status_code=500, detail="恢复操作失败")
        return restored_tea

    @staticmethod
    async def get_stats(db: AsyncSession):
        """
        统计男女老师人数

        :param db: 异步数据库会话
        :return: 统计数据
        """
        return await TeacherDao.get_teacher_stats(db)
