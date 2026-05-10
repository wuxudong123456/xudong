# 班级服务模块
# 修改说明：
# 1. 调用 ClassInfoDao 类方法
# 2. 保留原有业务逻辑判断
from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from dao.class_info_dao import ClassInfoDao
from models.class_info_models import ClassInfo


class ClassInfoService:
    """班级服务类 - 处理业务逻辑，调用 DAO 层"""

    @staticmethod
    def get_all_classinfo_service(db: Session):
        """
        获取所有班级信息

        :param db: 数据库会话
        :return: 班级列表
        """
        all_cls_service = ClassInfoDao.get_all_classinfo(db)
        if not all_cls_service:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="暂无班级数据")
        return all_cls_service

    @staticmethod
    def get_one_classinfo_service(db: Session, class_id: int):
        """
        查询单个班级学生信息

        :param db: 数据库会话
        :param class_id: 班级ID
        :return: 班级对象
        """
        one_cls_service = ClassInfoDao.get_one_classinfo(db, class_id)
        if not one_cls_service:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="暂无班级数据")
        return one_cls_service

    @staticmethod
    def post_add_class_service(db: Session, cls_data):
        """
        添加班级

        :param db: 数据库会话
        :param cls_data: 班级数据
        :return: 新增的班级对象
        """
        # 1. 判断班级名称是否重复
        exists = db.query(ClassInfo).filter(
            ClassInfo.class_name == cls_data.class_name,
            ClassInfo.is_deleted == 0
        ).first()

        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="班级名称已存在，不能重复添加"
            )

        # 2. 判断必填字段不为空
        if not cls_data.class_name:
            raise HTTPException(status_code=400, detail="班级名称不能为空")

        # 3. 调用 DAO 层添加
        return ClassInfoDao.post_add_class(cls_data, db)

    @staticmethod
    def put_update_class_service(db: Session, class_id: int, update_data):
        """
        修改班级信息

        :param db: 数据库会话
        :param class_id: 班级ID
        :param update_data: 更新数据
        :return: 更新后的班级对象
        """
        # 检查班级是否存在
        class_obj = db.query(ClassInfo).filter(
            ClassInfo.class_id == class_id,
            ClassInfo.is_deleted == 0
        ).first()
        if not class_obj:
            raise HTTPException(status_code=404, detail="班级不存在")
        # 调用 DAO
        return ClassInfoDao.put_update_classinfo(class_id, update_data, db)

    @staticmethod
    def delete_class_service(db: Session, class_id: int):
        """
        逻辑删除班级

        :param db: 数据库会话
        :param class_id: 班级ID
        :return: 删除结果
        """
        # 1. 先查询班级是否存在
        cls = db.query(ClassInfo).filter(
            ClassInfo.class_id == class_id,
            ClassInfo.is_deleted == 0
        ).first()

        # 2. 不存在就抛异常
        if not cls:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="班级不存在，无法删除"
            )

        # 3. 调用 DAO 执行删除
        return ClassInfoDao.delete_class(class_id, db)

    @staticmethod
    def restore_class_service(db: Session, class_id: int):
        """
        恢复逻辑删除数据

        :param db: 数据库会话
        :param class_id: 班级ID
        :return: 恢复结果
        """
        # 先查这条数据有没有（不管删没删）
        cls = db.query(ClassInfo).filter(ClassInfo.class_id == class_id).first()
        if not cls:
            raise HTTPException(status_code=404, detail="班级不存在")

        # 判断是否已经是正常状态，不用重复恢复
        if cls.is_deleted == 0:
            raise HTTPException(status_code=400, detail="该班级未被删除，无需恢复")
        return ClassInfoDao.restore_class(class_id, db)

    @staticmethod
    def count_class_month_service(db: Session, month: str = None):
        """
        按月统计班级数

        :param db: 数据库会话
        :param month: 月份（可选）
        :return: 统计数据
        """
        data = ClassInfoDao.count_class_month(db, month=month)
        if not data:
            raise HTTPException(status_code=404, detail="暂无数据")
        return data

    @staticmethod
    def get_class_by_lecturer_id_service(db: Session, lecturer_id: int):
        """
        按上课老师id查他的上课班级名

        :param db: 数据库会话
        :param lecturer_id: 授课老师ID
        :return: 班级名称列表
        """
        if not ClassInfoDao.get_class_by_lecturer_id(db, lecturer_id):
            raise HTTPException(status_code=404, detail="暂无班级数据")
        return ClassInfoDao.get_class_by_lecturer_id(db, lecturer_id)
