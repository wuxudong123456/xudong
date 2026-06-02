# 新增功能：天气预测 + 运势占卜 实施计划

> **Goal:** 为八戒智能体添加天气查询和每日运势占卜功能
> **Architecture:** 外部API集成 + AI生成个性化内容
> **Tech Stack:** 和风天气API / OpenWeatherMap, DeepSeek/阿里云生成

---

## 功能概述

### 1. 天气预测 (Weather Agent)

**功能描述:**
- 用户询问"今天天气怎么样？""明天北京会下雨吗？"
- 八戒调用天气API获取实时数据
- 用八戒口吻回复，带穿衣建议、出行提醒

**技术方案:**
- 天气数据源: 和风天气API (免费版够用) 或 OpenWeatherMap
- 需要用户位置: 前端获取浏览器定位，或用户手动输入城市
- AI增强: 用DeepSeek/阿里云将天气数据转为八戒口吻的个性化建议

**API选择:**
```
和风天气: https://dev.qweather.com/ (免费1000次/天)
- 实时天气: /v7/weather/now
- 未来3天: /v7/weather/3d
- 需要申请Key

OpenWeatherMap: https://openweathermap.org/api (免费1000次/天)
- 当前天气: /data/2.5/weather
- 预报: /data/2.5/forecast
```

**数据流转:**
```
用户: "今天天气怎么样？"
  ↓
意图分类: weather_query
  ↓
WeatherAgent:
  1. 提取城市名（从消息或用户资料）
  2. 调用天气API获取数据
  3. 用AI生成八戒口吻回复
  ↓
回复: "哼哼～俺老猪看了眼天象，今天北京晴转多云，25度。
      穿件薄外套就行，别学俺老猪穿那么厚！"
```

---

### 2. 运势占卜 (Fortune Agent)

**功能描述:**
- 用户说"帮我算一卦""今天运势如何？"
- 八戒根据用户星座/生肖/生辰生成每日运势
- 包含: 综合运势、爱情运、事业运、财运、幸运色、幸运数字

**技术方案:**
- 运势生成: 用DeepSeek/阿里云生成个性化运势内容
- 个性化因子:
  - 用户星座 (需要用户资料扩展)
  - 用户生肖 (从生日推算)
  - 当前日期 (每日运势变化)
  - 用户历史交互 (记忆系统)
- 格式: 结构化JSON → 前端卡片展示

**数据流转:**
```
用户: "帮我算一卦"
  ↓
意图分类: fortune_telling
  ↓
FortuneAgent:
  1. 获取用户资料（星座、生肖）
  2. 获取当前日期
  3. 用AI生成运势内容（结构化）
  4. 存入记忆（用户今日已占卜）
  ↓
回复: JSON格式
{
  "overall": "⭐⭐⭐⭐ 运势不错",
  "love": "桃花运旺，适合表白",
  "career": "工作效率高，领导赏识",
  "wealth": "有小财进账，但别贪心",
  "lucky_color": "红色",
  "lucky_number": "8",
  "advice": "今天适合出门走走，说不定能遇到贵人"
}
```

---

## 文件变更总览

| 操作 | 文件 | 说明 |
|------|------|------|
| 新建 | `backend/utils/weather_util.py` | 天气API封装 |
| 新建 | `backend/utils/fortune_util.py` | 运势生成工具 |
| 新建 | `backend/service/weather_service.py` | 天气服务 |
| 新建 | `backend/service/fortune_service.py` | 运势服务 |
| 新建 | `backend/controller/weather_controller.py` | 天气接口 |
| 新建 | `backend/controller/fortune_controller.py` | 运势接口 |
| 修改 | `backend/service/agent_service.py` | 增加weather/fortune意图 |
| 修改 | `frontend/src/views/bajie/` | 新增运势页面/天气展示 |
| 修改 | `backend/config.py` | 天气API配置 |

---

## Task 1: 天气功能实现

**Files:**
- 新建: `backend/utils/weather_util.py`
- 新建: `backend/service/weather_service.py`
- 新建: `backend/controller/weather_controller.py`
- 修改: `backend/config.py`

**Step 1: 天气API封装**

```python
# backend/utils/weather_util.py
"""
天气查询工具
封装和风天气API / OpenWeatherMap
"""
import httpx
import logging
from typing import Dict, Optional
from backend.config import settings

logger = logging.getLogger(__name__)


async def get_weather_by_city(city_name: str) -> Optional[Dict]:
    """
    根据城市名获取天气
    使用和风天气API
    """
    if not settings.WEATHER_API_KEY:
        logger.warning("天气API Key未配置")
        return None
    
    try:
        # 1. 城市名转城市ID
        async with httpx.AsyncClient(timeout=10.0) as client:
            geo_resp = await client.get(
                "https://geoapi.qweather.com/v2/city/lookup",
                params={
                    "location": city_name,
                    "key": settings.WEATHER_API_KEY,
                }
            )
            geo_data = geo_resp.json()
            if not geo_data.get("location"):
                return None
            city_id = geo_data["location"][0]["id"]
            city_name = geo_data["location"][0]["name"]
            
            # 2. 获取实时天气
            weather_resp = await client.get(
                "https://devapi.qweather.com/v7/weather/now",
                params={
                    "location": city_id,
                    "key": settings.WEATHER_API_KEY,
                }
            )
            weather_data = weather_resp.json()
            
            # 3. 获取未来3天预报
            forecast_resp = await client.get(
                "https://devapi.qweather.com/v7/weather/3d",
                params={
                    "location": city_id,
                    "key": settings.WEATHER_API_KEY,
                }
            )
            forecast_data = forecast_resp.json()
            
            return {
                "city": city_name,
                "now": weather_data.get("now", {}),
                "forecast": forecast_data.get("daily", [])[:3],
            }
    except Exception as e:
        logger.error("获取天气失败: %s", e)
        return None


def format_weather_for_prompt(weather_data: Dict) -> str:
    """将天气数据格式化为AI提示词可用的文本"""
    now = weather_data.get("now", {})
    city = weather_data.get("city", "")
    
    return f"""
城市: {city}
当前天气: {now.get('text', '未知')}
温度: {now.get('temp', '?')}°C
体感温度: {now.get('feelsLike', '?')}°C
湿度: {now.get('humidity', '?')}%
风向: {now.get('windDir', '?')} {now.get('windScale', '?')}级
"""
```

**Step 2: 天气服务**

```python
# backend/service/weather_service.py
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
```

**Step 3: 天气接口**

```python
# backend/controller/weather_controller.py
"""
天气查询接口
"""
from fastapi import APIRouter, Query, Depends
from backend.dependencies import get_current_user
from backend.entity.user import User
from backend.service.weather_service import WeatherService

router = APIRouter()


@router.get("/now", summary="查询当前天气")
async def get_weather(
    city: str = Query(..., description="城市名，如: 北京、上海"),
    current_user: User = Depends(get_current_user),
):
    """查询指定城市的当前天气，返回八戒口吻的回复"""
    service = WeatherService()
    reply = await service.get_weather_reply(city)
    return {"code": 200, "message": "success", "data": {"city": city, "reply": reply}}
```

**Step 4: 配置扩展**

```python
# backend/config.py 增加
WEATHER_API_KEY: str = Field(default="", alias="WEATHER_API_KEY")
```

---

## Task 2: 运势功能实现

**Files:**
- 新建: `backend/utils/fortune_util.py`
- 新建: `backend/service/fortune_service.py`
- 新建: `backend/controller/fortune_controller.py`

**Step 1: 运势生成工具**

```python
# backend/utils/fortune_util.py
"""
运势生成工具
根据星座/生肖/日期生成每日运势
"""
from datetime import datetime
from typing import Dict


def get_zodiac_sign(month: int, day: int) -> str:
    """根据生日获取星座"""
    dates = [(1, 20, "水瓶座"), (2, 19, "双鱼座"), (3, 21, "白羊座"),
             (4, 20, "金牛座"), (5, 21, "双子座"), (6, 21, "巨蟹座"),
             (7, 23, "狮子座"), (8, 23, "处女座"), (9, 23, "天秤座"),
             (10, 23, "天蝎座"), (11, 22, "射手座"), (12, 22, "摩羯座")]
    
    for m, d, sign in dates:
        if (month, day) <= (m, d):
            return sign
    return "摩羯座"


def get_chinese_zodiac(year: int) -> str:
    """根据年份获取生肖"""
    animals = ["猴", "鸡", "狗", "猪", "鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊"]
    return animals[year % 12]


def get_lucky_color(seed: int) -> str:
    """根据种子生成幸运色"""
    colors = ["红色", "橙色", "黄色", "绿色", "青色", "蓝色", "紫色", "粉色", "白色", "黑色"]
    return colors[seed % len(colors)]


def get_lucky_number(seed: int) -> int:
    """根据种子生成幸运数字"""
    return (seed % 9) + 1
```

**Step 2: 运势服务**

```python
# backend/service/fortune_service.py
"""
运势占卜服务
生成个性化每日运势
"""
import json
import random
from datetime import datetime
from typing import Dict
from backend.utils.llm_router import chat_completion
from backend.utils.fortune_util import (
    get_zodiac_sign, get_chinese_zodiac,
    get_lucky_color, get_lucky_number
)


class FortuneService:
    """运势服务"""
    
    async def generate_fortune(self, birth_date: str = None, zodiac: str = None) -> Dict:
        """
        生成每日运势
        :param birth_date: 生日 (YYYY-MM-DD)
        :param zodiac: 直接指定星座
        :return: 运势数据
        """
        today = datetime.now()
        
        # 确定星座
        if zodiac:
            sign = zodiac
        elif birth_date:
            dt = datetime.strptime(birth_date, "%Y-%m-%d")
            sign = get_zodiac_sign(dt.month, dt.day)
        else:
            sign = "未知"
        
        # 生成种子（基于日期，保证同一天结果一致）
        seed = int(today.strftime("%Y%m%d")) + hash(sign) % 10000
        random.seed(seed)
        
        # 用AI生成运势内容
        prompt = f"""你是猪八戒，正在给朋友算今日运势。

朋友信息:
- 星座: {sign}
- 日期: {today.strftime("%Y年%m月%d日")}

请生成今日运势，以JSON格式返回:
{{
  "overall_score": 1-5,
  "overall_text": "综合运势描述（20字以内）",
  "love_score": 1-5,
  "love_text": "爱情运势描述（30字以内）",
  "career_score": 1-5,
  "career_text": "事业运势描述（30字以内）",
  "wealth_score": 1-5,
  "wealth_text": "财运描述（30字以内）",
  "health_score": 1-5,
  "health_text": "健康建议（30字以内）",
  "advice": "今日建议（50字以内，用猪八戒口吻）"
}}

注意:
1. 运势要有变化，不能每天都是大吉
2. 描述要用猪八戒的口吻，自称"俺老猪"
3. 建议要实用且幽默"""
        
        try:
            reply = await chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9,
                max_tokens=500,
            )
            
            # 解析JSON
            fortune = json.loads(reply)
            
            # 添加固定字段
            fortune.update({
                "date": today.strftime("%Y-%m-%d"),
                "zodiac": sign,
                "lucky_color": get_lucky_color(seed),
                "lucky_number": get_lucky_number(seed),
                "lucky_direction": random.choice(["东", "南", "西", "北", "东南", "东北", "西南", "西北"]),
            })
            
            return fortune
            
        except Exception:
            # AI生成失败，返回默认运势
            return self._default_fortune(sign, today, seed)
    
    def _default_fortune(self, sign: str, today: datetime, seed: int) -> Dict:
        """默认运势（AI失败时使用）"""
        random.seed(seed)
        scores = {k: random.randint(2, 5) for k in ["overall", "love", "career", "wealth", "health"]}
        
        texts = {
            5: "大吉大利，万事如意",
            4: "运势不错，把握机会",
            3: "平平淡淡，稳中求进",
            2: "小有波折，谨慎行事",
            1: "运势低迷，多加小心",
        }
        
        return {
            "date": today.strftime("%Y-%m-%d"),
            "zodiac": sign,
            "overall_score": scores["overall"],
            "overall_text": texts[scores["overall"]],
            "love_score": scores["love"],
            "love_text": texts[scores["love"]],
            "career_score": scores["career"],
            "career_text": texts[scores["career"]],
            "wealth_score": scores["wealth"],
            "wealth_text": texts[scores["wealth"]],
            "health_score": scores["health"],
            "health_text": texts[scores["health"]],
            "advice": "俺老猪掐指一算，今天适合吃顿好的，心情好了运势自然旺！",
            "lucky_color": get_lucky_color(seed),
            "lucky_number": get_lucky_number(seed),
            "lucky_direction": random.choice(["东", "南", "西", "北"]),
        }
```

**Step 3: 运势接口**

```python
# backend/controller/fortune_controller.py
"""
运势占卜接口
"""
from fastapi import APIRouter, Query, Depends
from backend.dependencies import get_current_user
from backend.entity.user import User
from backend.service.fortune_service import FortuneService

router = APIRouter()


@router.get("/today", summary="今日运势")
async def get_today_fortune(
    zodiac: str = Query(None, description="星座，如: 白羊座"),
    current_user: User = Depends(get_current_user),
):
    """生成今日运势"""
    service = FortuneService()
    
    # 尝试从用户资料获取生日
    birth_date = None
    # TODO: 从user_profile获取
    
    fortune = await service.generate_fortune(birth_date=birth_date, zodiac=zodiac)
    return {"code": 200, "message": "success", "data": fortune}
```

---

## Task 3: 意图分类扩展

**修改: `backend/service/agent_service.py`**

在 `INTENT_CLASSIFIER_PROMPT` 中增加:
```
- weather_query: 查询天气（如"今天天气怎么样""北京会下雨吗"）
- fortune_telling: 运势占卜（如"帮我算一卦""今天运势如何"）
```

在 `process_message` 中增加路由:
```python
elif intent == "weather_query":
    agent_name = "WeatherAgent"
    reply, data = await self._handle_weather(message)
elif intent == "fortune_telling":
    agent_name = "FortuneAgent"
    reply, data = await self._handle_fortune(message)
```

---

## Task 4: 前端页面

**新建: `frontend/src/views/bajie/FortuneTelling.vue`**

运势占卜页面，包含:
- 星座选择
- 运势卡片展示（五星评分）
- 幸运色/数字/方向展示
- 每日建议

**修改: `frontend/src/router/index.js`**

增加路由:
```javascript
{
  path: 'bajie/fortune',
  name: 'FortuneTelling',
  component: () => import('@/views/bajie/FortuneTelling.vue'),
  meta: { title: '每日运势', icon: 'Star' },
}
```

---

## 验证清单

- [ ] 天气查询返回正确城市天气
- [ ] 天气回复是八戒口吻
- [ ] 运势生成包含所有字段
- [ ] 同一天同一星座运势一致
- [ ] 不同日期运势有变化
- [ ] 前端运势页面展示正常
- [ ] 意图分类能正确识别天气/运势查询
