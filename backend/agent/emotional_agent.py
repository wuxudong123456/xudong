from backend.agent.base_agent import BaseAgent
from backend.agent.system_prompts import get_system_prompt
from backend.utils.deepseek_util import chat_completion


class EmotionalAgent(BaseAgent):

    @property
    def agent_name(self) -> str:
        return "EmotionalCounselingAgent"

    async def execute(self, message, character="bajie", history=None, user_id=None):
        system_prompt = get_system_prompt(character) + "\n\n你现在正在安慰一个心情不好的朋友。请用共情的方式回应：先认同感受，再温和安慰，最后给建议。用你自己的语气和自称。"
        try:
            if user_id and self.db:
                from backend.utils.memory_retriever import MemoryRetriever
                mem = MemoryRetriever(self.db).build_memory_prompt(user_id, message)
                if mem:
                    system_prompt += "\n\n" + mem
        except Exception:
            pass
        reply = await chat_completion(
            messages=[{"role": "user", "content": message}],
            system_prompt=system_prompt, temperature=0.8, max_tokens=500,
        )
        return reply, None
