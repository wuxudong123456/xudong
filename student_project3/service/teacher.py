from fastapi import HTTPException
from sqlalchemy.orm import Session
from dao.teacher import *
from models.teacher import *
from schemas.teacher import TeacherUpdate

#查询所有老师的判断
def judge_get_all_teachers(db: Session):
    teachers = db.query(Teacher_Model) \
        .filter(Teacher_Model.is_deleted == 0) \
        .all()
    if not teachers:
        raise HTTPException(status_code=404, detail="数据库中暂无老师数据")
    return teachers
#按id查询的判断
def judge_get_teacher(db: Session, teacher_id: int):
    tea = get_teacher_by_id(db, teacher_id)
    if not tea:
        raise HTTPException(status_code=404, detail="老师不存在")
    return tea

#按条件查询的判断
def judge_get_teachers(db: Session, teacher_name=None, gender=None, page=1, page_size=10):
    total, data = get_teacher_by_conditions(db, teacher_name, gender, page, page_size)
    if total == 0:
        raise HTTPException(status_code=404, detail="未找到符合条件的老师")
    return total, data

#查询被删除老师信息的判断
def judge_get_deleted_teachers(db: Session, page=1, page_size=10):
    total, data = get_deleted_teachers(db, page, page_size)
    if total == 0:
        raise HTTPException(status_code=404, detail="未找到已删除的老师")
    return total, data

#修改信息的判断
def judge_update_teacher(db: Session, teacher_id: int, data: TeacherUpdate):
    tea = update_teacher(db, teacher_id, data)
    if not tea:
        raise HTTPException(status_code=404, detail="老师不存在，无法更新")
    return tea

#删除老师的判断
def judge_delete_teacher(db: Session, teacher_id: int):
    tea = db.query(Teacher_Model).filter(
        Teacher_Model.teacher_id == teacher_id
    ).first()
    if not tea:
        raise HTTPException(status_code=404, detail="老师ID不存在")
    if tea.is_deleted == 1:
        raise HTTPException(status_code=400, detail="老师已被删除，无需重复删除")
    success = delete_teacher(db, teacher_id)
    if not success:
        raise HTTPException(status_code=500, detail="删除操作失败")
    return {"message": "删除成功"}

#恢复老师的判断
def judge_restore_teacher(db: Session, teacher_id: int):
    tea = db.query(Teacher_Model).filter(
        Teacher_Model.teacher_id == teacher_id,
        Teacher_Model.is_deleted == 1
    ).first()
    if not tea:
        raise HTTPException(status_code=404, detail="老师不存在或未被删除")

    restored_tea = restore_teacher(db, teacher_id)
    if not restored_tea:
        raise HTTPException(status_code=500, detail="恢复操作失败")
    return restored_tea

#统计男女老师的判断
def judge_get_stats(db: Session):
    return get_teacher_stats(db)

