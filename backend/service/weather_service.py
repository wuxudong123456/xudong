"""
天气服务
调用天气API + AI生成个性化回复
"""
from backend.utils.weather_util import get_weather_by_city, format_weather_for_prompt
from backend.utils.llm_router import chat_completion


class WeatherService:
    """天气查询服务"""

    async def get_weather_reply(self, city: str, user_message: str = "") -> str:
        """
        获取天气回复
        :param city: 城市名
        :param user_message: 用户原始消息
        :return: 八戒口吻的天气回复
        """
        weather_data = await get_weather_by_city(city)

        if not weather_data:
            return "哼哼～俺老猪的天眼通暂时失灵了，查不到这地方的天气。你换个城市试试？"

        weather_text = format_weather_for_prompt(weather_data)

        prompt = f"""你是猪八戒，正在告诉朋友天气情况。

{weather_text}

请用猪八戒的口吻（自称"俺老猪"）回复，包含：
1. 当前天气概况
2. 穿衣建议
3. 出行提醒（如果需要带伞/防晒）
4. 一句幽默的调侃

语气要憨厚诙谐，像老朋友聊天。"""

        reply = await chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=300,
        )

        return reply
