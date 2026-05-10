"""成绩数据访问模块（异步版本）
# 修改说明：
# 1. 使用 AsyncSession 替代 Session
# 2. 所有数据库操作使用 await session.execute() 或 await session.scalars()
# 3. 使用 SQLAlchemy 2.0 select() 语法
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from collections import defaultdict
from models.score import Score_DB
from models.student_info import Student
from schemas.score import Score_QQ, ScoreUpdate


class ScoreDao:
    """成绩数据访问类（异步）"""

    @staticmethod
    async def add_score_dao(db: AsyncSession, score: Score_QQ):
        """
        添加成绩数据

        :param db: 异步数据库会话
        :param score: 成绩数据
        :return: 添加后的成绩数据
        """
        item = Score_DB(**score.model_dump(), is_deleted=0)
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item

    @staticmethod
    async def get_comprehensive_scores(
        db: AsyncSession,
        id=None,
        student_no=None,
        exam_order=None,
        page=1,
        size=10
    ):
        """
        综合查询成绩

        :param db: 异步数据库会话
        :param id: 成绩ID
        :param student_no: 学生学号
        :param exam_order: 考试序号
        :param page: 页码
        :param size: 每页条数
        :return: (成绩列表, 总条数)
        """
        # 基础查询
        stmt = select(Score_DB).where(Score_DB.is_deleted == 0)

        # 多条件模糊查询
        if id:
            stmt = stmt.where(Score_DB.id.like(f"%{id}%"))
        if student_no:
            stmt = stmt.where(Score_DB.student_no.like(f"%{student_no}%"))
        if exam_order:
            stmt = stmt.where(Score_DB.exam_order.like(f"%{exam_order}%"))

        # 查询总数
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar()

        # 分页查询
        stmt = stmt.offset((page - 1) * size).limit(size)
        result = await db.execute(stmt)
        data_list = result.scalars().all()

        return data_list, total

    @staticmethod
    async def update_score_dao(db: AsyncSession, id: int, data: ScoreUpdate):
        """
        修改成绩

        :param db: 异步数据库会话
        :param id: 成绩ID
        :param data: 更新数据
        :return: 修改后的数据
        """
        stmt = select(Score_DB).where(Score_DB.id == id, Score_DB.is_deleted == 0)
        result = await db.execute(stmt)
        item = result.scalar_one_or_none()

        if item:
            item.score = data.score
            await db.commit()
            await db.refresh(item)

        return item

    @staticmethod
    async def delete_score_dao(db: AsyncSession, id: int):
        """
        删除成绩（逻辑删除）

        :param db: 异步数据库会话
        :param id: 成绩ID
        :return: 删除后的数据
        """
        stmt = select(Score_DB).where(Score_DB.id == id, Score_DB.is_deleted == 0)
        result = await db.execute(stmt)
        item = result.scalar_one_or_none()

        if item:
            item.is_deleted = 1
            await db.commit()

        return item

    @staticmethod
    async def get_deleted_scores_dao(
        db: AsyncSession,
        id: int = None,
        student_no: str = None,
        exam_order: int = None
    ):
        """
        查询已删除的成绩

        :param db: 异步数据库会话
        :param id: 成绩ID
        :param student_no: 学生学号
        :param exam_order: 考试序号
        :return: 已删除数据列表
        """
        stmt = select(Score_DB).where(Score_DB.is_deleted == 1)

        if id is not None:
            stmt = stmt.where(Score_DB.id.like(f"%{id}%"))
        if student_no:
            stmt = stmt.where(Score_DB.student_no.like(f"%{student_no}%"))
        if exam_order is not None:
            stmt = stmt.where(Score_DB.exam_order.like(f"%{exam_order}%"))

        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_all_above_80_dao(db: AsyncSession):
        """
        查询每次考核成绩大于80的学生

        :param db: 异步数据库会话
        :return: 学生列表
        """
        # 子查询：按学号分组，查询每个学生的最低分
        subquery = select(
            Score_DB.student_no,
            func.min(Score_DB.score).label("min_score")
        ).where(
            Score_DB.is_deleted == 0
        ).group_by(Score_DB.student_no).subquery()

        # 主查询：关联学生表，查询最低分>80的学生信息
        stmt = select(
            Student.student_no,
            Student.student_name,
            subquery.c.min_score.label("score")
        ).join(
            subquery, Student.student_no == subquery.c.student_no
        ).where(
            subquery.c.min_score > 80,
            Student.is_deleted == 0
        )

        result = await db.execute(stmt)

        return [
            {"student_no": r[0], "student_name": r[1], "score": r[2]}
            for r in result.all()
        ]

    @staticmethod
    async def get_multiple_fail_dao(db: AsyncSession):
        """
        查询不及格超过2次的学生

        :param db: 异步数据库会话
        :return: 学生列表
        """
        # 找出不及格 > 2 次的学号
        fail_stmt = select(Score_DB.student_no).where(
            Score_DB.score < 60,
            Score_DB.is_deleted == 0
        ).group_by(Score_DB.student_no).having(func.count() > 2)

        fail_result = await db.execute(fail_stmt)
        fail_student_nos = [row[0] for row in fail_result.all()]

        if not fail_student_nos:
            return []

        # 查询这些学生的姓名 + 所有不及格记录
        stmt = select(
            Student.student_no,
            Student.student_name,
            Score_DB.exam_order,
            Score_DB.score
        ).join(
            Score_DB, Student.student_no == Score_DB.student_no
        ).where(
            Student.student_no.in_(fail_student_nos),
            Score_DB.score < 60,
            Student.is_deleted == 0,
            Score_DB.is_deleted == 0
        )

        result = await db.execute(stmt)

        # 按学生分组
        grouped = defaultdict(lambda: {"student_name": "", "fail_records": []})
        for row in result.all():
            grouped[row[0]]["student_no"] = row[0]
            grouped[row[0]]["student_name"] = row[1]
            grouped[row[0]]["fail_records"].append(
                {"exam_order": row[2], "score": float(row[3])}
            )

        return list(grouped.values())

    @staticmethod
    async def get_class_avg_dao(db: AsyncSession, class_id=None):
        """
        班级平均分统计

        :param db: 异步数据库会话
        :param class_id: 班级ID（可选）
        :return: 统计结果列表
        """
        stmt = select(
            Student.class_id,
            Score_DB.exam_order,
            func.avg(Score_DB.score).label("avg_score")
        ).join(
            Student, Score_DB.student_no == Student.student_no
        ).where(
            Student.is_deleted == 0,
            Score_DB.is_deleted == 0
        )

        if class_id:
            stmt = stmt.where(Student.class_id == class_id)

        stmt = stmt.group_by(Score_DB.exam_order, Student.class_id)
        result = await db.execute(stmt)

        return [
            {
                "class_id": r[0],
                "exam_order": r[1],
                "avg_score": float(r[2]) if r[2] else None
            }
            for r in result.all()
        ]
