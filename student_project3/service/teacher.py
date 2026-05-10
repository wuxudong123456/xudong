# 教师服务模块
# 修改说明：
# 1. 调用 TeacherDao 类方法
# 2. 保留原有业务逻辑判断
from fastapi import HTTPException
from sqlalchemy.orm import Session
from dao.teacher import TeacherDao
from models.teacher import Teacher_Model
from schemas.teacher import TeacherCreate, TeacherUpdate


class TeacherService:
    """教师服务类 - 处理业务逻辑，调用 DAO 层"""

    @staticmethod
    def get_all_teachers(db: Session):
        """
        查询所有老师

        :param db: 数据库会话
        :return: 教师列表
        """
        teachers = TeacherDao.get_all_teachers(db)
        if not teachers:
            raise HTTPException(status_code=404, detail="数据库中暂无老师数据")
        return teachers

    @staticmethod
    def get_teacher(db: Session, teacher_id: int):
        """
        按id查询老师

        :param db: 数据库会话
        :param teacher_id: 教师ID
        :return: 教师对象
        """
        tea = TeacherDao.get_teacher_by_id(db, teacher_id)
        if not tea:
            raise HTTPException(status_code=404, detail="老师不存在")
        return tea

    @staticmethod
    def get_teachers(db: Session, teacher_name=None, gender=None, page=1, page_size=10):
        """
        按条件查询老师

        :param db: 数据库会话
        :param teacher_name: 教师姓名
        :param gender: 性别
        :param page: 页码
        :param page_size: 每页条数
        :return: (总数, 教师列表)
        """
        total, data = TeacherDao.get_teacher_by_conditions(db, teacher_name, gender, page, page_size)
        if total == 0:
            raise HTTPException(status_code=404, detail="未找到符合条件的老师")
        return total, data

    @staticmethod
    def create_teacher(db: Session, t: TeacherCreate):
        """
        新增老师

        :param db: 数据库会话
        :param t: 教师数据
        :return: 创建的教师对象
        """
        return TeacherDao.create_teacher(db, t)

    @staticmethod
    def update_teacher(db: Session, teacher_id: int, data: TeacherUpdate):
        """
        修改老师信息

        :param db: 数据库会话
        :param teacher_id: 教师ID
        :param data: 更新数据
        :return: 更新后的教师对象
        """
        tea = TeacherDao.update_teacher(db, teacher_id, data)
        if not tea:
            raise HTTPException(status_code=404, detail="老师不存在，无法更新")
        return tea

    @staticmethod
    def delete_teacher(db: Session, teacher_id: int):
        """
        删除老师

        :param db: 数据库会话
        :param teacher_id: 教师ID
        :return: 删除结果
        """
        tea = db.query(Teacher_Model).filter(
            Teacher_Model.teacher_id == teacher_id
        ).first()
        if not tea:
            raise HTTPException(status_code=404, detail="老师ID不存在")
        if tea.is_deleted == 1:
            raise HTTPException(status_code=400, detail="老师已被删除，无需重复删除")
        success = TeacherDao.delete_teacher(db, teacher_id)
        if not success:
            raise HTTPException(status_code=500, detail="删除操作失败")
        return {"message": "删除成功"}

    @staticmethod
    def get_deleted_teachers(db: Session, page=1, page_size=10):
        """
        查询被删除老师信息

        :param db: 数据库会话
        :param page: 页码
        :param page_size: 每页条数
        :return: (总数, 教师列表)
        """
        total, data = TeacherDao.get_deleted_teachers(db, page, page_size)
        if total == 0:
            raise HTTPException(status_code=404, detail="未找到已删除的老师")
        return total, data

    @staticmethod
    def restore_teacher(db: Session, teacher_id: int):
        """
        恢复老师

        :param db: 数据库会话
        :param teacher_id: 教师ID
        :return: 恢复后的教师对象
        """
        tea = db.query(Teacher_Model).filter(
            Teacher_Model.teacher_id == teacher_id,
            Teacher_Model.is_deleted == 1
        ).first()
        if not tea:
            raise HTTPException(status_code=404, detail="老师不存在或未被删除")

        restored_tea = TeacherDao.restore_teacher(db, teacher_id)
        if not restored_tea:
            raise HTTPException(status_code=500, detail="恢复操作失败")
        return restored_tea

    @staticmethod
    def get_stats(db: Session):
        """
        统计男女老师人数

        :param db: 数据库会话
        :return: 统计数据
        """
        return TeacherDao.get_teacher_stats(db)
