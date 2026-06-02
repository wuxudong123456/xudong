"""
ReAct (Reasoning + Acting) 推理 Agent
LLM 驱动：Thought → Action → Observation → 循环 → Final Answer
"""
import json
import logging
from typing import Tuple, Any
from backend.agent.base_agent import BaseAgent
from backend.utils.deepseek_util import chat_completion

logger = logging.getLogger(__name__)

REACT_PROMPT = """你是一个推理助手，能逐步分析复杂问题。你可以使用以下工具：

{tool_list}

每轮思考后，严格输出 JSON（不要其他内容）：

需要调用工具时：
{{"thought": "分析当前情况和下一步计划", "action": {{"tool": "工具名", "input": "工具输入"}}}}

给出最终答案时：
{{"final_answer": "基于所有观察结果的完整回答"}}

规则：
- 每次只输出一个 JSON，不要多余文字
- 先用 thought 分析，再决定是调用工具还是给答案
- 如果现有信息足够回答，直接给 final_answer
- 所有回答用中文"""


class ReactAgent(BaseAgent):
    """ReAct 推理循环 Agent"""

    @property
    def agent_name(self) -> str:
        return "ReActReasoningAgent"

    async def execute(self, message: str, character: str = "bajie",
                      history: list = None, user_id: int = None) -> Tuple[str, Any]:
        tools = self._build_tools()
        if not tools:
            return "当前没有可用的工具，无法进行推理分析。", None

        tool_list = "\n".join([f"- {t['name']}: {t['desc']}" for t in tools])
        system_prompt = REACT_PROMPT.format(tool_list=tool_list)

        context = f"用户问题：{message}"
        observations = []
        steps_data = []

        for step in range(5):
            prompt = f"{context}\n\n已有观察结果：\n" + "\n".join(
                [f"[步骤{i+1}] {o}" for i, o in enumerate(observations)]
            ) if observations else context

            resp = await chat_completion(
                messages=[{"role": "user", "content": prompt}],
                system_prompt=system_prompt, temperature=0.3, max_tokens=500,
            )
            parsed = self._parse_json(resp)

            if parsed.get("final_answer"):
                return parsed["final_answer"], {"steps": steps_data}

            if parsed.get("action"):
                action = parsed["action"]
                obs = await self._execute_tool(action, tools)
                thought = parsed.get("thought", f"调用 {action.get('tool', '?')}")
                observations.append(f"{thought} → {obs}")
                steps_data.append({"thought": thought, "action": action, "observation": obs})
                continue

            observations.append(f"LLM 返回了无法解析的内容: {resp[:100]}")
            steps_data.append({"error": resp[:100]})

        # max_steps 用完，强行总结
        summary_prompt = f"{context}\n\n以下是推理过程：\n" + "\n".join(observations) + "\n\n请根据以上信息给出最终答案。"
        reply = await chat_completion(
            messages=[{"role": "user", "content": summary_prompt}],
            temperature=0.5, max_tokens=400,
        )
        return reply.strip(), {"steps": steps_data, "forced_conclusion": True}

    # ===== 工具系统 =====

    def _build_tools(self) -> list:
        tools = []
        if self.db is not None:
            tools.append({"name": "nl2sql", "desc": "数据库查询。input: 自然语言问题（如'有多少学生''成绩最高的是谁'）",
                          "fn": self._tool_nl2sql})
        tools.append({"name": "rag_search", "desc": "四大名著知识检索。input: 要搜索的问题（如'孙悟空大闹天宫'）",
                      "fn": self._tool_rag})
        tools.append({"name": "graph_query", "desc": "人物关系图谱查询。input: 历史人物名（如'诸葛亮'）",
                      "fn": self._tool_graph})
        return tools

    async def _execute_tool(self, action: dict, tools: list) -> str:
        tool_name = action.get("tool", "")
        tool_input = action.get("input", "")
        for t in tools:
            if t["name"] == tool_name:
                try:
                    return await t["fn"](tool_input)
                except Exception as e:
                    return f"工具 {tool_name} 执行失败: {e}"
        return f"未知工具: {tool_name}，可用工具: {[t['name'] for t in tools]}"

    async def _tool_nl2sql(self, question: str) -> str:
        from backend.service.nl2sql_service import nl2sql_query
        result = await nl2sql_query(self.db, question)
        rows = (result.get("result") or {}).get("rows", [])
        if not rows:
            return result.get("error", "查询无结果")
        return str(rows[:10])

    async def _tool_rag(self, question: str) -> str:
        from backend.service.rag_service import RAGService
        result = await RAGService().answer_question_async(question)
        return result.get("answer", "检索无结果")[:500]

    async def _tool_graph(self, name: str) -> str:
        from backend.service.graph_service import GraphService
        result = GraphService().get_person_relations(name.strip())
        relations = result.get("relations", [])[:5]
        if not relations:
            return f"未找到 {name} 的人物关系"
        return "; ".join([f"{r['relation_type']}:{r['target_name']}" for r in relations])

    @staticmethod
    def _parse_json(text: str) -> dict:
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            s = text.find("{")
            e = text.rfind("}") + 1
            if s >= 0 and e > s:
                try:
                    return json.loads(text[s:e])
                except json.JSONDecodeError:
                    pass
        return {}
