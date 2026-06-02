"""
多智能体编排服务
架构: IntentClassifier → OrchestratorAgent → 8个专家Agent
"""
import json
import logging
from typing import Dict, List, AsyncGenerator
from sqlalchemy.orm import Session
from backend.utils.deepseek_util import chat_completion, chat_completion_stream
from backend.agent.orchestrator_agent import OrchestratorAgent
from backend.agent.system_prompts import get_system_prompt, CHARACTER_NAMES

logger = logging.getLogger(__name__)

# 意图分类提示词
INTENT_CLASSIFIER_PROMPT = """你是一个意图分类器。分析用户消息，归类到以下9种意图之一。只回复意图代码，不要其他内容。

意图代码:
- data_query: 查询学生/班级/成绩/就业/课程等业务数据（如"有多少学生"、"成绩最高的是谁"、"就业率多少"）
- knowledge_question: 询问四大名著相关知识（如"孙悟空大闹天宫是哪一回"、"曹操败走华容道"）
- chat_greet: 日常闲聊/打招呼/自我介绍（如"你好"、"你是谁"、"今天天气不错"）
- emotional_support: 情绪低落/需要安慰/倾诉（如"我好难过"、"压力很大"、"失恋了怎么办"）
- social_help: 需要社交帮助/话术/情书（如"帮我写封情书"、"怎么跟女生搭讪"、"约会说什么"）
- game_riddle: 猜灯谜相关（如"来道谜题"、"出个灯谜"、"我猜答案是..."）
- game_poetry: 飞花令/对诗相关（如"来对诗"、"飞花令"）
- weather_query: 查询天气（如"今天天气怎么样"、"北京会下雨吗"）
- fortune_telling: 运势占卜（如"帮我算一卦"、"今天运势如何"）

用户消息: """


async def classify_intent(message: str) -> str:
    """
    调用DeepSeek分类用户意图
    :param message: 用户消息
    :return: 意图代码
    """
    try:
        response = await chat_completion(
            messages=[{"role": "user", "content": f"{INTENT_CLASSIFIER_PROMPT}{message}"}],
            temperature=0.1,
            max_tokens=20,
        )
        intent = response.strip().lower()
        valid_intents = [
            "data_query", "knowledge_question", "chat_greet",
            "emotional_support", "social_help", "game_riddle", "game_poetry",
            "weather_query", "fortune_telling",
        ]
        if intent in valid_intents:
            return intent
        return "chat_greet"
    except Exception as e:
        logger.error(f"意图分类失败: {e}")
        return "chat_greet"


async def classify_intent_hybrid(message: str) -> str:
    """贝叶斯 + LLM 混合分类：贝叶斯置信度 >=0.85 直接用，否则回退 LLM"""
    try:
        from backend.service.bayesian_classifier import classify, add_training_sample
        bayes_intent, confidence = classify(message)
        logger.info("Bayesian: intent=%s confidence=%.2f", bayes_intent, confidence)
        if bayes_intent != "unknown" and confidence >= 0.85:
            return bayes_intent

        # 回退 LLM
        intent = await classify_intent(message)
        # 自我学习：LLM 结果加入训练缓冲区
        if intent != "unknown":
            add_training_sample(message, intent)
        return intent
    except Exception as e:
        logger.warning("Hybrid classify failed, fallback to LLM: %s", e)
        return await classify_intent(message)


class AgentService:
    """多智能体编排服务"""

    def __init__(self, db: Session = None):
        self.db = db
        self.orchestrator = OrchestratorAgent(db)
        self._user_id = None

    async def process_message(self, message: str,
                              history: List[Dict[str, str]] = None,
                              character: str = "bajie",
                              user_id: int = None) -> Dict:
        intent = await classify_intent_hybrid(message)
        history = history or []
        self._user_id = user_id
        return await self.orchestrator.execute(intent, message, character, history, user_id)

    async def process_message_stream(self, message: str,
                                     history: List[Dict[str, str]] = None,
                                     character: str = "bajie",
                                     user_id: int = None
                                     ) -> AsyncGenerator[str, None]:
        intent = await classify_intent_hybrid(message)
        history = history or []
        self._user_id = user_id

        yield f"event: intent\ndata: {json.dumps({'intent': intent})}\n\n"

        if intent == "knowledge_question":
            from backend.service.rag_service import RAGService
            rag_service = RAGService()
            async for chunk in rag_service.answer_question_stream(message):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            yield "data: [DONE]\n\n"
        elif intent in ("data_query", "emotional_support", "social_help",
                        "weather_query", "fortune_telling", "game_riddle",
                        "game_poetry", "chat_greet"):
            result = await self.orchestrator.execute(intent, message, character, history, user_id)
            reply = result.get("reply", "")
            if result.get("data"):
                yield f"data: {json.dumps({'content': reply, 'data': result['data']})}\n\n"
            else:
                yield f"data: {json.dumps({'content': reply})}\n\n"
            yield "data: [DONE]\n\n"
        else:
            # 兜底：角色闲聊
            stream_msgs = history + [{"role": "user", "content": message}]
            async for chunk in chat_completion_stream(
                messages=stream_msgs,
                system_prompt=get_system_prompt(character),
                temperature=0.85, max_tokens=500,
            ):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            yield "data: [DONE]\n\n"

    @staticmethod
    def _character_agent_name(character: str) -> str:
        names = {"bajie": "BajiePersonaAgent", "luzhishen": "LuzhishenPersonaAgent",
                 "lindaiyu": "LindaiyuPersonaAgent", "zhugeliang": "ZhugeliangPersonaAgent"}
        return names.get(character, "BajiePersonaAgent")
