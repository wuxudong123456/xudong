from sqlalchemy import func
from sqlalchemy.orm import Session

from models.score import Score_DB
from models.student_info import Student
from schemas.score import Score_QQ, ScoreUpdate
# 从集合模块导入默认字典，自动为不存在的键初始化空值
from collections import defaultdict

# 添加成绩数据访问层方法：操作数据库添加成绩
def add_score_dao(db: Session, score: Score_QQ):
    # 创建成绩数据库对象，is_deleted=0表示未删除
    item = Score_DB(**score.model_dump(), is_deleted=0)
    # 将对象添加到数据库会话
    db.add(item)
    # 提交事务，保存到数据库
    db.commit()
    # 刷新对象，同步数据库最新数据
    db.refresh(item)
    # 返回添加后的成绩数据
    return item

# 综合查询数据访问层方法：多条件+分页查询成绩
def get_comprehensive_scores(db: Session, id=None, student_no=None, exam_order=None, page=1, size=10):
    # 基础查询：查询未删除的成绩数据
    q = db.query(Score_DB).filter(Score_DB.is_deleted == 0)
    # ID 模糊查询
    if id:
        q = q.filter(Score_DB.id.like(f"%{id}%"))
    # 学号 模糊查询
    if student_no:
        q = q.filter(Score_DB.student_no.like(f"%{student_no}%"))
    # 考试序号 模糊查询
    if exam_order:
        q = q.filter(Score_DB.exam_order.like(f"%{exam_order}%"))
    # 查询总条数
    total = q.count()
    # 分页查询：偏移量+限制条数
    data_list = q.offset((page - 1) * size).limit(size).all()
    # 返回查询结果列表和总条数
    return data_list, total


# 修改成绩数据访问层方法：根据id修改成绩分数
def update_score_dao(db: Session, id: int, data: ScoreUpdate):
    # 查询指定id且未删除的成绩数据
    item = db.query(Score_DB).filter_by(id=id, is_deleted=0).first()
    # 如果数据存在
    if item:
        # 修改成绩分数
        item.score = data.score
        # 提交事务
        db.commit()
        # 刷新对象
        db.refresh(item)
    # 返回修改后的数据（不存在返回None）
    return item

# 删除成绩数据访问层方法：逻辑删除（修改删除标记）
def delete_score_dao(db: Session, id: int):
    # 查询指定id且未删除的成绩数据
    item = db.query(Score_DB).filter_by(id=id, is_deleted=0).first()
    # 如果数据存在
    if item:
        # 设置删除标记为1（已删除）
        item.is_deleted = 1
        # 提交事务
        db.commit()
    # 返回删除后的数据（不存在返回None）
    return item

# 多条件模糊查询【已删除】的成绩数据，返回列表
def get_deleted_scores_dao(db: Session, id: int = None, student_no: str = None, exam_order: int = None):
    # 只查已删除的数据
    query = db.query(Score_DB).filter(Score_DB.is_deleted == 1)

    # 多条件模糊查询
    if id is not None:
        query = query.filter(Score_DB.id.like(f"%{id}%"))
    if student_no:
        query = query.filter(Score_DB.student_no.like(f"%{student_no}%"))
    if exam_order is not None:
        query = query.filter(Score_DB.exam_order.like(f"%{exam_order}%"))

    # 返回查询到的【已删除数据列表】
    return query.all()

# 查询每次考核成绩大于80的学生
def get_all_above_80_dao(db: Session):
    # 子查询：按学号分组，查询每个学生的最低分
    subquery = db.query(
        Score_DB.student_no,
        func.min(Score_DB.score).label("min_score")
    ).filter(Score_DB.is_deleted == 0).group_by(Score_DB.student_no).subquery()

    # 主查询：关联学生表，查询最低分>80的学生信息
    result = db.query(
        Student.student_no,
        Student.student_name,
        subquery.c.min_score.label("score")
    ).join(
        subquery, Student.student_no == subquery.c.student_no
    ).filter(
        subquery.c.min_score > 80,
        Student.is_deleted == 0
    ).all()

    # 将查询结果转成字典列表，适配前端格式
    return [
        {"student_no": r[0], "student_name": r[1], "score": r[2]}
        for r in result
    ]

# 查询不及格超过2次的学生
def get_multiple_fail_dao(db: Session):
    # 1. 找出不及格 > 2 次的学号
    fail_student_nos = db.query(Score_DB.student_no).filter(
        Score_DB.score < 60,
        Score_DB.is_deleted == 0
    ).group_by(Score_DB.student_no).having(func.count() > 2)  # 查询不及格大于2次的学生学号
    if not fail_student_nos.count():  # 如果没有符合条件的数据
        return []  # 直接返回空列表
    # 2. 查询这些学生的姓名 + 所有不及格记录
    query = db.query(
        Student.student_no,
        Student.student_name,
        Score_DB.exam_order,
        Score_DB.score
    ).join(
        Score_DB,
        Student.student_no == Score_DB.student_no
    ).filter(
        Student.student_no.in_(fail_student_nos),
        Score_DB.score < 60,
        Student.is_deleted == 0,
        Score_DB.is_deleted == 0
    )  # 联表查询学生信息与不及格成绩
    # 3. 按学生分组
    result = defaultdict(lambda: {"student_name": "", "fail_records": []})  # 创建自动初始化字典
    for row in query.all():  # 遍历所有不及格记录
        result[row.student_no]["student_no"] = row.student_no  # 设置学生学号
        result[row.student_no]["student_name"] = row.student_name  # 设置学生姓名
        result[row.student_no]["fail_records"].append(
            {"exam_order": row.exam_order,
             "score": float(row.score)
             }
        )  # 添加不及格记录
    # 4. 返回最终格式
    return list(result.values())  # 将字典值转为列表返回


# 按考核序次和班级分组，统计每个班级每场考试的平均分
def get_class_avg_dao(db: Session,class_id=None):
    # 关联学生表，分组计算班级+考试平均分
    if class_id:
        query = (
            db.query(
                Student.class_id,  # 班级ID
                Score_DB.exam_order,  # 考试序号
                func.avg(Score_DB.score).label("avg_score")  # 平均分
            )
            .join(Student, Score_DB.student_no == Student.student_no)  # 关联学生
            .filter(Student.is_deleted == 0, Score_DB.is_deleted == 0,Student.class_id == class_id)  # 过滤未删除数据
            .group_by(Score_DB.exam_order, Student.class_id)  # 分组条件
        )
    else:
        query = (
            db.query(
                Student.class_id,  # 班级ID
                Score_DB.exam_order,  # 考试序号
                func.avg(Score_DB.score).label("avg_score")  # 平均分
            )
            .join(Student, Score_DB.student_no == Student.student_no)  # 关联学生
            .filter(Student.is_deleted == 0, Score_DB.is_deleted == 0)  # 过滤未删除数据
            .group_by(Score_DB.exam_order, Student.class_id)  # 分组条件
        )
    # 将结果转为字典列表
    return [
        {"class_id": r[0],"exam_order":r[1], "avg_score": float(r[2]) if r[2] else None}
        for r in query.all()
    ]