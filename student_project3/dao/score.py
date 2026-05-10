# 成绩数据访问模块
# 修改说明：将所有函数改为 ScoreDao 类的 @staticmethod 方法
from sqlalchemy import func
from sqlalchemy.orm import Session
from models.score import Score_DB
from models.student_info import Student
from schemas.score import Score_QQ, ScoreUpdate
from collections import defaultdict


class ScoreDao:
    """成绩数据访问类 - 使用 @staticmethod 统一调用"""

    @staticmethod
    def add_score_dao(db: Session, score: Score_QQ):
        """
        添加成绩数据访问层方法

        :param db: 数据库会话
        :param score: 成绩数据
        :return: 添加后的成绩数据
        """
        # 创建成绩数据库对象，is_deleted=0表示未删除
        item = Score_DB(**score.model_dump(), is_deleted=0)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def get_comprehensive_scores(db: Session, id=None, student_no=None, exam_order=None, page=1, size=10):
        """
        综合查询数据访问层方法：多条件+分页查询成绩

        :param db: 数据库会话
        :param id: 成绩ID
        :param student_no: 学生学号
        :param exam_order: 考试序号
        :param page: 页码
        :param size: 每页条数
        :return: (成绩列表, 总条数)
        """
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
        return data_list, total

    @staticmethod
    def update_score_dao(db: Session, id: int, data: ScoreUpdate):
        """
        修改成绩数据访问层方法

        :param db: 数据库会话
        :param id: 成绩ID
        :param data: 更新数据
        :return: 修改后的数据（不存在返回None）
        """
        # 查询指定id且未删除的成绩数据
        item = db.query(Score_DB).filter_by(id=id, is_deleted=0).first()
        if item:
            item.score = data.score
            db.commit()
            db.refresh(item)
        return item

    @staticmethod
    def delete_score_dao(db: Session, id: int):
        """
        删除成绩数据访问层方法：逻辑删除

        :param db: 数据库会话
        :param id: 成绩ID
        :return: 删除后的数据（不存在返回None）
        """
        # 查询指定id且未删除的成绩数据
        item = db.query(Score_DB).filter_by(id=id, is_deleted=0).first()
        if item:
            item.is_deleted = 1
            db.commit()
        return item

    @staticmethod
    def get_deleted_scores_dao(db: Session, id: int = None, student_no: str = None, exam_order: int = None):
        """
        多条件模糊查询【已删除】的成绩数据

        :param db: 数据库会话
        :param id: 成绩ID
        :param student_no: 学生学号
        :param exam_order: 考试序号
        :return: 已删除数据列表
        """
        # 只查已删除的数据
        query = db.query(Score_DB).filter(Score_DB.is_deleted == 1)

        # 多条件模糊查询
        if id is not None:
            query = query.filter(Score_DB.id.like(f"%{id}%"))
        if student_no:
            query = query.filter(Score_DB.student_no.like(f"%{student_no}%"))
        if exam_order is not None:
            query = query.filter(Score_DB.exam_order.like(f"%{exam_order}%"))

        return query.all()

    @staticmethod
    def get_all_above_80_dao(db: Session):
        """
        查询每次考核成绩大于80的学生

        :param db: 数据库会话
        :return: 学生列表
        """
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

        # 将查询结果转成字典列表
        return [
            {"student_no": r[0], "student_name": r[1], "score": r[2]}
            for r in result
        ]

    @staticmethod
    def get_multiple_fail_dao(db: Session):
        """
        查询不及格超过2次的学生

        :param db: 数据库会话
        :return: 学生列表
        """
        # 1. 找出不及格 > 2 次的学号
        fail_student_nos = db.query(Score_DB.student_no).filter(
            Score_DB.score < 60,
            Score_DB.is_deleted == 0
        ).group_by(Score_DB.student_no).having(func.count() > 2)

        if not fail_student_nos.count():
            return []

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
        )

        # 3. 按学生分组
        result = defaultdict(lambda: {"student_name": "", "fail_records": []})
        for row in query.all():
            result[row.student_no]["student_no"] = row.student_no
            result[row.student_no]["student_name"] = row.student_name
            result[row.student_no]["fail_records"].append(
                {"exam_order": row.exam_order, "score": float(row.score)}
            )

        return list(result.values())

    @staticmethod
    def get_class_avg_dao(db: Session, class_id=None):
        """
        按考核序次和班级分组，统计每个班级每场考试的平均分

        :param db: 数据库会话
        :param class_id: 班级ID（可选）
        :return: 统计结果列表
        """
        if class_id:
            query = (
                db.query(
                    Student.class_id,
                    Score_DB.exam_order,
                    func.avg(Score_DB.score).label("avg_score")
                )
                .join(Student, Score_DB.student_no == Student.student_no)
                .filter(
                    Student.is_deleted == 0,
                    Score_DB.is_deleted == 0,
                    Student.class_id == class_id
                )
                .group_by(Score_DB.exam_order, Student.class_id)
            )
        else:
            query = (
                db.query(
                    Student.class_id,
                    Score_DB.exam_order,
                    func.avg(Score_DB.score).label("avg_score")
                )
                .join(Student, Score_DB.student_no == Student.student_no)
                .filter(
                    Student.is_deleted == 0,
                    Score_DB.is_deleted == 0
                )
                .group_by(Score_DB.exam_order, Student.class_id)
            )

        return [
            {"class_id": r[0], "exam_order": r[1], "avg_score": float(r[2]) if r[2] else None}
            for r in query.all()
        ]
