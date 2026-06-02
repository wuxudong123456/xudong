from backend.agent.base_agent import BaseAgent
from backend.agent.system_prompts import get_system_prompt, CHARACTER_NAMES
from backend.service.nl2sql_service import nl2sql_query
from backend.utils.deepseek_util import chat_completion


class DataAgent(BaseAgent):

    @property
    def agent_name(self) -> str:
        return "BusinessManagementAgent"

    async def execute(self, message, character="bajie", history=None, user_id=None):
        char_name = CHARACTER_NAMES.get(character, "猪八戒")
        mem_prompt = ""
        try:
            if user_id and self.db:
                from backend.utils.memory_retriever import MemoryRetriever
                mem_prompt = MemoryRetriever(self.db).build_memory_prompt(user_id, message)
        except Exception:
            pass
        if not self.db:
            return f"数据库连不上，查不了数据！", None
        result = await nl2sql_query(self.db, message) or {}
        rows = (result.get("result") or {}).get("rows", [])
        row_count = (result.get("result") or {}).get("row_count", 0)

        if row_count > 0:
            summary = f"查到了{row_count}条记录：\n"
            if mem_prompt:
                summary = mem_prompt + "\n\n" + summary
            for i, row in enumerate(rows[:10]):
                summary += f"\n{i+1}. " + " | ".join(f"{k}: {v}" for k, v in row.items())
            if row_count > 10:
                summary += f"\n\n...(还有{row_count - 10}条未显示)"
            return summary, result

        # SQL 失败或 0 结果 → 记忆回退
        try:
            from backend.service.memory_service import MemoryService
            memory = MemoryService(self.db)
            recent = memory.get_query_history(None)[:5]
            if recent:
                q_list = "\n".join([f"- {r['question']}" for r in recent])
                prompt = f"""你是{char_name}。用户问："{message}"
最近的查询记录：{q_list}
请根据这些记录直接回答用户。用你自己的口吻和自称。"""
                reply = await chat_completion(
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5, max_tokens=200,
                )
                return reply.strip(), result
        except Exception:
            pass

        err_msg = result.get("error") if result else "无法转换"
        return f"查询出了点问题：{err_msg}。要不换个问题试试？", result
