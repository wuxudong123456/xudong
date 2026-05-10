from fastapi import HTTPException
from dao.score import *
from models.score import Score_DB
from schemas.score import Score_QQ, ScoreUpdate

# 添加成绩业务逻辑（先判断 学号+序次 是否重复）
def add_score_service(db, score: Score_QQ):
    # 1. 先查询：同一学生 + 同一考试序次 是否已经存在
    exists = db.query(Score_DB).filter(
        Score_DB.student_no == score.student_no,  # 学号相同
        Score_DB.exam_order == score.exam_order,   # 考试序次相同
        Score_DB.is_deleted == 0                   # 未删除的数据
    ).first()
    # 2. 如果存在 → 直接抛 HTTP 异常
    if exists:
        raise HTTPException(
            status_code=409,
            detail="该学生此考试成绩已存在，不可重复添加"
        )
    # 3. 不存在 → 调用 dao 添加
    return add_score_dao(db, score)

# 格式化成绩列表：统一返回前端需要的结构
def format_score_list(score_list):
    # 遍历成绩列表，转换为前端需要的字典格式
    return [
        {
            "id": s.id,
            "student_no": s.student_no,
            "exam_order": s.exam_order,
            "score": float(s.score) if s.score else None
        }
        for s in score_list
    ]

# 综合查询成绩业务逻辑
def get_scores_service(db, id, student_no, exam_order, page, size):
    # 1. 参数处理：保证页码和条数合法
    page = max(1, page)
    size = max(1, min(size, 50))
    # 2. 调用 dao 查询
    data_list, total = get_comprehensive_scores(db, id, student_no, exam_order, page, size)
    # 3. 格式化数据
    result_data = format_score_list(data_list)
    # 4. 返回统一结构
    return {
        "code": 200,
        "message": "查询成功" if result_data else "暂无成绩数据",
        "data": result_data,
        "total": total,
        "page": page,
        "size": size
    }

# 修改成绩的业务逻辑：校验数据是否存在
def update_score_service(db, id: int, data: ScoreUpdate):
    # 调用dao层修改数据
    item = update_score_dao(db, id, data)
    # 如果数据不存在，抛出404异常
    if not item:
        raise HTTPException(status_code=404, detail="成绩不存在")
    # 返回修改后的数据
    return item

# 删除成绩的业务逻辑：校验数据是否存在
def delete_score_service(db, id: int):
    # 调用dao层删除数据
    item = delete_score_dao(db, id)
    # 如果数据不存在，抛出404异常
    if not item:
        raise HTTPException(status_code=404, detail="成绩不存在")
    # 返回成功标记
    return True

# 多条件模糊查询 → 批量/单条恢复成绩
def restore_score_service(db: Session, id: int = None, student_no: str = None, exam_order: int = None):
    # 1. 调用DAO：只查询【已删除】的数据
    score_list = get_deleted_scores_dao(db, id=id, student_no=student_no, exam_order=exam_order)
    # 2. 业务校验
    if not score_list:
        raise HTTPException(status_code=404, detail="未找到任何已删除的成绩数据")
    # 3. 批量恢复（同时支持单条/多条）
    restore_count = 0
    for score in score_list:
        score.is_deleted = 0  # 恢复
        restore_count += 1
    # 4. 提交事务
    db.commit()
    # 5. 返回结果
    return restore_count

# 判断80分以上学生是否存在，不存在抛出异常
def get_all_above_80_service(db):
    data = get_all_above_80_dao(db)
    if not data:
        raise HTTPException(status_code=404, detail="暂无80分以上学生")
    return data

# 判断不及格超过2次的学生是否存在，不存在抛出异常
def get_multiple_fail_service(db):
    data = get_multiple_fail_dao(db)
    if not data:
        raise HTTPException(status_code=404, detail="暂无不及格超过2次的学生")
    return data

# 判断班级成绩是否存在，不存在抛出异常
def get_class_avg_service(db,class_id):
    data = get_class_avg_dao(db,class_id)  # 调用dao
    if not data:  # 判断：没数据
        raise HTTPException(status_code=404, detail="暂无考试成绩数据")
    return data  # 有数据 → 原样返回