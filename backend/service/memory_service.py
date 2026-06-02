"""
通用记忆业务层
统一管理各模块的对话记忆：会话创建、消息存取、历史检索
"""
import logging
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from backend.dao.memory_dao import MemoryDAO

logger = logging.getLogger(__name__)


class MemoryService:
    """通用记忆服务"""

    def __init__(self, db: Session):
        self.db = db
        self.dao = MemoryDAO(db)

    # ===== 会话 =====

    def create_session(self, user_id: int, character: str = None,
                       memory_type: str = "chat") -> str:
        return self.dao.create_session(user_id, character, memory_type)

    def list_sessions(self, user_id: int, memory_type: str = "chat",
                      character: str = None) -> List[Dict]:
        return self.dao.list_sessions(user_id, memory_type, character)

    def delete_session(self, session_id: str, user_id: int) -> bool:
        return self.dao.delete_session(session_id, user_id) > 0

    # ===== 消息 =====

    def save_exchange(self, user_id: int, session_id: str,
                      user_msg: str, assistant_reply: str,
                      memory_type: str = "chat", character: str = None,
                      agent_type: str = None, extra_data: dict = None):
        """保存一对用户/助手消息"""
        self.dao.save_message(user_id, session_id, "user", user_msg,
                              memory_type, character, agent_type, extra_data)
        self.dao.save_message(user_id, session_id, "assistant", assistant_reply,
                              memory_type, character, agent_type, extra_data)
        self.dao.commit()

    def save_query(self, user_id: int, session_id: str,
                   question: str, answer: str,
                   sql: str = None, row_count: int = 0):
        """保存智能问数记录"""
        extra = {"sql": sql, "row_count": row_count} if sql else None
        self.save_exchange(user_id, session_id, question, answer,
                           memory_type="query", extra_data=extra)

    def save_game_record(self, user_id: int, game_type: str,
                         content: str, result: dict):
        """保存游戏记录"""
        sid = f"{user_id}_game_{game_type}"
        extra = result
        self.dao.save_message(user_id, sid, "user", content,
                              memory_type="game", extra_data=extra)

    # ===== 历史加载 =====

    def load_history(self, session_id: str, user_id: int = None,
                     limit: int = 50) -> List[dict]:
        """加载会话消息，转为前端可用格式"""
        rows = self.dao.get_session_messages(session_id, limit=limit, user_id=user_id)
        return [{"role": r.role, "content": r.content} for r in rows]

    def load_recent(self, session_id: str, limit: int = 20,
                    user_id: int = None) -> List[dict]:
        """加载最近 N 条"""
        rows = self.dao.get_recent_messages(session_id, limit=limit, user_id=user_id)
        return [{"role": r.role, "content": r.content} for r in rows]

    # ===== 查询历史 =====

    def get_query_history(self, user_id: int) -> List[Dict]:
        return self.dao.get_query_history(user_id)

    def get_query_detail(self, query_id: int) -> Optional[Dict]:
        return self.dao.get_query_result(query_id)