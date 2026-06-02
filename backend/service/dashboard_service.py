"""仪表盘数据聚合服务"""
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.entity.student import Student
from backend.entity.class_info import ClassInfo
from backend.entity.score import Score
from backend.entity.employment import Employment
from backend.entity.teacher import Teacher


class DashboardService:

    def __init__(self, db: Session):
        self.db = db

    def get_overview(self) -> Dict[str, Any]:
        """仪表盘概览数据"""
        total_students = self.db.query(func.count(Student.id)).filter(Student.is_deleted == 0).scalar() or 0
        total_classes = self.db.query(func.count(ClassInfo.class_id)).filter(ClassInfo.is_deleted == 0).scalar() or 0
        total_teachers = self.db.query(func.count(Teacher.teacher_id)).filter(Teacher.is_deleted == 0).scalar() or 0
        avg_score = self.db.query(func.avg(Score.score)).filter(Score.is_deleted == 0).scalar() or 0
        employed = self.db.query(func.count(Employment.employment_id)).filter(
            Employment.is_deleted == 0, Employment.final_choice == 1
        ).scalar() or 0
        rate = round(employed / total_students * 100, 1) if total_students > 0 else 0

        return {
            "total_students": total_students,
            "total_classes": total_classes,
            "total_teachers": total_teachers,
            "avg_score": round(float(avg_score), 1),
            "employment_rate": rate,
        }

    def get_class_distribution(self) -> list:
        """班级学生分布(饼图数据)"""
        rows = (
            self.db.query(ClassInfo.class_name, func.count(Student.id))
            .outerjoin(Student, (ClassInfo.class_id == Student.class_id) & (Student.is_deleted == 0))
            .filter(ClassInfo.is_deleted == 0)
            .group_by(ClassInfo.class_id).all()
        )
        return [{"name": name, "value": count} for name, count in rows]

    def get_score_trend(self) -> list:
        """各次考试的平均分趋势(折线图数据)"""
        rows = (
            self.db.query(Score.exam_order, func.avg(Score.score))
            .filter(Score.is_deleted == 0)
            .group_by(Score.exam_order)
            .order_by(Score.exam_order).all()
        )
        return [{"exam_order": f"第{order}次", "avg_score": round(float(avg), 1)} for order, avg in rows]

    def get_employment_by_class(self) -> list:
        """各班就业情况(柱状图数据)"""
        rows = (
            self.db.query(ClassInfo.class_name, func.count(Employment.employment_id),
                          func.avg(Employment.salary))
            .outerjoin(Employment, (ClassInfo.class_id == Employment.class_id) &
                       (Employment.is_deleted == 0))
            .filter(ClassInfo.is_deleted == 0)
            .group_by(ClassInfo.class_id)
            .order_by(ClassInfo.class_id).all()
        )
        return [{"class_name": name, "employed_count": cnt, "avg_salary": round(float(avg), 1) if avg else 0}
                for name, cnt, avg in rows]

    def get_score_distribution(self) -> list:
        """成绩分数段分布"""
        ranges = [("90-100", 90, 100), ("80-89", 80, 89), ("70-79", 70, 79),
                  ("60-69", 60, 69), ("0-59", 0, 59)]
        result = []
        for label, lo, hi in ranges:
            cnt = self.db.query(func.count(Score.id)).filter(
                Score.is_deleted == 0, Score.score >= lo, Score.score <= hi
            ).scalar() or 0
            result.append({"range": label, "count": cnt})
        return result
