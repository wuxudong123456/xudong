#导入模块
from sqlalchemy import func
from sqlalchemy.orm import Session
from models.class_info_models import ClassInfo
from schemas.class_info_schemas import ClassResp, ClassUpdate


#1查询所有班级信息:
def get_all_classinfo(db:Session):
    all_cls = db.query(ClassInfo).filter(ClassInfo.is_deleted == 0).all()
    return all_cls

#2查询单个班级学生信息：
def get_one_classinfo(db: Session,class_id: int):
    one_cls = db.query(ClassInfo).filter(ClassInfo.class_id == class_id, ClassInfo.is_deleted == 0).first()
    return one_cls

#3添加班级：
def post_add_class(cls:ClassUpdate,db:Session):
    new_class = ClassInfo(**cls.dict())
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return new_class

#4改班级信息：
def put_update_classinfo(class_id: int, update_data, db: Session):
    # 1. 查询数据库里的真实班级对象
    class_obj = db.query(ClassInfo).filter(ClassInfo.class_id == class_id, ClassInfo.is_deleted == 0).first()

    # 2. 用前端数据更新数据库对象
    for k, v in update_data.dict(exclude_unset=True).items():
        setattr(class_obj, k, v)
    db.commit()
    db.refresh(class_obj)  # 这里必须是数据库对象！
    return class_obj

#5逻辑删除：
def delete_class(class_id: int, db: Session):
    cls = db.query(ClassInfo).filter(ClassInfo.class_id == class_id).first()
    cls.is_deleted = 1
    db.commit()
    return {"msg": "删除成功"}

#6恢复逻辑删除数据：
def restore_class(class_id: int, db: Session):
    cls = db.query(ClassInfo).filter(ClassInfo.class_id == class_id).first()
    cls.is_deleted = 0
    db.commit()
    return {"msg": "恢复数据成功"}

#统计分析模块：
# 按年月统计每个月开班的班级数量:
def count_class_month(db: Session, month: str = None):
    # 1. 基础查询：按月分组，统计数量 + 班级名称列表
    query = db.query(
        func.DATE_FORMAT(ClassInfo.start_time, "%Y-%m").label("month"),  # 年月
        func.count(ClassInfo.class_id).label("count"),                  # 数量
        func.group_concat(ClassInfo.class_name).label("class_names")    # 班级名称（用逗号拼接）
    ).filter(ClassInfo.is_deleted == 0)

    # 2. 如果传了月份，过滤
    if month:
        query = query.filter(func.DATE_FORMAT(ClassInfo.start_time, "%Y-%m") == month.strip('"').strip("'"))

    # 3. 分组 + 排序
    result = query.group_by(
        func.DATE_FORMAT(ClassInfo.start_time, "%Y-%m")
    ).order_by("month").all()

    # 4. 返回：月份、数量、班级名称列表
    return [{ "month": row.month,
            "count": row.count,
            "class_names": row.class_names.split(",") } for row in result]

#按上课老师id查他的上课班级名：
def get_class_by_lecturer_id(db: Session,lecturer_id: int):
    result = db.query(ClassInfo.class_name).filter(ClassInfo.lecturer_id == lecturer_id, ClassInfo.is_deleted == 0).all()
    return [row.class_name for row in result]

