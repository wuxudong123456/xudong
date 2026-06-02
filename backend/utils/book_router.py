"""
智能书籍路由
根据用户问题判断涉及哪本名著
策略: 关键词匹配 + LLM兜底
"""
import logging
from typing import List
from backend.utils.llm_router import chat_completion

logger = logging.getLogger("book_router")

# 关键词路由表
BOOK_KEYWORDS = {
    "novel_xiyou": [
        "孙悟空", "唐僧", "八戒", "沙僧", "如来", "观音", "取经", "大闹天宫",
        "花果山", "紧箍咒", "白骨精", "火焰山", "西天", "佛祖", "菩萨", "妖怪",
        "猴哥", "师傅", "老孙", "贫僧", "施主", "玄奘", "悟空", "悟能", "悟净",
    ],
    "novel_sanguo": [
        "刘备", "关羽", "张飞", "曹操", "诸葛亮", "孙权", "三国", "赤壁",
        "赵云", "马超", "黄忠", "魏延", "姜维", "吕布", "貂蝉", "董卓",
        "袁绍", "袁术", "刘表", "孙策", "周瑜", "鲁肃", "吕蒙", "陆逊",
        "桃园结义", "三顾茅庐", "草船借箭", "火烧赤壁", "过五关斩六将",
        "魏", "蜀", "吴", "蜀汉", "曹魏", "东吴",
    ],
    "novel_shuihu": [
        "宋江", "林冲", "武松", "李逵", "鲁智深", "梁山", "好汉", "招安",
        "吴用", "公孙胜", "关胜", "秦明", "呼延灼", "花荣", "柴进", "李应",
        "朱仝", "戴宗", "燕青", "史进", "李俊", "阮小二", "阮小五", "阮小七",
        "晁盖", "王伦", "一百单八将", "替天行道", "水泊梁山", "聚义厅",
    ],
    "novel_honglou": [
        "贾宝玉", "林黛玉", "薛宝钗", "王熙凤", "贾母", "大观园", "金陵十二钗",
        "贾政", "王夫人", "贾琏", "贾珍", "贾蓉", "贾蔷", "贾芸", "贾环",
        "史湘云", "妙玉", "贾元春", "贾迎春", "贾探春", "贾惜春",
        "袭人", "晴雯", "平儿", "鸳鸯", "紫鹃", "雪雁", "莺儿",
        "刘姥姥", "甄士隐", "冷子兴", "贾府", "荣国府", "宁国府",
        "石头记", "情僧录", "风月宝鉴",
    ],
}

# 跨书比较关键词
CROSS_BOOK_KEYWORDS = [
    "比较", "对比", "vs", "VS", "和", "与", "跟", "区别", "差异",
    "谁更", "哪个", "有什么不同", "有什么不一样",
]


def _keyword_route(question: str) -> List[str]:
    """关键词匹配路由"""
    matched = []
    for coll, keywords in BOOK_KEYWORDS.items():
        if any(kw in question for kw in keywords):
            matched.append(coll)
    return matched


def _is_cross_book_question(question: str) -> bool:
    """判断是否是跨书比较问题"""
    return any(kw in question for kw in CROSS_BOOK_KEYWORDS)


async def _llm_route_book(question: str) -> List[str]:
    """LLM判断涉及哪些书"""
    prompt = f"""分析用户问题涉及中国四大名著中的哪些。只返回JSON数组，如["novel_sanguo"]或["all"]。

四大名著:
- novel_xiyou: 《西游记》（孙悟空、唐僧、神仙妖怪、取经）
- novel_sanguo: 《三国演义》（刘备、曹操、诸葛亮、战争、三国）
- novel_shuihu: 《水浒传》（宋江、梁山好汉、招安）
- novel_honglou: 《红楼梦》（贾宝玉、林黛玉、贾府、爱情）

如果涉及多本书或无法确定，返回["all"]。

用户问题: {question}

返回格式: ["novel_xxx"] 或 ["all"]"""

    try:
        response = await chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=50,
        )
        import json
        result = json.loads(response.strip())
        if isinstance(result, list) and len(result) > 0:
            if "all" in result:
                return ["novel_xiyou", "novel_sanguo", "novel_shuihu", "novel_honglou"]
            return [r for r in result if r in BOOK_KEYWORDS]
    except Exception as e:
        logger.error("LLM路由失败: %s", e)

    # 兜底：返回全部
    return ["novel_xiyou", "novel_sanguo", "novel_shuihu", "novel_honglou"]


async def route_book(question: str) -> List[str]:
    """
    智能书籍路由
    :param question: 用户问题
    :return: 涉及的集合名列表
    """
    # 1. 检查是否是跨书比较问题
    if _is_cross_book_question(question):
        logger.info("[路由] 跨书问题，查询全部: %s", question)
        return ["novel_xiyou", "novel_sanguo", "novel_shuihu", "novel_honglou"]

    # 2. 关键词匹配
    matched = _keyword_route(question)

    # 3. 如果匹配到1本，直接返回
    if len(matched) == 1:
        logger.info("[路由] 关键词匹配: %s -> %s", question, matched[0])
        return matched

    # 4. 如果匹配到多本或没匹配到，用LLM判断
    logger.info("[路由] LLM判断: %s", question)
    return await _llm_route_book(question)
