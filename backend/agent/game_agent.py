from backend.agent.base_agent import BaseAgent
from backend.agent.system_prompts import get_system_prompt
from backend.utils.deepseek_util import chat_completion


class GameAgent(BaseAgent):

    @property
    def agent_name(self) -> str:
        return "GameAgent"

    async def execute(self, message, character="bajie", history=None, user_id=None,
                      intent: str = None):
        system_prompt = get_system_prompt(character) + "\n\n你正在跟人玩游戏。如果对方想猜灯谜就出一道有趣的灯谜，如果对方想玩飞花令就说一个上句让对方对下句。用你自己的语气和自称。"
        reply = await chat_completion(
            messages=[{"role": "user", "content": message}],
            system_prompt=system_prompt, temperature=0.85, max_tokens=400,
        )
        return reply, None
