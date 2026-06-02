"""
图谱深度推理服务 — 因果链 / 阵营分析 / 事件时间线 / LLM 深度问答
"""
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class GraphReasoningService:
    """Neo4j 深度推理"""

    def __init__(self):
        from backend.utils.neo4j_util import neo4j_client
        self.client = neo4j_client

    def _is_ready(self) -> bool:
        return self.client.is_connected()

    def event_causal_chain(self, event_name: str) -> dict:
        """事件因果链查询 + LLM 解释"""
        if not self._is_ready():
            return {"error": "Neo4j 未连接"}

        try:
            rows = self.client.query_event_chain(event_name)
            if not rows or not rows[0].get("chain"):
                return {"event": event_name, "chain": [], "reasons": [],
                        "explanation": f"未找到 {event_name} 的因果链"}

            chain = rows[0]["chain"]
            reasons = rows[0].get("reasons", [])

            # LLM 解释
            chain_text = " → ".join(chain)
            reason_text = ", ".join([r for r in reasons if r])
            prompt = f"""事件因果链: {chain_text}
原因说明: {reason_text}
请用一段话解释这个事件因果链，像在讲故事一样。"""
            try:
                from backend.utils.deepseek_util import chat_completion
                import asyncio
                expl = asyncio.get_event_loop().run_until_complete(
                    chat_completion(messages=[{"role": "user", "content": prompt}],
                                    temperature=0.7, max_tokens=300))
            except Exception:
                expl = f"事件 {event_name} 的因果链: {chain_text}"

            return {"event": event_name, "chain": chain, "reasons": reasons,
                    "explanation": expl.strip()}
        except Exception as e:
            logger.error("event_causal_chain failed: %s", e)
            return {"error": str(e)}

    def faction_analysis(self, faction: str) -> dict:
        """阵营分析"""
        if not self._is_ready():
            return {"error": "Neo4j 未连接"}

        try:
            members = self.client.query_faction_members(faction)
            return {"faction": faction,
                    "members": [{"name": m["name"], "identity": m.get("identity", "")}
                                for m in members],
                    "count": len(members)}
        except Exception as e:
            logger.error("faction_analysis failed: %s", e)
            return {"error": str(e)}

    def story_timeline(self, book: str) -> dict:
        """事件时间线"""
        if not self._is_ready():
            return {"error": "Neo4j 未连接"}

        try:
            events = self.client.query_story_timeline(book)
            return {"book": book, "events": [
                {"chapter": e["chapter"], "name": e["name"],
                 "description": e.get("description", ""),
                 "type": e.get("type", "")}
                for e in events
            ]}
        except Exception as e:
            logger.error("story_timeline failed: %s", e)
            return {"error": str(e)}

    async def deep_query(self, question: str) -> dict:
        """LLM 解析深度问题 → 自动调度方法"""
        if not self._is_ready():
            return {"error": "Neo4j 未连接"}

        prompt = f"""分析以下关于四大名著的问题，返回JSON指定查询类型：
问题: {question}
返回格式: {{"type": "causal"|"faction"|"timeline"|"relation", "target": "目标名称"}}

规则:
- "为什么" / "原因" / "导致" → type=causal, target=事件名
- "阵营" / "势力" / "派系" → type=faction, target=阵营名
- "时间线" / "顺序" / "大事" → type=timeline, target=书名(novel_xiyou/novel_sanguo/novel_honglou/novel_shuihu)
- "关系" / "认识" / "谁" → type=relation, target=人名
只返回JSON。"""

        try:
            import json as _json
            from backend.utils.deepseek_util import chat_completion

            resp = await chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2, max_tokens=150,
            )
            s = resp.find("{")
            e = resp.rfind("}") + 1
            parsed = _json.loads(resp[s:e]) if s >= 0 and e > s else {}
            qtype = parsed.get("type", "")
            target = parsed.get("target", "")

            if qtype == "causal":
                return self.event_causal_chain(target)
            elif qtype == "faction":
                return self.faction_analysis(target)
            elif qtype == "timeline":
                return self.story_timeline(target)
            elif qtype == "relation":
                from backend.service.graph_service import GraphService
                return {"relations": GraphService().find_relation_path(target, target)}
            return {"answer": "请尝试更具体的问题", "detected_type": qtype}
        except Exception as e:
            logger.error("deep_query failed: %s", e)
            return {"answer": "请尝试更具体的问题"}
