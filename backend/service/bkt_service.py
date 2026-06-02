"""
贝叶斯知识追踪 (BKT) 服务 — 简化版
P_known: 学生掌握概率，基于历史考试成绩迭代更新
"""
from typing import List, Dict
from sqlalchemy.orm import Session


class BKTService:
    """贝叶斯知识追踪"""

    def __init__(self, db: Session):
        self.db = db
        self.P_learn = 0.2   # 学习率
        self.P_guess = 0.1   # 猜测率
        self.P_slip = 0.1    # 失误率
        self.P_init = 0.5    # 初始掌握概率

    def calculate_mastery_probability(self, student_no: str,
                                      scores_history: List[Dict]) -> Dict:
        """根据历史成绩计算掌握概率"""
        if len(scores_history) < 1:
            return {"student_no": student_no, "mastery_probability": self.P_init,
                    "level": "weak", "message": "无考试记录，使用默认值"}

        p = self.P_init
        for exam in sorted(scores_history, key=lambda x: x.get("exam_order", 0)):
            score = exam.get("score", 0)
            if score >= 60:
                p = p + (1 - p) * self.P_learn
            else:
                p = p * (1 - self.P_slip)

        p = round(p, 4)
        if p >= 0.8:
            level = "mastered"
        elif p >= 0.4:
            level = "learning"
        else:
            level = "weak"

        return {"student_no": student_no, "mastery_probability": p, "level": level}
