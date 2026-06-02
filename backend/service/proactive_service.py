"""
主动对话服务 — 根据用户画像和上下文自动发起搭话
"""
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, Optional
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# 触发记录字典（重启丢失无所谓）
_trigger_log: Dict[int, dict] = {}

CHARACTER_STYLES = {
    "bajie":    ("幽默接地气，自称俺老猪", 0.85),
    "luzhishen": ("豪爽直接，自称洒家", 0.80),
    "lindaiyu": ("含蓄文艺，自称我", 0.90),
    "zhugeliang": ("稳重睿智，自称亮", 0.70),
}

TIME_SLOTS = {
    (22, 6):   "深夜了",
    (6, 9):    "早上好",
    (11, 14):  "午饭时间",
}


class ProactiveService:

    @staticmethod
    def check_and_generate(user_id: int, db: Session,
                           character: str = "bajie") -> Optional[dict]:
        try:
            profile = ProactiveService._get_profile(db, user_id)
            if not profile or not profile.proactive_preference:
                return None

            # 清理过期记录
            ProactiveService._clean_log(user_id)

            # 选择最高优先级触发
            trigger_type, trigger_msg = ProactiveService._select_trigger(
                user_id, profile, db)
            if not trigger_type:
                return None

            # 防骚扰检查
            if ProactiveService._rate_limit(user_id, trigger_type):
                return None

            # 获取记忆
            mem_text = ""
            try:
                from backend.utils.memory_retriever import MemoryRetriever
                mem_text = MemoryRetriever(db).build_memory_prompt(
                    user_id, trigger_msg or "")
            except Exception:
                pass

            # 生成消息
            content = ProactiveService._generate_message(
                trigger_type, mem_text, profile, character)

            # 记录触发
            ProactiveService._record_trigger(user_id, trigger_type)

            return {"type": trigger_type, "content": content}

        except Exception as e:
            logger.error("Proactive check failed: %s", e)
            return None

    # ===== 触发选择 =====

    @staticmethod
    def _select_trigger(user_id: int, profile, db: Session) -> tuple:
        now = datetime.now()
        triggers = []

        # 1. 见面问候: > 1小时
        if profile.last_active_time:
            last = profile.last_active_time
            if isinstance(last, str):
                last = datetime.fromisoformat(last.replace("Z", "+00:00"))
            gap = (now - last.replace(tzinfo=None) if hasattr(last, 'tzinfo') and last.tzinfo
                   else now - last).total_seconds()
            if gap > 3600:
                triggers.append((1, "greeting", f"距上次对话 {int(gap/60)} 分钟"))

        # 2. 沉默搭话: 最后消息 > 2分钟
        last_msg = ProactiveService._get_last_message(db, user_id)
        if last_msg:
            gap = (now - last_msg).total_seconds()
            if 120 < gap < 1800:
                triggers.append((2, "silence", "用户沉默了一会儿"))

        # 3. 时段关怀
        hour = now.hour
        for (start, end), label in TIME_SLOTS.items():
            if (start <= hour < end) or (start > end and (hour >= start or hour < end)):
                triggers.append((3, "time_care", f"现在是{label}"))
                break

        # 4. 事件提醒: 记忆中有日期事件
        from backend.entity.memory_fragment import MemoryFragment
        events = db.query(MemoryFragment).filter(
            MemoryFragment.user_id == user_id,
            MemoryFragment.memory_type == "event",
        ).order_by(MemoryFragment.created_at.desc()).limit(3).all()
        for ev in events:
            triggers.append((4, "event_reminder", ev.content[:50]))

        # 5. 情绪追踪: 负面情绪 + > 24小时
        if profile.last_emotion and profile.last_active_time:
            last = profile.last_active_time
            if isinstance(last, str):
                last = datetime.fromisoformat(last.replace("Z", "+00:00"))
            if (now - last.replace(tzinfo=None) if hasattr(last, 'tzinfo') and last.tzinfo
                else now - last).total_seconds() > 86400:
                negative = ["难过", "焦虑", "伤心", "生气", "烦躁", "郁闷"]
                if any(w in (profile.last_emotion or "") for w in negative):
                    triggers.append((5, "emotion_check", profile.last_emotion))

        # 6. 兴趣激活
        if profile.preferred_topics:
            topics = [t for t in profile.preferred_topics.split(",") if t]
            if topics:
                triggers.append((6, "interest", random.choice(topics)))

        if not triggers:
            return None, None

        triggers.sort(key=lambda x: x[0])
        return triggers[0][1], triggers[0][2]

    # ===== 防骚扰 =====

    @staticmethod
    def _rate_limit(user_id: int, trigger_type: str) -> bool:
        log = _trigger_log.get(user_id, {})
        now = datetime.now()

        # 每小时最多5条
        hourly = [t for t in log.get("hourly_count", [])
                  if (now - t[1]).total_seconds() < 3600]
        if len(hourly) >= 5:
            return True  # 超限

        # 同类型间隔
        intervals = {
            "greeting": 1800, "silence": 600, "time_care": 14400,
            "event_reminder": 3600, "emotion_check": 86400, "interest": 7200,
        }
        last_key = f"last_{trigger_type}"
        last_time = log.get(last_key)
        if last_time and (now - last_time).total_seconds() < intervals.get(trigger_type, 600):
            return True

        return False

    @staticmethod
    def _record_trigger(user_id: int, trigger_type: str):
        now = datetime.now()
        if user_id not in _trigger_log:
            _trigger_log[user_id] = {}
        log = _trigger_log[user_id]
        log[f"last_{trigger_type}"] = now
        hourly = log.get("hourly_count", [])
        hourly.append((trigger_type, now))
        log["hourly_count"] = hourly

    @staticmethod
    def _clean_log(user_id: int):
        log = _trigger_log.get(user_id, {})
        if not log:
            return
        now = datetime.now()
        log["hourly_count"] = [t for t in log.get("hourly_count", [])
                               if (now - t[1]).total_seconds() < 3600]

    # ===== 消息生成 =====

    @staticmethod
    def _generate_message(trigger_type: str, mem_text: str,
                          profile, character: str) -> str:
        style, temp = CHARACTER_STYLES.get(character, ("幽默接地气", 0.85))

        # 亲密度
        count = profile.interaction_count or 0
        if count < 5:
            intimacy = "礼貌疏离，不要过于热情"
        elif count < 20:
            intimacy = "适度亲近，像普通朋友"
        else:
            intimacy = "亲密老友，可以开玩笑"

        profile_text = ""
        if profile.preferred_topics:
            topics = profile.preferred_topics.split(",")[:3]
            profile_text = f"用户兴趣: {', '.join(topics)}"
        if profile.last_emotion:
            profile_text += f"\n最近情绪: {profile.last_emotion}"

        trigger_guide = {
            "greeting": "用户刚回来，打个招呼，问候一下",
            "silence": "用户沉默了一会儿，轻轻搭个话但别追问",
            "time_care": f"现在是{trigger_type}，提醒用户注意休息/吃饭",
            "event_reminder": "提醒用户之前提到的事件",
            "emotion_check": "用户之前情绪不好，关心一下现在怎么样了",
            "interest": f"聊聊用户感兴趣的 {trigger_type}",
        }

        prompt = f"""你是{character}，{style}。
亲密度: {intimacy}
{profile_text}
{mem_text}

场景: {trigger_guide.get(trigger_type, '随便聊聊')}

请说一句话，20-50字，自然不生硬。"""

        try:
            from backend.utils.deepseek_util import chat_completion
            import asyncio
            reply = asyncio.get_event_loop().run_until_complete(
                chat_completion(
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temp, max_tokens=80,
                )
            )
            # 安全过滤
            reply = reply.strip()
            if len(reply) < 3 or len(reply) > 100:
                return ProactiveService._fallback(character)
            # 过滤敏感追问
            sensitive = ["你家住哪", "电话多少", "身份证", "银行卡", "密码"]
            if any(w in reply for w in sensitive):
                return ProactiveService._fallback(character)
            return reply
        except Exception:
            return ProactiveService._fallback(character)

    @staticmethod
    def _fallback(character: str) -> str:
        defaults = {
            "bajie": "哼哼～俺老猪来也！有啥新鲜事跟俺说说？",
            "luzhishen": "洒家正闲着呢，有啥事尽管说！",
            "lindaiyu": "你来了？我正觉得有些闷，陪我说话吧。",
            "zhugeliang": "亮在此恭候多时，阁下请讲。",
        }
        return defaults.get(character, "你好呀，有什么新鲜事吗？")

    # ===== 数据查询 =====

    @staticmethod
    def _get_profile(db: Session, user_id: int):
        from backend.entity.user_profile import UserProfile
        return db.query(UserProfile).filter(
            UserProfile.user_id == user_id).first()

    @staticmethod
    def _get_last_message(db: Session, user_id: int):
        from backend.entity.conversation_history import ConversationHistory
        row = db.query(ConversationHistory.create_time).filter(
            ConversationHistory.user_id == user_id,
            ConversationHistory.role == "user",
        ).order_by(ConversationHistory.id.desc()).first()
        return row[0] if row else None
