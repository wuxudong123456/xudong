from backend.agent.base_agent import BaseAgent
from backend.agent.system_prompts import get_system_prompt, CHARACTER_NAMES
from backend.service.weather_service import WeatherService
from backend.utils.deepseek_util import chat_completion
from backend.utils.llm_router import chat_completion as llm_chat


class WeatherAgent(BaseAgent):

    @property
    def agent_name(self) -> str:
        return "WeatherQueryAgent"

    async def execute(self, message, character="bajie", history=None, user_id=None):
        city = await self._extract_city(message)
        char_name = CHARACTER_NAMES.get(character, "猪八戒")
        if not city:
            no_city = {"bajie": "你想查哪儿的天气？告诉俺老猪城市名字就行！",
                       "luzhishen": "洒家不知道你想查哪儿的天气！说个地名来！",
                       "lindaiyu": "你要查什么地方的天气？不说清楚我怎么帮你。",
                       "zhugeliang": "请告知城池名称，亮方能查询天气。",
                       }
            return no_city.get(character, f"你想查哪儿的天气？"), None
        weather_service = WeatherService()
        weather_data = await weather_service.get_weather_reply(city, message)
        system_prompt = get_system_prompt(character)
        final_prompt = f"""{weather_data}

请用你自己的语气和自称，把以上天气信息自然地告诉对方。不要提"俺老猪"。"""
        reply = await chat_completion(
            messages=[{"role": "user", "content": final_prompt}],
            system_prompt=system_prompt, temperature=0.7, max_tokens=300,
        )
        return reply, {"city": city}

    async def _extract_city(self, message: str) -> str:
        prompt = f"""从用户消息中提取城市名称。只回复城市名，不要其他内容。如果没提到城市，回复"NONE"。

用户消息: {message}"""
        try:
            result = await llm_chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1, max_tokens=20,
            )
            city = result.strip()
            if city.upper() == "NONE" or not city:
                return ""
            return city
        except Exception:
            return ""
