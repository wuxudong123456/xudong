from backend.agent.base_agent import BaseAgent
from backend.agent.system_prompts import get_system_prompt
from backend.utils.deepseek_util import chat_completion


class SocialAgent(BaseAgent):

    @property
    def agent_name(self) -> str:
        return "SocialAssistantAgent"

    async def execute(self, message, character="bajie", history=None, user_id=None):
        system_prompt = get_system_prompt(character) + "\n\n你现在在帮人出谋划策提供社交建议。给的建议要实用，用你自己的语气和自称。"
        reply = await chat_completion(
            messages=[{"role": "user", "content": message}],
            system_prompt=system_prompt, temperature=0.9, max_tokens=500,
        )
        return reply, None
