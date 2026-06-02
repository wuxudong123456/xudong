"""
任务分解器 — LLM 分析复合问题 → 拆分为独立子任务
"""
import json
import logging
from typing import List

logger = logging.getLogger(__name__)

VALID_INTENTS = [
    "data_query", "knowledge_question", "chat_greet",
    "emotional_support", "social_help", "game_riddle", "game_poetry",
    "weather_query", "fortune_telling",
]

DECOMPOSE_PROMPT = """分析用户消息，判断是否为需要分解的复合问题。

如果是单一问题，返回空数组: {"subtasks": []}
如果是复合问题（最多拆3个），返回: {"subtasks": [{"intent":"意图代码","sub_message":"子问题描述","order":0}]}

意图代码选项: data_query(数据库查询), knowledge_question(名著知识), emotional_support(情绪疏导), social_help(社交帮助), weather_query(天气查询), fortune_telling(运势占卜), chat_greet(闲聊)

复合问题示例:
- "查一下张三的成绩，再分析他的学习状态" → 2个子任务
- "今天天气怎么样，适合出去玩吗" → 1个子任务(weather_query)
- "帮我算一卦，然后再查一下就业率" → 2个子任务
- "你好" → 空数组

只返回JSON，不要其他内容。

用户消息: """


class TaskDecomposer:
    """LLM 驱动的任务分解器"""

    @staticmethod
    async def decompose(message: str) -> List[dict]:
        try:
            from backend.utils.deepseek_util import chat_completion
            resp = await chat_completion(
                messages=[{"role": "user", "content": DECOMPOSE_PROMPT + message}],
                temperature=0.2, max_tokens=300,
            )
            s = resp.find("{")
            e = resp.rfind("}") + 1
            if s >= 0 and e > s:
                data = json.loads(resp[s:e])
                subtasks = data.get("subtasks", [])
                # 过滤非法意图 + 限制 3 个
                valid = [t for t in subtasks
                         if t.get("intent") in VALID_INTENTS and t.get("sub_message")]
                return valid[:3]
        except Exception as e:
            logger.warning("Task decomposition failed: %s", e)
        return []
