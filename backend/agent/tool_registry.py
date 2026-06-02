"""
工具注册表 — 单例，统一管理所有可调用工具
"""
import logging
from typing import Dict, List, Any, Callable

logger = logging.getLogger(__name__)


class ToolRegistry:
    """单例工具注册表"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools: Dict[str, dict] = {}
            cls._instance._init_defaults()
        return cls._instance

    def _init_defaults(self):
        self.register("nl2sql", _tool_nl2sql,
                      description="查询业务数据库（学生/成绩/班级/课程/就业等），返回表格数据",
                      params={"query": "string"})
        self.register("rag_search", _tool_rag,
                      description="检索四大名著知识库（西游记/三国/水浒/红楼），返回原文相关内容",
                      params={"question": "string"})
        self.register("graph_query", _tool_graph,
                      description="查询人物关系图谱，返回该人物的关系网络",
                      params={"name": "string"})
        self.register("calculate", _tool_calculate,
                      description="数学计算，支持加减乘除幂运算等",
                      params={"expression": "string"})
        self.register("get_weather", _tool_weather,
                      description="查询指定城市的实时天气",
                      params={"city": "string"})
        self.register("get_fortune", _tool_fortune,
                      description="运势占卜，返回今日综合运势",
                      params={})

    def register(self, name: str, func: Callable, description: str, params: dict):
        self._tools[name] = {"name": name, "func": func, "description": description, "params": params}

    def get_all_tools(self) -> List[dict]:
        return [{"name": t["name"], "description": t["description"], "params": t["params"]}
                for t in self._tools.values()]

    async def execute(self, name: str, params: dict) -> str:
        tool = self._tools.get(name)
        if not tool:
            return f"未知工具: {name}"
        try:
            result = tool["func"](**params)
            if hasattr(result, "__await__"):
                result = await result
            return str(result)[:1000]
        except Exception as e:
            logger.warning("Tool %s failed: %s", name, e)
            return f"工具 {name} 执行失败: {e}"


# ===== 工具实现 =====

async def _tool_nl2sql(query: str) -> str:
    from backend.database import SessionLocal
    from backend.service.nl2sql_service import nl2sql_query
    db = SessionLocal()
    try:
        result = await nl2sql_query(db, query)
        rows = (result.get("result") or {}).get("rows", [])
        return str(rows[:10]) if rows else (result.get("error") or "无结果")
    finally:
        db.close()


async def _tool_rag(question: str) -> str:
    from backend.service.rag_service import RAGService
    result = await RAGService().answer_question_async(question)
    return result.get("answer", "无结果")[:500]


async def _tool_graph(name: str) -> str:
    from backend.service.graph_service import GraphService
    result = GraphService().get_person_relations(name.strip())
    relations = result.get("relations", [])[:5]
    return "; ".join([f"{r['relation_type']}:{r['target_name']}" for r in relations]) if relations else f"未找到 {name} 的关系"


async def _tool_calculate(expression: str) -> str:
    import ast
    import operator
    allowed = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
               ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg}
    try:
        tree = ast.parse(expression, mode="eval")
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and type(node.op) not in allowed:
                return "不支持的运算"
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"计算失败: {e}"


async def _tool_weather(city: str) -> str:
    from backend.utils.weather_util import get_weather_by_city, format_weather_for_prompt
    data = await get_weather_by_city(city)
    return format_weather_for_prompt(data) if data else f"未找到 {city} 的天气"


async def _tool_fortune() -> str:
    from backend.service.fortune_service import FortuneService
    fortune = await FortuneService().generate_fortune()
    if not fortune:
        return "运势数据不可用"
    return f"综合{fortune.get('overall_score','?')}分 {fortune.get('overall_text','')} | 爱情{fortune.get('love_score','?')}分 | 事业{fortune.get('career_score','?')}分 | 财运{fortune.get('wealth_score','?')}分"
