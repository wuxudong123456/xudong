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
