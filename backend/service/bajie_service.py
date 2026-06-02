"""
八戒游戏与角色服务
提供灯谜游戏、飞花令诗词对句、情绪疏导、社交僚机等功能
"""
import json
import os
import random
from typing import Dict, List, Optional
from backend.utils.deepseek_util import chat_completion


# 加载数据文件
_data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def _load_json(filename: str):
    path = os.path.join(_data_dir, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


class BajieService:
    """八戒角色服务：游戏、灯谜、诗词、情绪、社交"""

    def __init__(self):
        self.riddles = _load_json("riddles.json") or []
        self.persona = _load_json("bajie_persona.json") or {}

    # ========== 灯谜游戏 ==========

    def get_random_riddle(self, difficulty: str = None) -> Dict:
        """
        随机获取一道灯谜
        :param difficulty: 可选筛选难度 (简单/中等/困难)
        :return: {text, hint, difficulty, category} 不含答案
        """
        pool = self.riddles
        if difficulty:
            pool = [r for r in pool if r.get("difficulty") == difficulty]
        if not pool:
            pool = self.riddles
        if not pool:
            return {"text": "俺老猪今天没带灯谜本子", "hint": "暂无提示", "difficulty": "简单", "category": ""}
        riddle = random.choice(pool)
        return {
            "text": riddle["text"],
            "hint": riddle.get("hint", ""),
            "difficulty": riddle.get("difficulty", "简单"),
            "category": riddle.get("category", ""),
            # 不返回答案，由 check_riddle_answer 校验
        }

    def check_riddle_answer(self, riddle_text: str, user_answer: str) -> Dict:
        """
        检查灯谜答案（支持模糊匹配）
        :param riddle_text: 谜面
        :param user_answer: 用户回答
        :return: {correct: bool, answer: str, message: str, score_change: int}
        """
        # 找到对应的谜题
        matched = None
        for r in self.riddles:
            if r["text"] == riddle_text:
                matched = r
                break

        if not matched:
            return {"correct": False, "answer": "未知", "message": "哼哼～这题俺老猪都忘了是哪个了...", "score_change": 0}

        correct_answer = matched["answer"]
        user_clean = user_answer.strip().lower()
        answer_clean = correct_answer.strip().lower()

        # 完全匹配或包含匹配
        if user_clean == answer_clean or user_clean in answer_clean or answer_clean in user_clean:
            messages = [
                "哼哼～对对对！就是它！俺老猪就知道你行！",
                "嘿嘿，猜对啦！看来你这呆子还挺聪明！",
                "没错！俺老猪的谜题都被你破了，改天再来一题！",
            ]
            return {"correct": True, "answer": correct_answer, "message": random.choice(messages), "score_change": 10}
        else:
            messages = [
                f"嘿嘿，不对不对！答案其实是「{correct_answer}」。没事，俺老猪以前也猜不出来！",
                f"哼哼～差一点！告诉你吧，答案是「{correct_answer}」。再试试别的题？",
                f"可惜啦！是「{correct_answer}」才对。别灰心，俺当年在天庭猜灯谜也老输！",
            ]
            return {"correct": False, "answer": correct_answer, "message": random.choice(messages), "score_change": 0}

    # ========== 飞花令 / 诗词对句 ==========

    def get_random_poetry(self) -> Dict:
        """
        随机获取诗词上句
        :return: {line, source, answer}
        """
        poetries = [
            {"line": "床前明月光", "source": "李白《静夜思》", "answer": "疑是地上霜"},
            {"line": "白日依山尽", "source": "王之涣《登鹳雀楼》", "answer": "黄河入海流"},
            {"line": "春眠不觉晓", "source": "孟浩然《春晓》", "answer": "处处闻啼鸟"},
            {"line": "锄禾日当午", "source": "李绅《悯农》", "answer": "汗滴禾下土"},
            {"line": "离离原上草", "source": "白居易《赋得古原草送别》", "answer": "一岁一枯荣"},
            {"line": "鹅鹅鹅", "source": "骆宾王《咏鹅》", "answer": "曲项向天歌"},
            {"line": "日照香炉生紫烟", "source": "李白《望庐山瀑布》", "answer": "遥看瀑布挂前川"},
            {"line": "两个黄鹂鸣翠柳", "source": "杜甫《绝句》", "answer": "一行白鹭上青天"},
            {"line": "独在异乡为异客", "source": "王维《九月九日忆山东兄弟》", "answer": "每逢佳节倍思亲"},
            {"line": "京口瓜洲一水间", "source": "王安石《泊船瓜洲》", "answer": "钟山只隔数重山"},
            {"line": "月落乌啼霜满天", "source": "张继《枫桥夜泊》", "answer": "江枫渔火对愁眠"},
            {"line": "远上寒山石径斜", "source": "杜牧《山行》", "answer": "白云深处有人家"},
            {"line": "千山鸟飞绝", "source": "柳宗元《江雪》", "answer": "万径人踪灭"},
            {"line": "松下问童子", "source": "贾岛《寻隐者不遇》", "answer": "言师采药去"},
            {"line": "春蚕到死丝方尽", "source": "李商隐《无题》", "answer": "蜡炬成灰泪始干"},
        ]
        chosen = random.choice(poetries)
        return {"line": chosen["line"], "source": chosen["source"]}

    async def check_poetry_answer(self, line: str, user_answer: str) -> Dict:
        """
        检查对诗答案，使用DeepSeek语义相似度评判
        :param line: 上句
        :param user_answer: 用户对的下句
        :return: {correct, correct_answer, message}
        """
        known_answers = {
            "床前明月光": "疑是地上霜",
            "白日依山尽": "黄河入海流",
            "春眠不觉晓": "处处闻啼鸟",
            "锄禾日当午": "汗滴禾下土",
            "离离原上草": "一岁一枯荣",
            "鹅鹅鹅": "曲项向天歌",
        }

        correct_answer = known_answers.get(line, "")
        if not correct_answer:
            return {"correct": False, "correct_answer": "", "message": "俺老猪不记得这道题了..."}

        user_clean = user_answer.strip()
        if user_clean == correct_answer:
            return {
                "correct": True, "correct_answer": correct_answer,
                "message": "对得好！就是这句！俺老猪在天庭时也常听文曲星念这个！",
            }

        # 语义相似度评判（用DeepSeek判断）
        try:
            prompt = f"""请判断用户对出的诗句是否与原诗下句意思一致或接近。
上句：{line}
原诗下句：{correct_answer}
用户对答：{user_clean}

只需要回复"对"（意思相近可以算对）或"错"（意思不对），然后给一句简短评价。"""
            result = await chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3, max_tokens=100,
            )
            is_correct = result.startswith("对")
            return {
                "correct": is_correct,
                "correct_answer": correct_answer,
                "message": f"哼哼～{'对啦！' if is_correct else '不对哦，来看看标准答案。'}\n{result}",
            }
        except Exception:
            return {
                "correct": False,
                "correct_answer": correct_answer,
                "message": f"不对哦，标准答案是「{correct_answer}」，记住它吧！",
            }

    # ========== 情绪疏导 ==========

    def is_night_time(self) -> bool:
        """检查当前是否为深夜时段 (22:00-06:00)"""
        from datetime import datetime
        hour = datetime.now().hour
        return hour >= 22 or hour < 6

    def get_night_greeting(self) -> str:
        """获取深夜关怀话术"""
        night_msgs = self.persona.get("emotional_counseling", {}).get(
            "night_mode", {}).get("messages", [])
        if night_msgs:
            return random.choice(night_msgs)
        return "都这么晚了还没睡？俺老猪都睡醒一觉了。有啥心事跟俺说说？"

    async def emotional_support(self, user_message: str, user_name: str = None) -> str:
        """
        情绪疏导（共情五步法）
        :param user_message: 用户倾诉内容
        :param user_name: 用户名称
        :return: 八戒的安慰回复
        """
        five_step = self.persona.get("emotional_counseling", {}).get("five_step_method", {})
        system_prompt = self.persona.get("system_prompts", {}).get("emotional_support",
            "你是猪八戒，正在安慰一个心情不好的朋友。")

        prompt = f"""用户正在向你倾诉烦恼。请按照以下五步法进行情绪疏导：

{json.dumps(five_step, ensure_ascii=False, indent=2)}

用户说：{user_message}

请用猪八戒的口吻（自称俺老猪），自然地融合五步法给出安慰回复。不要机械地列出步骤，要自然地融入对话。"""

        reply = await chat_completion(
            messages=[{"role": "user", "content": prompt}],
            system_prompt=system_prompt,
            temperature=0.8,
            max_tokens=500,
        )
        return reply

    # ========== 社交僚机 ==========

    async def generate_chat_lines(self, scenario: str, personality: str,
                                  extra_info: str = "") -> List[str]:
        """
        生成聊天话术
        :param scenario: 场景 (first_meet/flirt/apologize/care/invite/confess)
        :param personality: 对方性格
        :param extra_info: 额外信息
        :return: 话术列表
        """
        scenario_map = {
            "first_meet": "初次搭讪",
            "flirt": "暧昧升温",
            "apologize": "道歉求和",
            "care": "日常关心",
            "invite": "约会邀约",
            "confess": "表白心意",
        }
        personality_map = {
            "outgoing": "活泼开朗",
            "shy": "文静内敛",
            "independent": "独立强势",
            "gentle": "温柔体贴",
        }

        scene_cn = scenario_map.get(scenario, scenario)
        pers_cn = personality_map.get(personality, personality)

        prompt = f"""请以猪八戒（前天蓬元帅、自称俺老猪）的口吻，为以下场景生成3条聊天话术：
- 场景：{scene_cn}
- 对方性格：{pers_cn}
- 补充信息：{extra_info or '无'}

要求：
1. 用猪八戒的幽默诙谐语气，接地气
2. 话术要实用，不是搞笑段子
3. 每条话术50-100字
4. 按场景分【开场】、【互动】、【推进】三个步骤

直接输出3条话术，每条一行。"""

        reply = await chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=600,
        )

        lines = [l.strip().lstrip("0123456789.、- ") for l in reply.split("\n") if l.strip()]
        return lines[:3] if len(lines) >= 3 else lines

    async def write_love_letter(self, to: str, style: str, memory: str = "") -> str:
        """
        代写情书
        :param to: 收信人昵称
        :param style: 风格 (romantic/humorous/sincere)
        :param memory: 关键回忆
        :return: 情书全文
        """
        style_map = {"romantic": "浪漫文艺", "humorous": "幽默风趣", "sincere": "朴实真诚"}
        style_cn = style_map.get(style, "浪漫文艺")

        prompt = f"""请以猪八戒的口吻写一封情书：
- 收信人：{to}
- 风格：{style_cn}
- 关键回忆：{memory or '无特殊回忆'}

要求：
1. 署名"想你的 八戒 🐷"
2. 开头用"【{to}亲启】"
3. 150-300字
4. 用猪八戒的憨厚诙谐口吻，自称"俺老猪"
5. 风格要体现所选风格特点"""

        reply = await chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=600,
        )
        return reply

    # ========== 飞花令单字接龙 ==========

    def start_feihualing(self, keyword: str = None) -> Dict:
        """
        开始飞花令单字接龙
        :param keyword: 指定字，不指定则随机选
        :return: {keyword, hint, example}
        """
        common_chars = ["花", "月", "风", "云", "山", "水", "春", "雪", "人", "心", "日", "梦", "红", "柳", "雨"]
        if not keyword:
            keyword = random.choice(common_chars)
        examples = {
            "花": "花间一壶酒，独酌无相亲。——李白《月下独酌》",
            "月": "月落乌啼霜满天，江枫渔火对愁眠。——张继《枫桥夜泊》",
            "风": "春风又绿江南岸，明月何时照我还。——王安石《泊船瓜洲》",
            "云": "云想衣裳花想容，春风拂槛露华浓。——李白《清平调》",
            "山": "会当凌绝顶，一览众山小。——杜甫《望岳》",
            "水": "问君能有几多愁，恰似一江春水向东流。——李煜《虞美人》",
            "春": "春眠不觉晓，处处闻啼鸟。——孟浩然《春晓》",
            "雪": "忽如一夜春风来，千树万树梨花开。——岑参《白雪歌送武判官归京》",
            "人": "人生自古谁无死，留取丹心照汗青。——文天祥《过零丁洋》",
            "心": "身无彩凤双飞翼，心有灵犀一点通。——李商隐《无题》",
        }
        return {
            "keyword": keyword,
            "hint": f"请说出一句含有「{keyword}」字的古诗词",
            "example": examples.get(keyword, f"如：{keyword}落知多少..."),
        }

    async def check_feihualing(self, keyword: str, user_answer: str) -> Dict:
        """
        校验飞花令单字接龙
        :param keyword: 关键字
        :param user_answer: 用户回答的诗词
        :return: {correct, message, keyword}
        """
        if not user_answer or len(user_answer.strip()) < 2:
            return {"correct": False, "message": "嘿嘿，好歹说句完整的诗嘛！", "keyword": keyword}
        if keyword not in user_answer:
            return {"correct": False, "message": f"哼哼～你这句里没有「{keyword}」字呀！再想想？", "keyword": keyword}

        prompt = f"""请判断以下诗句是否真的是古诗词（或合理仿写），以及是否含有「{keyword}」字。

诗句：{user_answer}

只需要回复JSON格式：
{{"is_poem": true/false, "comment": "简短评价（用猪八戒口吻）"}}"""
        try:
            result = await chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3, max_tokens=150,
            )
            import json as _json
            data = _json.loads(result) if result.strip().startswith("{") else {"is_poem": True, "comment": "好诗好诗！"}
            is_poem = data.get("is_poem", True)
            comment = data.get("comment", "妙哉妙哉！")
            return {
                "correct": is_poem,
                "message": f"🎉 {comment}" if is_poem else f"😅 {comment}",
                "keyword": keyword,
            }
        except Exception:
            return {"correct": True, "message": f"嘿嘿，含有「{keyword}」字，俺老猪算你过！", "keyword": keyword}

    # ========== LLM 猜灯谜 ==========

    async def generate_riddle_llm(self, topic: str = None) -> Dict:
        """
        使用LLM生成灯谜
        :param topic: 主题: 四大名著/成语/日常物品/动物/自然
        :return: {text, hint, difficulty, category, answer}
        """
        topics = ["四大名著", "成语", "日常物品", "动物", "自然现象", "历史人物"]
        if not topic or topic not in topics:
            topic = random.choice(topics)

        topic_guide = {
            "四大名著": "谜底必须是四大名著中的具体人物、典故或物品。如：孙悟空、紧箍咒、通灵宝玉。谜面要围绕该人物/物品的特征。",
            "成语": "谜底是一个四字成语。谜面要形象化描述这个成语的意思。",
            "日常物品": "谜底是生活中的常见物品。如：镜子、筷子、灯笼。谜面描述其外形或用途。",
            "动物": "谜底是常见动物。如：猫、鱼、鹰。谜面描述其特征或习性。",
            "自然现象": "谜底是自然现象。如：风、雨、彩虹。谜面描述其表现。",
            "历史人物": "谜底是中国历史知名人物。如：诸葛亮、李白。谜面提及其主要事迹或特点。",
        }

        prompt = f"""你是一个灯谜大师，请出一道高质量的灯谜。

主题：{topic}
{topic_guide.get(topic, "")}

要求：
1. 谜面特点：通过比喻、拟人、拆字、双关等手法暗示谜底，让人需要"拐个弯"才能想到，但不能完全猜不出
2. 谜底特点：是具体、明确的事物/人物/成语，不会产生歧义
3. 谜面和谜底之间要有清晰的逻辑关联
4. 用猪八戒的口吻（自称"俺老猪"）写谜面，但不要过度使用语气词影响到谜面本身的逻辑

返回JSON（只返回JSON）：
{{"text": "谜面", "answer": "谜底", "hint": "简短提示", "difficulty": "简单/中等/困难"}}"""
        try:
            result = await chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.85, max_tokens=400,
            )
            import json as _json
            start = result.find("{")
            end = result.rfind("}") + 1
            if start >= 0 and end > start:
                data = _json.loads(result[start:end])
                return {
                    "text": data.get("text", "俺老猪今天脑子转不动了..."),
                    "hint": data.get("hint", "动动脑筋"),
                    "difficulty": data.get("difficulty", "中等"),
                    "category": topic,
                    "answer": data.get("answer", "").strip(),
                }
        except Exception:
            pass
        return self.get_random_riddle()

    async def check_riddle_llm(self, riddle_text: str, correct_answer: str, user_answer: str) -> Dict:
        """校验LLM灯谜答案（宽松语义匹配 + 模糊匹配）"""
        if not user_answer.strip():
            return {"correct": False, "answer": correct_answer, "message": "你倒是猜一个呀！", "score_change": 0}

        user_clean = user_answer.strip()
        answer_clean = correct_answer.strip()

        # 1. 精确匹配
        if user_clean == answer_clean:
            return {"correct": True, "answer": correct_answer, "message": "嘿嘿，猜对啦！就是这个！俺老猪服你！", "score_change": 10}

        # 2. 包含匹配（用户答案包含谜底 或 谜底包含用户答案）
        if answer_clean and user_clean and (answer_clean in user_clean or user_clean in answer_clean):
            return {"correct": True, "answer": correct_answer, "message": f"差不多！谜底就是「{correct_answer}」，算你对啦！", "score_change": 8}

        # 3. 同义/近似判断
        prompt = f"""判断以下两个词是否指同一事物（允许简称、别名、同义词）。

谜底：{correct_answer}
用户答案：{user_clean}

只回复JSON：{{"same": true/false, "brief": "一句话说明"}}"""
        try:
            result = await chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1, max_tokens=100,
            )
            import json as _json
            data = _json.loads(result.strip()) if result.strip().startswith("{") else {"same": False}
            if data.get("same"):
                return {"correct": True, "answer": correct_answer, "message": f"对啦！「{user_clean}」就是「{correct_answer}」！", "score_change": 9}
        except Exception:
            pass

        # 4. 不对，给个提示
        hints = [
            f"嘿嘿，不对哦～谜底是「{correct_answer}」。别灰心，俺老猪以前也猜不出来！",
            f"哼哼～差一点！答案是「{correct_answer}」。再试一题？",
            f"可惜啦！谜底是「{correct_answer}」。来，俺老猪再给你换一题！",
        ]
        return {"correct": False, "answer": correct_answer, "message": random.choice(hints), "score_change": 0}

    # ========== 成语接龙 ==========

    def start_chengyu_chain(self, start_word: str = None) -> Dict:
        """开始成语接龙"""
        starters = ["一心一意", "龙马精神", "春暖花开", "万事如意", "画龙点睛", "胸有成竹", "马到成功", "花好月圆"]
        word = start_word or random.choice(starters)
        return {
            "word": word,
            "last_char": word[-1],
            "hint": f"请说一个以「{word[-1]}」字开头的成语",
            "history": [word],
        }

    async def check_chengyu(self, prev_last_char: str, user_answer: str, history: list) -> Dict:
        """校验成语接龙（宽松模式）"""
        word = user_answer.strip()
        if not word:
            return {"correct": False, "message": "你还没说成语呢！", "word": "", "next_char": ""}
        if len(word) != 4:
            return {"correct": False, "message": "嘿嘿～成语得是四个字！不过你这话倒提醒了俺...", "word": "", "next_char": ""}
        if not word[0] == prev_last_char:
            return {"correct": False, "message": f"哼哼～第一个字得是「{prev_last_char}」才行！", "word": "", "next_char": ""}
        if word in history:
            return {"correct": False, "message": "这个成语已经用过啦！俺老猪都记得，换一个！", "word": "", "next_char": ""}

        prompt = f"""判断「{word}」是否为真实汉语成语。宽松判断：常见的四字俗语、惯用语也可以算。

只回复JSON：{{"is_idiom": true/false, "meaning": "意思（10字内）", "comment": "用猪八戒口吻夸一句"}}"""
        try:
            result = await chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2, max_tokens=150,
            )
            import json as _json
            raw = result.strip()
            start = raw.find("{")
            end = raw.rfind("}") + 1
            data = _json.loads(raw[start:end]) if start >= 0 and end > start else {"is_idiom": False}
            if data.get("is_idiom", False):
                meaning = data.get("meaning", "")
                comment = data.get("comment", "好成语！")
                return {
                    "correct": True,
                    "word": word,
                    "message": f"好！「{word}」——{meaning}。{comment}",
                    "next_char": word[-1],
                }
            return {"correct": False, "message": f"「{word}」好像不是成语哦...再想想？", "word": "", "next_char": ""}
        except Exception:
            # 兜底：宽松接受4字词
            return {
                "correct": True,
                "word": word,
                "message": f"嘿嘿，俺老猪觉得「{word}」算你过！",
                "next_char": word[-1],
            }

    async def chengyu_bot_reply(self, last_char: str, history: list) -> Dict:
        """八戒自动接龙回复"""
        prompt = f"""请说出一个以「{last_char}」开头的常用四字成语。不能是以下已用过的：{history[-5:]}。

如果接不上就回复"NONE"，如果能接上就只回复成语本身。"""
        try:
            result = await chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7, max_tokens=20,
            )
            word = result.strip()
            if word and word != "NONE" and len(word) == 4 and word[0] == last_char and word not in history:
                comments = [
                    f"俺老猪接：「{word}」！到你啦～",
                    f"嘿嘿，看俺的：「{word}」！你还接得上吗？",
                    f"哼哼～「{word}」！俺老猪可不是只会吃的！",
                    f"「{word}」！怎么样，俺老猪肚子里还是有点墨水的吧？",
                ]
                return {
                    "word": word,
                    "next_char": word[-1],
                    "message": random.choice(comments),
                }
        except Exception:
            pass

        # 接不上的幽默回应
        fail_msgs = [
            f"哎哟！「{last_char}」字开头的成语...俺老猪一时想不起来了！这局算你赢！",
            f"哼哼～俺老猪脑子卡壳了，「{last_char}」字太难了！你赢啦！",
            f"散了散了！这「{last_char}」字俺接不上，猴哥来了也接不上！算你厉害！",
        ]
        return {"word": "", "next_char": last_char, "message": random.choice(fail_msgs)}

    # ========== 角色对话 ==========

    async def bajie_chat(self, user_message: str,
                         history: List[Dict[str, str]] = None) -> str:
        """
        八戒角色扮演对话
        :param user_message: 用户消息
        :param history: 历史对话
        :return: 八戒的回复
        """
        system_prompt = self.persona.get("system_prompts", {}).get("default",
            "你是猪八戒，前天蓬元帅，说话用猪八戒的口吻，自称'俺老猪'。")

        # 记忆注入
        user_id = getattr(self, '_user_id', None)
        if user_id:
            try:
                from backend.database import SessionLocal
                db = SessionLocal()
                from backend.utils.memory_retriever import MemoryRetriever
                mem = MemoryRetriever(db).build_memory_prompt(user_id, user_message)
                if mem:
                    system_prompt += "\n\n" + mem
                db.close()
            except Exception:
                pass

        messages = history or []
        messages.append({"role": "user", "content": user_message})

        reply = await chat_completion(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.85,
            max_tokens=500,
        )
        return reply
