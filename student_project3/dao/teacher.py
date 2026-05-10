# 教师数据访问模块
# 修改说明：将所有函数改为 TeacherDao 类的 @staticmethod 方法
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.teacher import Teacher_Model
from schemas.teacher import TeacherCreate, TeacherUpdate


class TeacherDao:
    """教师数据访问类 - 使用 @staticmethod 统一调用"""

    @staticmethod
    def create_teacher(db: Session, t: TeacherCreate):
        """
        新增老师

        :param db: 数据库会话
        :param t: 教师数据
        :return: 创建的教师对象
        """
        db_tea = Teacher_Model(**t.model_dump())
        db.add(db_tea)
        db.commit()
        db.refresh(db_tea)
        return db_tea

    @staticmethod
    def update_teacher(db: Session, teacher_id: int, data: TeacherUpdate):
        """
        更新老师

        :param db: 数据库会话
        :param teacher_id: 教师ID
        :param data: 更新数据
        :return: 更新后的教师对象
        """
        tea = db.query(Teacher_Model).filter(
            Teacher_Model.teacher_id == teacher_id,
            Teacher_Model.is_deleted == 0
        ).first()
        if not tea:
            return None
        # 只更新传入的字段
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(tea, key, value)
        db.commit()
        db.refresh(tea)
        return tea

    @staticmethod
    def delete_teacher(db: Session, teacher_id: int):
        """
        逻辑删除老师

        :param db: 数据库会话
        :param teacher_id: 教师ID
        :return: 是否删除成功
        """
        tea = db.query(Teacher_Model).filter(
            Teacher_Model.teacher_id == teacher_id
        ).first()
        if not tea:
            return False
        tea.is_deleted = 1
        db.commit()
        return True

    @staticmethod
    def get_all_teachers(db: Session):
        """
        查询所有老师信息

        :param db: 数据库会话
        :return: 教师列表
        """
        teachers = db.query(Teacher_Model) \
                     .filter(Teacher_Model.is_deleted == 0) \
                     .all()
        return teachers

    @staticmethod
    def get_teacher_by_id(db: Session, teacher_id: int):
        """
        根据 ID 查询老师

        :param db: 数据库会话
        :param teacher_id: 教师ID
        :return: 教师对象
        """
        return db.query(Teacher_Model).filter(
            Teacher_Model.teacher_id == teacher_id,
            Teacher_Model.is_deleted == 0
        ).first()

    @staticmethod
    def get_teacher_by_conditions(db: Session, teacher_name=None, gender=None, page=1, page_size=10):
        """
        条件查询 + 分页

        :param db: 数据库会话
        :param teacher_name: 教师姓名
        :param gender: 性别
        :param page: 页码
        :param page_size: 每页条数
        :return: (总数, 教师列表)
        """
        q = db.query(Teacher_Model).filter(Teacher_Model.is_deleted == 0)
        if teacher_name:
            q = q.filter(Teacher_Model.teacher_name.like(f"%{teacher_name}%"))
        if gender:
            q = q.filter(Teacher_Model.gender == gender)
        total = q.count()
        data = q.offset((page - 1) * page_size).limit(page_size).all()
        return total, data

    @staticmethod
    def get_deleted_teachers(db: Session, page=1, page_size=10):
        """
        查询所有被删除的老师

        :param db: 数据库会话
        :param page: 页码
        :param page_size: 每页条数
        :return: (总数, 教师列表)
        """
        q = db.query(Teacher_Model).filter(Teacher_Model.is_deleted == 1)
        total = q.count()
        data = q.offset((page - 1) * page_size).limit(page_size).all()
        return total, data

    @staticmethod
    def restore_teacher(db: Session, teacher_id: int):
        """
        恢复已删除老师

        :param db: 数据库会话
        :param teacher_id: 教师ID
        :return: 恢复后的教师对象
        """
        tea = db.query(Teacher_Model).filter(
            Teacher_Model.teacher_id == teacher_id,
            Teacher_Model.is_deleted == 1
        ).first()
        if not tea:
            return None
        tea.is_deleted = 0
        db.commit()
        db.refresh(tea)
        return tea

    @staticmethod
    def get_teacher_stats(db: Session):
        """
        统计男女老师人数

        :param db: 数据库会话
        :return: 统计数据
        """
        result = db.query(
            Teacher_Model.gender,
            func.count(Teacher_Model.teacher_id)
        ).filter(
            Teacher_Model.is_deleted == 0
        ).group_by(
            Teacher_Model.gender
        ).all()

        # 处理结果
        stats = {"male_count": 0, "female_count": 0, "total": 0}
        for gender, count in result:
            stats['total'] += count
            if gender == '男':
                stats['male_count'] = count
            elif gender == '女':
                stats['female_count'] = count
        return stats
