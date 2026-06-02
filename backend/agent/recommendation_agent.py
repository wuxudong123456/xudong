"""
学习推荐 Agent — 学号提取 + BKT 诊断 + LLM 学习计划
"""
import re
import logging
from backend.agent.base_agent import BaseAgent

logger = logging.getLogger(__name__)

LEARNING_KEYWORDS = ["学习计划", "推荐", "薄弱", "诊断", "分析", "掌握", "学习建议"]


class RecommendationAgent(BaseAgent):

    @property
    def agent_name(self) -> str:
        return "LearningRecommendationAgent"

    async def execute(self, message: str, character: str = "bajie",
                      history: list = None, user_id: int = None):
        if not self.db:
            return "数据库不可用，无法进行分析。", None

        student_no = self._extract_student_no(message)

        if not student_no:
            return "请提供学生的学号（如 S2024001），我来帮你分析学习情况。", None

        has_keyword = any(kw in message for kw in LEARNING_KEYWORDS)
        if not has_keyword:
            return f"要为学号 {student_no} 做什么？可以说「生成学习计划」「诊断薄弱点」或「分析成绩趋势」。", None

        try:
            from backend.service.recommendation_service import RecommendationService
            svc = RecommendationService(self.db)

            if "计划" in message or "推荐" in message:
                result = await svc.generate_learning_plan(student_no)
                diag = result["diagnosis"]
                reply = f"""【{result.get('student_name', student_no)} 学习报告】

掌握度：{diag['mastery']:.0%}（{diag['level']}）
趋势：{diag['trend']}
薄弱点：{'；'.join(diag['weak_points'][:3])}

📋 学习计划：
{result['plan']}"""
            else:
                diag = svc.diagnose_weak_points(student_no)
                reply = f"""【{student_no} 诊断结果】

掌握度：{diag['mastery']:.0%}（{diag['level']}）
趋势：{diag['trend']}
薄弱点：
""" + "\n".join([f"  - {w}" for w in diag['weak_points'][:5]])

            return reply.strip(), result if 'result' in dir() else diag
        except Exception as e:
            logger.error("RecommendationAgent failed: %s", e)
            return f"分析失败：{e}", None

    @staticmethod
    def _extract_student_no(message: str) -> str:
        # 匹配 S开头+数字 的学号格式
        match = re.search(r"S\d{4,}", message, re.IGNORECASE)
        if match:
            return match.group(0).upper()
        # 匹配 "学号：xxx" 或 "学号: xxx"
        match = re.search(r"学号[：:\s]*(\w+)", message)
        if match:
            return match.group(1).upper()
        return ""
