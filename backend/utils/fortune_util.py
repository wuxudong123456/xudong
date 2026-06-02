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
