"""
多智能体编排器 — 任务分解 + 并行执行 + 结果合并 + 协同
"""
import asyncio
import logging
from typing import Dict
from sqlalchemy.orm import Session
from backend.agent.data_agent import DataAgent
from backend.agent.knowledge_agent import KnowledgeAgent
from backend.agent.emotional_agent import EmotionalAgent
from backend.agent.social_agent import SocialAgent
from backend.agent.game_agent import GameAgent
from backend.agent.persona_agent import PersonaAgent
from backend.agent.weather_agent import WeatherAgent
from backend.agent.fortune_agent import FortuneAgent
from backend.agent.agent_message_bus import AgentMessageBus

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """多智能体编排器"""

    def __init__(self, db: Session = None):
        self.db = db
        self.data_agent = DataAgent(db)
        self.knowledge_agent = KnowledgeAgent(db)
        self.emotional_agent = EmotionalAgent(db)
        self.social_agent = SocialAgent(db)
        self.game_agent = GameAgent(db)
        self.persona_agent = PersonaAgent(db)
        self.weather_agent = WeatherAgent(db)
        self.fortune_agent = FortuneAgent(db)
        self.bus = AgentMessageBus()

        # ReAct Agent（可选）
        try:
            from backend.agent.react_agent import ReactAgent
            self.react_agent = ReactAgent(db)
        except Exception:
            self.react_agent = None

        # 学习推荐 Agent（可选）
        try:
            from backend.agent.recommendation_agent import RecommendationAgent
            self.recommendation_agent = RecommendationAgent(db)
        except Exception:
            self.recommendation_agent = None

    # ===== 新入口：任务分解 + 并行调度 + 结果合并 =====

    async def execute(self, intent: str, message: str, character: str = "bajie",
                      history: list = None, user_id: int = None) -> Dict:
        """智能调度入口：Function Calling → 分解 → 并行 → 单Agent"""
        self.bus.set("user_message", message)

        # Function Calling 模式：data_query / knowledge_question
        if intent in ("data_query", "knowledge_question"):
            try:
                return await self._execute_function_calling(intent, message, character, history, user_id)
            except Exception as e:
                logger.warning("Function Calling failed, fallback: %s", e)

        # 任务分解
        subtasks = []
        try:
            from backend.agent.task_decomposer import TaskDecomposer
            subtasks = await TaskDecomposer.decompose(message)
        except Exception as e:
            logger.warning("Decompose failed, fallback to single: %s", e)

        if len(subtasks) > 1:
            return await self._execute_parallel(subtasks, message, character, history, user_id)

        return await self.execute_single(intent, message, character, history, user_id)

    async def _execute_function_calling(self, intent: str, message: str,
                                        character: str, history: list, user_id: int) -> Dict:
        """Function Calling 循环：LLM 自主决定调用工具（最多 3 轮）"""
        import json as _json
        from backend.agent.tool_registry import ToolRegistry
        from backend.utils.deepseek_util import chat_completion

        registry = ToolRegistry()
        tools = registry.get_all_tools()
        tool_desc = "\n".join([
            f"- {t['name']}: {t['description']}。参数: {_json.dumps(t['params'], ensure_ascii=False)}"
            for t in tools
        ])
        system_prompt = f"""你可以使用以下工具来回答问题。{chr(10)}{tool_desc}
如果需要使用工具，严格返回JSON: {{"tool": "工具名", "params": {{...}}}}
如果不需要工具或信息已足够，直接回复用户。"""

        context = [{"role": "user", "content": message}]
        if history:
            context = history[-6:] + context
        tool_results = []

        for _round in range(3):
            resp = await chat_completion(
                messages=context,
                system_prompt=system_prompt, temperature=0.3, max_tokens=500,
            )
            parsed = self._parse_func_json(resp)
            if not parsed or "tool" not in parsed:
                # LLM 选择直接回复
                return {"intent": intent, "agent": "FunctionCallingAgent",
                        "reply": resp.strip(), "data": {"tool_calls": tool_results}}

            tool_name = parsed["tool"]
            tool_params = parsed.get("params", {})
            obs = await registry.execute(tool_name, tool_params)
            tool_results.append({"tool": tool_name, "params": tool_params, "result": obs[:300]})
            context.append({"role": "assistant", "content": resp})
            context.append({"role": "user",
                           "content": f"[工具 {tool_name} 返回结果]\n{obs}\n\n请根据这个结果继续回答或调用其他工具。"})

        # 超 3 轮，强制总结
        final_resp = await chat_completion(
            messages=context + [{"role": "user", "content": "请根据以上所有信息给出最终答案。"}],
            temperature=0.5, max_tokens=400,
        )
        return {"intent": intent, "agent": "FunctionCallingAgent",
                "reply": final_resp.strip(), "data": {"tool_calls": tool_results}}

    @staticmethod
    def _parse_func_json(text: str) -> dict:
        import json as _json
        try:
            return _json.loads(text.strip())
        except _json.JSONDecodeError:
            s = text.find("{")
            e = text.rfind("}") + 1
            if s >= 0 and e > s:
                try:
                    return _json.loads(text[s:e])
                except _json.JSONDecodeError:
                    pass
        return {}

    async def _execute_parallel(self, subtasks: list, original_msg: str,
                                character: str, history: list, user_id: int) -> Dict:
        """并行执行子任务 + LLM 合并结果"""
        async def run_one(task):
            try:
                i = task["intent"]
                msg = task["sub_message"]
                result = await self.execute_single(i, msg, character, history, user_id)
                return {"intent": i, "sub_message": msg, "reply": result["reply"]}
            except Exception as e:
                return {"intent": task["intent"], "sub_message": task["sub_message"],
                        "reply": f"执行失败: {e}"}

        results = await asyncio.gather(*[run_one(t) for t in subtasks])

        # LLM 合并
        merged = await self._merge_results(original_msg, results, character)
        return {"intent": "collaborative", "agent": "MultiAgentSystem",
                "reply": merged, "data": results}

    async def _merge_results(self, message: str, results: list, character: str) -> str:
        """用 LLM 合并多 Agent 结果"""
        parts = "\n".join([
            f"[{r['intent']}] {r['sub_message']}: {r['reply'][:300]}"
            for r in results
        ])
        from backend.agent.system_prompts import get_system_prompt, CHARACTER_NAMES
        char_name = CHARACTER_NAMES.get(character, "猪八戒")
        prompt = f"""你是{char_name}。用户原问题是：{message}

以下是你从不同角度获取的信息：
{parts}

请将这些信息整合成一段自然、连贯的回复，用你自己的口吻。不要列出编号或说"根据xx角度"。"""
        try:
            from backend.utils.deepseek_util import chat_completion
            reply = await chat_completion(
                messages=[{"role": "user", "content": prompt}],
                system_prompt=get_system_prompt(character),
                temperature=0.7, max_tokens=500,
            )
            return reply.strip()
        except Exception as e:
            logger.error("Merge failed: %s", e)
            return "\n\n".join([r["reply"] for r in results])

    # ===== 原有路由逻辑（一行未删） =====

    async def execute_single(self, intent: str, message: str, character: str = "bajie",
                             history: list = None, user_id: int = None) -> Dict:
        routing = {
            "data_query": (self.data_agent, "BusinessManagementAgent"),
            "knowledge_question": (self.knowledge_agent, "RAGKnowledgeAgent"),
            "emotional_support": (self.emotional_agent, "EmotionalCounselingAgent"),
            "social_help": (self.social_agent, "SocialAssistantAgent"),
            "weather_query": (self.weather_agent, "WeatherQueryAgent"),
            "fortune_telling": (self.fortune_agent, "FortuneTellingAgent"),
            "game_riddle": (self.game_agent, "GameAgent"),
            "game_poetry": (self.game_agent, "GameAgent"),
            "chat_greet": (self.persona_agent, self._persona_agent_name(character)),
            "deep_reasoning": (self.react_agent, "ReActReasoningAgent") if self.react_agent else (self.persona_agent, "BajiePersonaAgent"),
            "learning_recommendation": (self.recommendation_agent, "LearningRecommendationAgent") if self.recommendation_agent else (self.persona_agent, "BajiePersonaAgent"),
        }

        agent, agent_name = routing.get(intent, (self.persona_agent, "BajiePersonaAgent"))

        extra = {}
        if intent in ("game_riddle", "game_poetry"):
            extra["intent"] = intent

        reply, data = await agent.execute(message, character, history, user_id, **extra)

        return {"intent": intent, "agent": agent_name, "reply": reply, "data": data}

    @staticmethod
    def _persona_agent_name(character: str) -> str:
        names = {"bajie": "BajiePersonaAgent", "luzhishen": "LuzhishenPersonaAgent",
                 "lindaiyu": "LindaiyuPersonaAgent", "zhugeliang": "ZhugeliangPersonaAgent"}
        return names.get(character, "BajiePersonaAgent")
