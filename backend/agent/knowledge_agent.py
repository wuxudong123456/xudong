from backend.agent.base_agent import BaseAgent
from backend.service.rag_service import RAGService


class KnowledgeAgent(BaseAgent):

    def __init__(self, db=None):
        super().__init__(db)
        self.rag_service = RAGService()

    @property
    def agent_name(self) -> str:
        return "RAGKnowledgeAgent"

    async def execute(self, message, character="bajie", history=None, user_id=None):
        result = await self.rag_service.answer_question(message)
        return result.get("answer", "一时答不上来..."), result
