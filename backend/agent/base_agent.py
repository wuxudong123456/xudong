from abc import ABC, abstractmethod
from typing import Tuple, Any, Optional, List
from sqlalchemy.orm import Session


class BaseAgent(ABC):
    """智能体基类"""

    def __init__(self, db: Session = None):
        self.db = db
        self.tools: List[dict] = []
        self.tool_registry: dict = {}

    @abstractmethod
    async def execute(self, message: str, character: str = "bajie",
                      history: list = None, user_id: int = None) -> Tuple[str, Any]:
        """执行Agent任务，返回 (reply, data)"""
        pass

    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Agent名称"""
        pass
