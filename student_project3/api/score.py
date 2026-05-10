"""成绩管理API模块"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from schemas.score import Score_QQ, ScoreUpdate
from service.score import (
    add_score_service,
    get_scores_service,
    update_score_service,
    delete_score_service,
    restore_score_service,
    get_all_above_80_service,
    get_multiple_fail_service,
    get_class_avg_service
)

router = APIRouter(prefix="/scores", tags=["学生成绩"])


@router.post("/", response_model=dict, summary="添加成绩")
def add_score(score: Score_QQ, db: Session = Depends(get_db)):
    """
    添加单条成绩信息
    
    :param score: 成绩数据
    :param db: 数据库会话
    :return: 添加结果
    """
    result = add_score_service(db, score)
    return {"code": 200, "message": "添加成功", "data": result}


@router.get("/", response_model=dict, summary="综合查询成绩")
def get_scores(
    id: Optional[int] = Query(None, description="成绩ID", ge=1),
    student_no: Optional[str] = Query(None, description="学生学号", min_length=3, max_length=20),
    exam_order: Optional[int] = Query(None, description="考试序号", ge=1),
    page: int = Query(1, description="页码", ge=1),
    size: int = Query(10, description="每页条数", ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    综合查询成绩，支持按ID/学号/考试序号查询，支持分页
    
    :param id: 成绩ID
    :param student_no: 学生学号
    :param exam_order: 考试序号
    :param page: 页码
    :param size: 每页条数
    :param db: 数据库会话
    :return: 分页成绩数据
    """
    result = get_scores_service(db, id, student_no, exam_order, page, size)
    return {"code": 200, "message": "查询成功", "data": result}


@router.put("/{score_id}", response_model=dict, summary="修改成绩")
def update_score(score_id: int, update_data: ScoreUpdate, db: Session = Depends(get_db)):
    """
    修改成绩信息
    
    :param score_id: 成绩ID
    :param update_data: 更新数据
    :param db: 数据库会话
    :return: 修改结果
    """
    data = update_score_service(db, score_id, update_data)
    return {"code": 200, "message": "修改成功", "data": data}


@router.delete("/{score_id}", response_model=dict, summary="删除成绩")
def delete_score(score_id: int, db: Session = Depends(get_db)):
    """
    逻辑删除成绩
    
    :param score_id: 成绩ID
    :param db: 数据库会话
    :return: 删除结果
    """
    delete_score_service(db, score_id)
    return {"code": 200, "message": "删除成功", "data": None}


@router.put("/restore", response_model=dict, summary="恢复已删除成绩")
def restore_score(
    id: Optional[int] = Query(None, description="成绩ID"),
    student_no: Optional[str] = Query(None, description="学生学号"),
    exam_order: Optional[int] = Query(None, description="考试序号"),
    db: Session = Depends(get_db)
):
    """
    批量或单条恢复已删除的成绩
    
    :param id: 成绩ID（可选）
    :param student_no: 学生学号（可选）
    :param exam_order: 考试序号（可选）
    :param db: 数据库会话
    :return: 恢复结果
    """
    count = restore_score_service(db, id, student_no, exam_order)
    return {"code": 200, "message": f"恢复成功，共恢复 {count} 条", "data": count}


@router.get("/all-above-80", response_model=dict, summary="查询80分以上学生")
def all_above_80(db: Session = Depends(get_db)):
    """
    查询所有科目80分以上的学生
    
    :param db: 数据库会话
    :return: 符合条件的学生列表
    """
    data = get_all_above_80_service(db)
    return {"code": 200, "message": "查询成功", "data": data}


@router.get("/multiple-fail", response_model=dict, summary="查询不及格超过2次的学生")
def multiple_fail(db: Session = Depends(get_db)):
    """
    查询不及格次数超过2次的学生
    
    :param db: 数据库会话
    :return: 符合条件的学生列表
    """
    data = get_multiple_fail_service(db)
    return {"code": 200, "message": "查询成功", "data": data}


@router.get("/class-avg", response_model=dict, summary="查询班级平均分统计")
def class_avg(
    class_id: Optional[int] = Query(None, description="班级ID"),
    db: Session = Depends(get_db)
):
    """
    按考试+班级分组，统计各班级各考试的平均分
    
    :param class_id: 班级ID（可选）
    :param db: 数据库会话
    :return: 班级平均分统计
    """
    data = get_class_avg_service(db, class_id)
    return {"code": 200, "message": "查询成功", "data": data}