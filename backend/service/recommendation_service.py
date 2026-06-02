"""
个性化学习推荐服务 — 薄弱点诊断 + LLM 学习计划
"""
import logging
from typing import Dict
from sqlalchemy.orm import Session
from backend.entity.score import Score
from backend.entity.student import Student

logger = logging.getLogger(__name__)


class RecommendationService:
    """学习推荐"""

    def __init__(self, db: Session):
        self.db = db

    def diagnose_weak_points(self, student_no: str) -> Dict:
        scores = self.db.query(Score).filter(
            Score.student_no == student_no, Score.is_deleted == 0
        ).order_by(Score.exam_order.asc()).all()

        if len(scores) < 2:
            return {"student_no": student_no, "scores": [],
                    "trend": "unknown", "mastery": 0.5, "level": "weak",
                    "weak_points": ["数据不足，需要至少2次考试成绩"],
                    "message": "数据不足，需要至少2次考试成绩"}

        score_list = [{"exam_order": s.exam_order, "score": float(s.score or 0)}
                      for s in scores]

        # 趋势分析
        first_half = [s["score"] for s in score_list[:len(score_list)//2]]
        second_half = [s["score"] for s in score_list[len(score_list)//2:]]
        avg1 = sum(first_half) / len(first_half)
        avg2 = sum(second_half) / len(second_half)

        if avg2 < avg1 - 5:
            trend = "declining"
        elif avg2 > avg1 + 5:
            trend = "improving"
        else:
            trend = "stable"

        # 下降点检测
        weak_points = []
        for i in range(1, len(score_list)):
            if score_list[i]["score"] < score_list[i-1]["score"] - 5:
                weak_points.append(
                    f"第{score_list[i]['exam_order']}次考试({score_list[i]['score']}分)"
                    f"比第{score_list[i-1]['exam_order']}次({score_list[i-1]['score']}分)下降"
                )

        if trend == "declining":
            weak_points.append("整体成绩呈下降趋势")
        if avg2 < 60:
            weak_points.append(f"近期平均分{avg2:.1f}，低于及格线")

        # BKT
        from backend.service.bkt_service import BKTService
        bkt = BKTService(self.db).calculate_mastery_probability(student_no, score_list)

        return {"student_no": student_no, "scores": score_list,
                "trend": trend, "mastery": bkt["mastery_probability"],
                "level": bkt["level"],
                "weak_points": weak_points if weak_points else ["暂未发现明显薄弱点"]}

    async def generate_learning_plan(self, student_no: str) -> Dict:
        diagnosis = self.diagnose_weak_points(student_no)

        if diagnosis.get("message"):
            return {"student_no": student_no, "diagnosis": diagnosis,
                    "plan": diagnosis["message"]}

        student = self.db.query(Student).filter(
            Student.student_no == student_no, Student.is_deleted == 0
        ).first()
        name = student.student_name if student else student_no

        scores_text = "\n".join([
            f"第{s['exam_order']}次: {s['score']}分" for s in diagnosis["scores"]
        ])
        weak_text = "\n".join([f"- {w}" for w in diagnosis["weak_points"]])

        prompt = f"""你是学习顾问。学生{name}（学号{student_no}）的成绩分析如下：

历次成绩：{scores_text}
趋势：{diagnosis['trend']}
掌握度：{diagnosis['mastery']:.1%}
薄弱点：{weak_text}

请生成个性化学习计划，包括：
1. 重点复习方向
2. 每日学习时间建议
3. 推荐练习内容
用简洁自然的语言，200字以内。"""

        try:
            from backend.utils.deepseek_util import chat_completion
            plan = await chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5, max_tokens=300,
            )
        except Exception as e:
            logger.error("LLM plan generation failed: %s", e)
            plan = f"建议重点复习薄弱环节，每天保持1-2小时学习时间。趋势：{diagnosis['trend']}，掌握度：{diagnosis['mastery']:.0%}"

        return {"student_no": student_no, "student_name": name,
                "diagnosis": diagnosis, "plan": plan.strip()}
