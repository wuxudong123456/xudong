# 成绩服务模块
# 修改说明：
# 1. 调用 ScoreDao 类方法
# 2. 保留原有业务逻辑判断
from fastapi import HTTPException
from sqlalchemy.orm import Session
from dao.score import ScoreDao
from models.score import Score_DB
from schemas.score import Score_QQ, ScoreUpdate


class ScoreService:
    """成绩服务类 - 处理业务逻辑，调用 DAO 层"""

    @staticmethod
    def add_score_service(db: Session, score: Score_QQ):
        """
        添加成绩业务逻辑（先判断 学号+序次 是否重复）

        :param db: 数据库会话
        :param score: 成绩数据
        :return: 添加后的成绩数据
        """
        # 1. 先查询：同一学生 + 同一考试序次 是否已经存在
        exists = db.query(Score_DB).filter(
            Score_DB.student_no == score.student_no,
            Score_DB.exam_order == score.exam_order,
            Score_DB.is_deleted == 0
        ).first()

        # 2. 如果存在 → 直接抛 HTTP 异常
        if exists:
            raise HTTPException(
                status_code=409,
                detail="该学生此考试成绩已存在，不可重复添加"
            )

        # 3. 不存在 → 调用 dao 添加
        return ScoreDao.add_score_dao(db, score)

    @staticmethod
    def format_score_list(score_list):
        """
        格式化成绩列表：统一返回前端需要的结构

        :param score_list: 成绩列表
        :return: 格式化后的字典列表
        """
        return [
            {
                "id": s.id,
                "student_no": s.student_no,
                "exam_order": s.exam_order,
                "score": float(s.score) if s.score else None
            }
            for s in score_list
        ]

    @staticmethod
    def get_scores_service(db: Session, id, student_no, exam_order, page, size):
        """
        综合查询成绩业务逻辑

        :param db: 数据库会话
        :param id: 成绩ID
        :param student_no: 学生学号
        :param exam_order: 考试序号
        :param page: 页码
        :param size: 每页条数
        :return: 统一结构的成绩数据
        """
        # 1. 参数处理：保证页码和条数合法
        page = max(1, page)
        size = max(1, min(size, 50))

        # 2. 调用 dao 查询
        data_list, total = ScoreDao.get_comprehensive_scores(db, id, student_no, exam_order, page, size)

        # 3. 格式化数据
        result_data = ScoreService.format_score_list(data_list)

        # 4. 返回统一结构
        return {
            "code": 200,
            "message": "查询成功" if result_data else "暂无成绩数据",
            "data": result_data,
            "total": total,
            "page": page,
            "size": size
        }

    @staticmethod
    def update_score_service(db: Session, id: int, data: ScoreUpdate):
        """
        修改成绩的业务逻辑

        :param db: 数据库会话
        :param id: 成绩ID
        :param data: 更新数据
        :return: 修改后的数据
        """
        item = ScoreDao.update_score_dao(db, id, data)
        if not item:
            raise HTTPException(status_code=404, detail="成绩不存在")
        return item

    @staticmethod
    def delete_score_service(db: Session, id: int):
        """
        删除成绩的业务逻辑

        :param db: 数据库会话
        :param id: 成绩ID
        :return: 是否成功
        """
        item = ScoreDao.delete_score_dao(db, id)
        if not item:
            raise HTTPException(status_code=404, detail="成绩不存在")
        return True

    @staticmethod
    def restore_score_service(db: Session, id: int = None, student_no: str = None, exam_order: int = None):
        """
        批量/单条恢复成绩

        :param db: 数据库会话
        :param id: 成绩ID（可选）
        :param student_no: 学生学号（可选）
        :param exam_order: 考试序号（可选）
        :return: 恢复的记录数
        """
        # 1. 调用DAO：只查询【已删除】的数据
        score_list = ScoreDao.get_deleted_scores_dao(db, id=id, student_no=student_no, exam_order=exam_order)

        # 2. 业务校验
        if not score_list:
            raise HTTPException(status_code=404, detail="未找到任何已删除的成绩数据")

        # 3. 批量恢复（同时支持单条/多条）
        restore_count = 0
        for score in score_list:
            score.is_deleted = 0
            restore_count += 1

        # 4. 提交事务
        db.commit()

        return restore_count

    @staticmethod
    def get_all_above_80_service(db: Session):
        """
        查询80分以上学生

        :param db: 数据库会话
        :return: 学生列表
        """
        data = ScoreDao.get_all_above_80_dao(db)
        if not data:
            raise HTTPException(status_code=404, detail="暂无80分以上学生")
        return data

    @staticmethod
    def get_multiple_fail_service(db: Session):
        """
        查询不及格超过2次的学生

        :param db: 数据库会话
        :return: 学生列表
        """
        data = ScoreDao.get_multiple_fail_dao(db)
        if not data:
            raise HTTPException(status_code=404, detail="暂无不及格超过2次的学生")
        return data

    @staticmethod
    def get_class_avg_service(db: Session, class_id=None):
        """
        查询班级平均分统计

        :param db: 数据库会话
        :param class_id: 班级ID（可选）
        :return: 统计结果
        """
        data = ScoreDao.get_class_avg_dao(db, class_id)
        if not data:
            raise HTTPException(status_code=404, detail="暂无考试成绩数据")
        return data
