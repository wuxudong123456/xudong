"""
天气查询工具
主源: wttr.in (免费, 无需API Key)
备源: 和风天气 (需 API Key, 数据更精细)
"""
import httpx
import logging
from typing import Dict, Optional
from backend.config import settings

logger = logging.getLogger("weather")


async def get_weather_by_city(city_name: str) -> Optional[Dict]:
    """
    根据城市名获取天气
    优先使用 wttr.in 免费API，如果配置了和风天气Key则使用和风
    """
    # 如果有和风天气Key，优先使用（数据更精准）
    if settings.WEATHER_API_KEY:
        result = await _qweather_fetch(city_name)
        if result:
            return result

    # 默认使用 wttr.in
    return await _wttr_fetch(city_name)


async def _wttr_fetch(city_name: str) -> Optional[Dict]:
    """通过 wttr.in 获取天气"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"https://wttr.in/{city_name}",
                params={"format": "j1", "lang": "zh"},
            )
            resp.raise_for_status()
            data = resp.json()

            current = data.get("current_condition", [{}])[0]
            weather = data.get("weather", [])

            now = {
                "text": _translate_weather_code(current.get("weatherCode", "0")),
                "temp": current.get("temp_C", "?"),
                "feelsLike": current.get("FeelsLikeC", "?"),
                "humidity": current.get("humidity", "?"),
                "windDir": current.get("winddir16Point", "?"),
                "windScale": current.get("windspeedKmph", "?"),
            }

            forecast = []
            for day in weather[:3]:
                hourly = day.get("hourly", [{}])[4] if day.get("hourly") else {}
                forecast.append({
                    "fxDate": day.get("date", ""),
                    "tempMin": day.get("mintempC", "?"),
                    "tempMax": day.get("maxtempC", "?"),
                    "textDay": _translate_weather_code(hourly.get("weatherCode", "0")),
                })

            return {"city": city_name, "now": now, "forecast": forecast}
    except Exception as e:
        logger.error("wttr.in 获取天气失败: %s", e)
        return None


async def _qweather_fetch(city_name: str) -> Optional[Dict]:
    """通过和风天气API获取天气"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            geo_resp = await client.get(
                "https://geoapi.qweather.com/v2/city/lookup",
                params={"location": city_name, "key": settings.WEATHER_API_KEY},
            )
            geo_data = geo_resp.json()
            if not geo_data.get("location"):
                return None
            city_id = geo_data["location"][0]["id"]
            city_name_cn = geo_data["location"][0]["name"]

            weather_resp = await client.get(
                "https://devapi.qweather.com/v7/weather/now",
                params={"location": city_id, "key": settings.WEATHER_API_KEY},
            )
            weather_data = weather_resp.json()

            forecast_resp = await client.get(
                "https://devapi.qweather.com/v7/weather/3d",
                params={"location": city_id, "key": settings.WEATHER_API_KEY},
            )
            forecast_data = forecast_resp.json()

            return {
                "city": city_name_cn,
                "now": weather_data.get("now", {}),
                "forecast": forecast_data.get("daily", [])[:3],
            }
    except Exception as e:
        logger.error("和风天气获取失败: %s", e)
        return None


def _translate_weather_code(code: str) -> str:
    """wttr.in 天气代码转中文"""
    mapping = {
        "113": "晴", "116": "多云", "119": "阴", "122": "阴",
        "143": "雾", "176": "小雨", "179": "小雪",
        "182": "雨夹雪", "185": "雨夹雪",
        "200": "雷阵雨", "227": "暴风雪",
        "230": "暴风雪", "248": "雾", "260": "雾",
        "263": "小雨", "266": "小雨", "281": "雨夹雪",
        "284": "雨夹雪", "293": "小雨", "296": "小雨",
        "299": "中雨", "302": "中雨", "305": "大雨",
        "308": "大雨", "311": "雨夹雪", "314": "雨夹雪",
        "317": "雨夹雪", "320": "雨夹雪",
        "323": "小雪", "326": "小雪", "329": "中雪",
        "332": "中雪", "335": "大雪", "338": "大雪",
        "350": "冰雹", "353": "阵雨", "356": "中雨",
        "359": "大雨", "362": "雨夹雪", "365": "雨夹雪",
        "368": "小雪", "371": "大雪", "374": "冰雹",
        "377": "冰雹", "386": "雷阵雨", "389": "雷阵雨",
        "392": "雷阵雨", "395": "大雪",
    }
    return mapping.get(code, "多云")


def format_weather_for_prompt(weather_data: Dict) -> str:
    """将天气数据格式化为AI提示词可用的文本"""
    now = weather_data.get("now", {})
    city = weather_data.get("city", "")
    forecast = weather_data.get("forecast", [])

    text = f"""
城市: {city}
当前天气: {now.get('text', '未知')}
温度: {now.get('temp', '?')}°C
体感温度: {now.get('feelsLike', '?')}°C
湿度: {now.get('humidity', '?')}%
风向: {now.get('windDir', '?')} {now.get('windScale', '?')}级
"""

    if forecast:
        text += "\n未来3天预报:\n"
        for day in forecast:
            text += f"- {day.get('fxDate', '')}: {day.get('textDay', '')}, {day.get('tempMin', '')}°C ~ {day.get('tempMax', '')}°C\n"

    return text