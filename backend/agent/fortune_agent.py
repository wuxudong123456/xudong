from backend.agent.base_agent import BaseAgent
from backend.agent.system_prompts import get_system_prompt
from backend.service.fortune_service import FortuneService
from backend.utils.deepseek_util import chat_completion


class FortuneAgent(BaseAgent):

    @property
    def agent_name(self) -> str:
        return "FortuneTellingAgent"

    async def execute(self, message, character="bajie", history=None, user_id=None):
        fortune_service = FortuneService()
        fortune = await fortune_service.generate_fortune()
        if not fortune:
            return "天机不可泄露，改日再看吧。", None
        data_text = f"""运势数据：
综合: {fortune.get('overall_score', '?')}分 - {fortune.get('overall_text', '')}
爱情: {fortune.get('love_score', '?')}分 - {fortune.get('love_text', '')}
事业: {fortune.get('career_score', '?')}分 - {fortune.get('career_text', '')}
财运: {fortune.get('wealth_score', '?')}分 - {fortune.get('wealth_text', '')}
健康: {fortune.get('health_score', '?')}分 - {fortune.get('health_text', '')}
幸运色: {fortune.get('lucky_color', '')}
幸运数字: {fortune.get('lucky_number', '')}
幸运方位: {fortune.get('lucky_direction', '')}
建议: {fortune.get('advice', '')}"""
        system_prompt = get_system_prompt(character)
        prompt = f"""{data_text}

请用你自己的语气和自称，告诉对方今日运势。不要提"俺老猪"或任何猪八戒的口头禅。"""
        reply = await chat_completion(
            messages=[{"role": "user", "content": prompt}],
            system_prompt=system_prompt, temperature=0.7, max_tokens=400,
        )
        return reply, fortune
