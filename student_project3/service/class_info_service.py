
from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from dao.class_info_dao import get_all_classinfo, get_one_classinfo, put_update_classinfo, post_add_class, delete_class, \
    restore_class, count_class_month, get_class_by_lecturer_id
from models.class_info_models import ClassInfo


#所有班级信息：
def get_all_classinfo_service(db:Session):
    # 1. 调用dao层查询数据
    all_cls_service = get_all_classinfo(db)
    if not all_cls_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="暂无班级数据")
    return all_cls_service

#查询单个班级学生信息：
def get_one_classinfo_service(db:Session,class_id:int):
    one_cls_service = get_one_classinfo(db,class_id)
    if not one_cls_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="暂无班级数据")
    return one_cls_service

#添加班级：
def post_add_class_service(db: Session, cls_data):
    # 1. 判断班级名称是否重复
    exists = db.query(ClassInfo).filter(ClassInfo.class_name == cls_data.class_name,ClassInfo.is_deleted == 0).first()

    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="班级名称已存在，不能重复添加" )

    # 2. 判断必填字段不为空
    if not cls_data.class_name:
        raise HTTPException(status_code=400, detail="班级名称不能为空")

    # 3. 调用 DAO 层添加
    return post_add_class(cls_data, db)

# 修改班级:
def put_update_class_service(db: Session, class_id: int, update_data):
    # 检查班级是否存在
    class_obj = db.query(ClassInfo).filter(ClassInfo.class_id == class_id, ClassInfo.is_deleted == 0).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="班级不存在")
    # 调用 DAO
    return put_update_classinfo(class_id, update_data, db)

#逻辑删除：
def delete_class_service(db: Session, class_id: int):
  # 1. 先查询班级是否存在
    cls = db.query(ClassInfo).filter( ClassInfo.class_id == class_id,ClassInfo.is_deleted == 0 ).first()

    # 2. 不存在就抛异常
    if not cls:
        raise HTTPException( status_code=status.HTTP_404_NOT_FOUND, detail="班级不存在，无法删除")

    # 3. 调用 DAO 执行删除
    return delete_class(class_id, db)

#恢复逻辑删除数据：
def restore_class_service(db: Session, class_id: int):
    # 先查这条数据有没有（不管删没删）
    cls = db.query(ClassInfo).filter(ClassInfo.class_id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="班级不存在")

    # 判断是否已经是正常状态，不用重复恢复
    if cls.is_deleted == 0:
        raise HTTPException(status_code=400, detail="该班级未被删除，无需恢复")
    return restore_class(class_id, db)

# 按月统计班级数 service
def count_class_month_service(db: Session, month: str = None):
    data = count_class_month(db, month=month)  # 把 month 传给 DAO
    if not data:
        raise HTTPException(status_code=404, detail="暂无数据")
    return data

#按上课老师id查他的上课班级名：
def get_class_by_lecturer_id_service(db: Session,lecturer_id: int):
    if not get_class_by_lecturer_id(db, lecturer_id):
        raise HTTPException(status_code=404, detail="暂无班级数据")
    return get_class_by_lecturer_id(db,lecturer_id)