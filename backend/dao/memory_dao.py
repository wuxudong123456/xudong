"""
通用记忆数据访问层
"""
import uuid
from typing import Optional, List, Dict
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from backend.entity.conversation_history import ConversationHistory


class MemoryDAO:
    """通用记忆 DAO — 所有模块的记忆存取统一入口"""

    def __init__(self, db: Session):
        self.db = db

    # ===== 消息存取 =====

    def save_message(self, user_id: int, session_id: str, role: str,
                     content: str, memory_type: str = "chat",
                     character: str = None, agent_type: str = None,
                     extra_data: dict = None) -> ConversationHistory:
        msg = ConversationHistory(
            user_id=user_id, session_id=session_id,
            memory_type=memory_type, role=role, character=character,
            content=content, agent_type=agent_type,
            extra_data=extra_data,
        )
        self.db.add(msg)
        self.db.flush()
        return msg

    def commit(self):
        self.db.commit()

    def get_session_messages(self, session_id: str, limit: int = 50,
                             user_id: int = None) -> List[ConversationHistory]:
        q = self.db.query(ConversationHistory).filter(
            ConversationHistory.session_id == session_id
        ).order_by(ConversationHistory.id.asc())
        if user_id:
            q = q.filter(ConversationHistory.user_id == user_id)
        return q.limit(limit).all()

    def get_recent_messages(self, session_id: str, limit: int = 20,
                            user_id: int = None) -> List[ConversationHistory]:
        """获取最近 N 条消息"""
        q = self.db.query(ConversationHistory).filter(
            ConversationHistory.session_id == session_id
        ).order_by(ConversationHistory.id.desc())
        if user_id:
            q = q.filter(ConversationHistory.user_id == user_id)
        rows = q.limit(limit).all()
        return list(reversed(rows))

    # ===== 会话管理 =====

    def create_session(self, user_id: int, character: str = None,
                       memory_type: str = "chat",
                       title: str = "新对话") -> str:
        sid = f"{user_id}_{memory_type}_{uuid.uuid4().hex[:8]}"
        if character:
            sid = f"{user_id}_{memory_type}_{character}_{uuid.uuid4().hex[:8]}"
        return sid

    def list_sessions(self, user_id: int, memory_type: str = "chat",
                      character: str = None, limit: int = 30) -> List[Dict]:
        """列出用户会话摘要"""
        q = self.db.query(
            ConversationHistory.session_id,
            ConversationHistory.character,
            func.max(ConversationHistory.create_time).label("last_time"),
            func.count(ConversationHistory.id).label("msg_count"),
        ).filter(
            ConversationHistory.user_id == user_id,
            ConversationHistory.memory_type == memory_type,
        )
        if character:
            q = q.filter(ConversationHistory.character == character)

        q = q.group_by(
            ConversationHistory.session_id,
            ConversationHistory.character,
        ).order_by(desc("last_time")).limit(limit)

        results = []
        for sid, char, last_time, msg_count in q:
            # 取首条用户消息作为标题
            first = self.db.query(ConversationHistory.content).filter(
                ConversationHistory.session_id == sid,
                ConversationHistory.role == "user",
            ).order_by(ConversationHistory.id.asc()).first()
            title = (first.content[:30] + "...") if first and first.content else "新对话"
            results.append({
                "session_id": sid,
                "character": char,
                "title": title,
                "msg_count": msg_count,
                "last_time": last_time.isoformat() if last_time else "",
            })
        return results

    def delete_session(self, session_id: str, user_id: int = None) -> int:
        q = self.db.query(ConversationHistory).filter(
            ConversationHistory.session_id == session_id
        )
        if user_id:
            q = q.filter(ConversationHistory.user_id == user_id)
        count = q.delete(synchronize_session=False)
        self.db.commit()
        return count

    # ===== 查询历史（智能问数用） =====

    def get_query_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        rows = self.db.query(ConversationHistory).filter(
            ConversationHistory.user_id == user_id,
            ConversationHistory.memory_type == "query",
            ConversationHistory.role == "user",
        ).order_by(desc(ConversationHistory.id)).limit(limit).all()
        return [{
            "id": r.id, "question": r.content,
            "time": r.create_time.isoformat() if r.create_time else "",
        } for r in rows]

    def get_query_result(self, query_id: int) -> Optional[ConversationHistory]:
        """根据用户消息 ID 找到对应的 assistant 回复"""
        user_msg = self.db.query(ConversationHistory).filter(
            ConversationHistory.id == query_id
        ).first()
        if not user_msg:
            return None
        return self.db.query(ConversationHistory).filter(
            ConversationHistory.session_id == user_msg.session_id,
            ConversationHistory.role == "assistant",
            ConversationHistory.id > user_msg.id,
        ).order_by(ConversationHistory.id.asc()).first()