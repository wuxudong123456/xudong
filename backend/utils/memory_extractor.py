"""
记忆提取器 — 从对话中提取关键信息，双写 MySQL + Milvus
异步 fire-and-forget，不阻塞对话回复
"""
import json
import time
import logging
import asyncio
from typing import List, Dict
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def _jaccard(text_a: str, text_b: str) -> float:
    """Jaccard 相似度（按字切分）"""
    if not text_a or not text_b:
        return 0.0
    sa = set(text_a)
    sb = set(text_b)
    inter = len(sa & sb)
    union = len(sa | sb)
    return inter / union if union > 0 else 0.0


class MemoryExtractor:

    @staticmethod
    def extract_memories(user_id: int, conversation: List[Dict[str, str]]):
        """提取记忆（fire-and-forget）"""
        asyncio.create_task(MemoryExtractor._do_extract(user_id, conversation))

    @staticmethod
    async def _do_extract(user_id: int, conversation: List[Dict[str, str]]):
        from backend.database import SessionLocal
        db = SessionLocal()
        try:
            # Step 1: LLM 提取
            memories = await MemoryExtractor._llm_extract(conversation)
            if not memories:
                return

            # Step 2: 去重
            existing = MemoryExtractor._load_existing(db, user_id)
            new_memories = []
            for m in memories:
                duplicate = False
                for ex in existing:
                    if _jaccard(m["content"], ex) > 0.3:
                        duplicate = True
                        break
                if not duplicate:
                    new_memories.append(m)

            if not new_memories:
                return

            # Step 3: 向量化 + 双写
            from backend.utils.embedding_util import get_embedding
            import uuid
            from backend.entity.memory_fragment import MemoryFragment

            for m in new_memories:
                content = m["content"]
                vec = await get_embedding(content)
                chunk_id = f"mem_{user_id}_{uuid.uuid4().hex[:8]}"

                frag = MemoryFragment(
                    user_id=user_id, content=content,
                    importance=m.get("importance", 0.5),
                    memory_type=m.get("type", "fact"),
                    source_session_id=None, chunk_id=chunk_id,
                )
                db.add(frag)
                db.flush()
                try:
                    MemoryExtractor._insert_milvus(chunk_id, user_id, content, vec)
                except Exception as e:
                    logger.warning("Milvus insert failed: %s", e)

            db.commit()
            MemoryExtractor._update_profile(db, user_id, memories)

        except Exception as e:
            logger.error("Memory extraction failed: %s", e)
            try:
                db.rollback()
            except Exception:
                pass
        finally:
            db.close()

    @staticmethod
    async def _llm_extract(conversation: List[Dict]) -> List[Dict]:
        conv_text = "\n".join([
            f"{'用户' if m['role'] == 'user' else 'AI'}: {m['content']}"
            for m in conversation
        ])
        prompt = f"""从以下对话中提取关键信息，以JSON格式返回：
{{"memories": [{{"type": "fact"|"preference"|"event"|"emotion", "content": "一句话概括", "importance": 0.0-1.0}}]}}

规则：
- fact: 用户客观事实（姓名/身份/学校/专业等）
- preference: 用户偏好（喜欢/不喜欢什么）
- event: 用户经历的或即将发生的事件
- emotion: 用户情绪状态
- importance: 越基础越持久越高（姓名=1.0, 临时情绪=0.5）
- 没有值得提取的信息返回空数组

对话:
{conv_text}"""
        from backend.utils.deepseek_util import chat_completion
        resp = await chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2, max_tokens=400,
        )
        start = resp.find("{")
        end = resp.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(resp[start:end])
            return data.get("memories", [])
        return []

    @staticmethod
    def _load_existing(db: Session, user_id: int) -> List[str]:
        from backend.entity.memory_fragment import MemoryFragment
        rows = db.query(MemoryFragment.content).filter(
            MemoryFragment.user_id == user_id
        ).all()
        return [r[0] for r in rows]

    @staticmethod
    def _insert_milvus(chunk_id: str, user_id: int,
                        content: str, vec: List[float]):
        from pymilvus import Collection
        coll = Collection("memory_vectors")
        coll.insert([[chunk_id], [user_id], [content], [vec]])
        coll.flush()

    @staticmethod
    def _update_profile(db: Session, user_id: int, memories: List[Dict]):
        from backend.entity.user_profile import UserProfile
        profile = db.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).first()
        if not profile:
            profile = UserProfile(user_id=user_id)
            db.add(profile)

        profile.interaction_count = (profile.interaction_count or 0) + 1
        profile.last_active_time = time.strftime("%Y-%m-%d %H:%M:%S")

        for m in memories:
            t = m.get("type", "")
            content = m.get("content", "")
            if t == "emotion":
                profile.last_emotion = content[:50]
            if t == "preference":
                existing = set((profile.preferred_topics or "").split(","))
                existing.add(content[:30])
                profile.preferred_topics = ",".join([x for x in existing if x][:10])
            if t == "fact":
                tags = set((profile.personality_tags or "").split(","))
                for keyword in content.split():
                    if len(keyword) >= 2:
                        tags.add(keyword[:10])
                profile.personality_tags = ",".join([x for x in tags if x][:8])
        db.commit()
