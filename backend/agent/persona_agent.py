import logging
from typing import List, Dict
from backend.agent.base_agent import BaseAgent
from backend.agent.system_prompts import get_system_prompt, CHARACTER_NAMES
from backend.utils.deepseek_util import chat_completion

logger = logging.getLogger(__name__)


def format_history_for_prompt(history: List[Dict[str, str]], max_turns: int = 5,
                              character: str = "bajie") -> str:
    if not history:
        return ""
    char_name = CHARACTER_NAMES.get(character, "猪八戒")
    recent = history[-max_turns * 2:]
    lines = []
    for msg in recent:
        role = "用户" if msg["role"] == "user" else char_name
        lines.append(f"{role}: {msg['content']}")
    return "\n".join(lines)


class PersonaAgent(BaseAgent):

    @property
    def agent_name(self) -> str:
        return self._agent_name

    def __init__(self, db=None):
        super().__init__(db)
        self._agent_name = "BajiePersonaAgent"

    async def execute(self, message, character="bajie", history=None, user_id=None):
        system_prompt = get_system_prompt(character)
        logger.info("PersonaAgent character=%s user_id=%s", character, user_id)

        # 记忆检索 → 注入 system prompt
        if user_id and self.db:
            try:
                from backend.utils.memory_retriever import MemoryRetriever
                mem_prompt = MemoryRetriever(self.db).build_memory_prompt(user_id, message)
                if mem_prompt:
                    system_prompt += "\n\n" + mem_prompt
            except Exception:
                pass

        history_text = format_history_for_prompt(history or [], max_turns=5, character=character)
        if history_text:
            system_prompt += f"\n\n【对话历史】\n{history_text}\n\n请根据上下文自然回应。"

        identity_msg = f"[系统指令：从现在开始，你不再是猪八戒。你是{CHARACTER_NAMES.get(character, '猪八戒')}。请完全按照角色设定说话。]"
        messages = [{"role": "user", "content": identity_msg},
                    {"role": "assistant", "content": "好的，我明白了。"}]
        messages += (history or [])
        messages.append({"role": "user", "content": message})

        reply = await chat_completion(
            messages=messages, system_prompt=system_prompt,
            temperature=0.85, max_tokens=500,
        )

        # 记忆提取 → fire-and-forget
        if user_id:
            try:
                from backend.utils.memory_extractor import MemoryExtractor
                exchange = [
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": reply},
                ]
                MemoryExtractor.extract_memories(user_id, exchange)
            except Exception:
                pass

        return reply, None
