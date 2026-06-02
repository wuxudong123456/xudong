"""轻量级 Agent 间通信总线"""
from threading import Lock


class AgentMessageBus:
    """共享上下文字典，支持并发读写"""

    def __init__(self):
        self.context = {}
        self._lock = Lock()

    def set(self, key: str, value):
        with self._lock:
            self.context[key] = value

    def get(self, key: str, default=None):
        with self._lock:
            return self.context.get(key, default)
