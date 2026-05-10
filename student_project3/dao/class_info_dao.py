# 班级数据访问模块
# 修改说明：将所有函数改为 ClassInfoDao 类的 @staticmethod 方法
from sqlalchemy import func
from sqlalchemy.orm import Session
from models.class_info_models import ClassInfo
from schemas.class_info_schemas import ClassResp, ClassUpdate


class ClassInfoDao:
    """班级数据访问类 - 使用 @staticmethod 统一调用"""

    @staticmethod
    def get_all_classinfo(db: Session):
        """
        查询所有班级信息

        :param db: 数据库会话
        :return: 班级列表
        """
        all_cls = db.query(ClassInfo).filter(ClassInfo.is_deleted == 0).all()
        return all_cls

    @staticmethod
    def get_one_classinfo(db: Session, class_id: int):
        """
        查询单个班级学生信息

        :param db: 数据库会话
        :param class_id: 班级ID
        :return: 班级对象
        """
        one_cls = db.query(ClassInfo).filter(
            ClassInfo.class_id == class_id,
            ClassInfo.is_deleted == 0
        ).first()
        return one_cls

    @staticmethod
    def post_add_class(cls: ClassUpdate, db: Session):
        """
        添加班级

        :param cls: 班级数据
        :param db: 数据库会话
        :return: 新增的班级对象
        """
        new_class = ClassInfo(**cls.model_dump())
        db.add(new_class)
        db.commit()
        db.refresh(new_class)
        return new_class

    @staticmethod
    def put_update_classinfo(class_id: int, update_data, db: Session):
        """
        修改班级信息

        :param class_id: 班级ID
        :param update_data: 更新数据
        :param db: 数据库会话
        :return: 更新后的班级对象
        """
        # 1. 查询数据库里的真实班级对象
        class_obj = db.query(ClassInfo).filter(
            ClassInfo.class_id == class_id,
            ClassInfo.is_deleted == 0
        ).first()

        # 2. 用前端数据更新数据库对象
        for k, v in update_data.model_dump(exclude_unset=True).items():
            setattr(class_obj, k, v)
        db.commit()
        db.refresh(class_obj)
        return class_obj

    @staticmethod
    def delete_class(class_id: int, db: Session):
        """
        逻辑删除班级

        :param class_id: 班级ID
        :param db: 数据库会话
        :return: 删除结果
        """
        cls = db.query(ClassInfo).filter(ClassInfo.class_id == class_id).first()
        cls.is_deleted = 1
        db.commit()
        return {"msg": "删除成功"}

    @staticmethod
    def restore_class(class_id: int, db: Session):
        """
        恢复逻辑删除数据

        :param class_id: 班级ID
        :param db: 数据库会话
        :return: 恢复结果
        """
        cls = db.query(ClassInfo).filter(ClassInfo.class_id == class_id).first()
        cls.is_deleted = 0
        db.commit()
        return {"msg": "恢复数据成功"}

    @staticmethod
    def count_class_month(db: Session, month: str = None):
        """
        按年月统计每个月开班的班级数量

        :param db: 数据库会话
        :param month: 月份（可选）
        :return: 统计结果列表
        """
        # 1. 基础查询：按月分组，统计数量 + 班级名称列表
        query = db.query(
            func.DATE_FORMAT(ClassInfo.start_time, "%Y-%m").label("month"),
            func.count(ClassInfo.class_id).label("count"),
            func.group_concat(ClassInfo.class_name).label("class_names")
        ).filter(ClassInfo.is_deleted == 0)

        # 2. 如果传了月份，过滤
        if month:
            query = query.filter(
                func.DATE_FORMAT(ClassInfo.start_time, "%Y-%m") == month.strip('"').strip("'")
            )

        # 3. 分组 + 排序
        result = query.group_by(
            func.DATE_FORMAT(ClassInfo.start_time, "%Y-%m")
        ).order_by("month").all()

        # 4. 返回：月份、数量、班级名称列表
        return [{
            "month": row.month,
            "count": row.count,
            "class_names": row.class_names.split(",")
        } for row in result]

    @staticmethod
    def get_class_by_lecturer_id(db: Session, lecturer_id: int):
        """
        按上课老师id查他的上课班级名

        :param db: 数据库会话
        :param lecturer_id: 授课老师ID
        :return: 班级名称列表
        """
        result = db.query(ClassInfo.class_name).filter(
            ClassInfo.lecturer_id == lecturer_id,
            ClassInfo.is_deleted == 0
        ).all()
        return [row.class_name for row in result]
