"""学生数据访问模块，处理学生数据的CRUD操作
# 修改说明：将所有函数改为 StudentDao 类的 @staticmethod 方法
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, case
from models.student_info import Student
from schemas.student_info import StudentCreate, StudentUpdate


class StudentDao:
    """学生数据访问类 - 使用 @staticmethod 统一调用"""

    @staticmethod
    def create_student(db: Session, data: StudentCreate):
        """
        创建学生记录

        :param db: 数据库会话
        :param data: 学生数据
        :return: 创建的学生对象
        """
        db_stu = Student(**data.model_dump())
        db.add(db_stu)
        db.commit()
        db.refresh(db_stu)
        return db_stu

    @staticmethod
    def get_student_by_id(db: Session, student_id: int):
        """
        根据ID查询学生

        :param db: 数据库会话
        :param student_id: 学生ID
        :return: 学生对象或None
        """
        return db.query(Student).filter(
            Student.id == student_id,
            Student.is_deleted == 0
        ).first()

    @staticmethod
    def get_student_list(
        db: Session,
        student_name: str = None,
        class_id: int = None,
        page: int = 1,
        page_size: int = 10
    ) -> tuple:
        """
        分页查询学生列表

        :param db: 数据库会话
        :param student_name: 学生姓名（模糊查询）
        :param class_id: 班级ID
        :param page: 页码
        :param page_size: 每页条数
        :return: (总数, 学生列表)
        """
        query = db.query(Student).filter(Student.is_deleted == 0)

        if student_name:
            query = query.filter(Student.student_name.contains(student_name))
        if class_id:
            query = query.filter(Student.class_id == class_id)

        total = query.count()
        data = query.offset((page - 1) * page_size).limit(page_size).all()
        return total, data

    @staticmethod
    def update_student_by_id(db: Session, student_id: int, data: StudentUpdate):
        """
        根据ID更新学生信息

        :param db: 数据库会话
        :param student_id: 学生ID
        :param data: 更新数据
        :return: 更新后的学生对象或None
        """
        stu = db.query(Student).filter(
            Student.id == student_id,
            Student.is_deleted == 0
        ).first()

        if not stu:
            return None

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(stu, key, value)

        db.commit()
        db.refresh(stu)
        return stu

    @staticmethod
    def delete_student_by_id(db: Session, student_id: int) -> bool:
        """
        逻辑删除学生

        :param db: 数据库会话
        :param student_id: 学生ID
        :return: 是否删除成功
        """
        stu = db.query(Student).filter(
            Student.id == student_id,
            Student.is_deleted == 0
        ).first()

        if not stu:
            return False

        stu.is_deleted = 1
        db.commit()
        return True

    @staticmethod
    def restore_student_by_id(db: Session, student_id: int) -> bool:
        """
        恢复已删除的学生

        :param db: 数据库会话
        :param student_id: 学生ID
        :return: 是否恢复成功
        """
        stu = db.query(Student).filter(
            Student.id == student_id,
            Student.is_deleted == 1
        ).first()

        if not stu:
            return False

        stu.is_deleted = 0
        db.commit()
        return True

    @staticmethod
    def get_deleted_student_list(
        db: Session,
        student_name: str = None,
        page: int = 1,
        page_size: int = 10
    ) -> tuple:
        """
        分页查询已删除的学生列表

        :param db: 数据库会话
        :param student_name: 学生姓名（模糊查询）
        :param page: 页码
        :param page_size: 每页条数
        :return: (总数, 学生列表)
        """
        query = db.query(Student).filter(Student.is_deleted == 1)

        if student_name:
            query = query.filter(Student.student_name.contains(student_name))

        total = query.count()
        data = query.offset((page - 1) * page_size).limit(page_size).all()
        return total, data

    @staticmethod
    def get_students_by_age(db: Session, age_threshold: int):
        """
        查询年龄超过指定阈值的学生

        :param db: 数据库会话
        :param age_threshold: 年龄阈值
        :return: 学生列表
        """
        return db.query(Student).filter(
            Student.is_deleted == 0,
            Student.age > age_threshold
        ).all()

    @staticmethod
    def get_gender_stats(db: Session, class_id: int = None):
        """
        统计班级学生性别分布

        :param db: 数据库会话
        :param class_id: 班级ID（可选）
        :return: 性别统计列表
        """
        query = db.query(
            Student.class_id.label("班级"),
            func.count(Student.id).label('班级总人数'),
            func.sum(case((Student.gender == "男", 1), else_=0)).label("男生人数"),
            func.sum(case((Student.gender == "女", 1), else_=0)).label("女生人数")
        ).filter(Student.is_deleted == 0)

        if class_id:
            query = query.filter(Student.class_id == class_id)

        query = query.group_by(Student.class_id).all()

        return [{
            "班级": item.班级,
            "班级总人数": item.班级总人数,
            "男生人数": item.男生人数,
            "女生人数": item.女生人数
        } for item in query]
