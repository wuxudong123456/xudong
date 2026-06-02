"""
人物关系图谱服务
提供四大名著人物关系查询
"""
import logging
from typing import List, Dict, Optional
from backend.utils.neo4j_util import neo4j_client, RELATIONSHIP_TYPES

logger = logging.getLogger("graph_service")


class GraphService:
    """人物关系图谱服务"""

    def __init__(self):
        self.client = neo4j_client

    def is_ready(self) -> bool:
        """检查图谱服务是否可用"""
        return self.client.is_connected()

    def get_person_info(self, name: str) -> Optional[Dict]:
        """获取人物详细信息"""
        if not self.is_ready():
            return None
        return self.client.get_person(name)

    def get_person_relations(self, name: str) -> Dict:
        """
        获取人物关系网络
        :return: {person, relations: [...]}
        """
        if not self.is_ready():
            return {"person": name, "relations": [], "error": "Neo4j未连接"}

        person_info = self.client.get_person(name)
        if not person_info:
            return {"person": name, "relations": [], "error": "人物不存在"}

        relations = self.client.get_person_relations(name)

        # 格式化关系
        formatted_relations = []
        for rel in relations:
            formatted_relations.append({
                "target_name": rel["target_name"],
                "target_identity": rel["target_identity"],
                "relation_type": RELATIONSHIP_TYPES.get(rel["relation_type"], rel["relation_type"]),
                "relation_desc": rel["relation_desc"],
                "target_book": rel["target_book"],
            })

        return {
            "person": person_info,
            "relations": formatted_relations,
        }

    def find_relation_path(self, from_name: str, to_name: str) -> Dict:
        """
        查找两个人物之间的关系路径
        :return: {from, to, path: [...]}
        """
        if not self.is_ready():
            return {"from": from_name, "to": to_name, "path": [], "error": "Neo4j未连接"}

        paths = self.client.find_path(from_name, to_name)

        if not paths:
            return {"from": from_name, "to": to_name, "path": [], "error": "未找到路径"}

        # 格式化路径
        path_data = paths[0]
        node_names = path_data.get("node_names", [])
        relations = path_data.get("relations", [])

        path_steps = []
        for i in range(len(relations)):
            path_steps.append({
                "from": node_names[i],
                "to": node_names[i + 1],
                "relation": RELATIONSHIP_TYPES.get(relations[i]["type"], relations[i]["type"]),
                "description": relations[i].get("description", ""),
            })

        return {
            "from": from_name,
            "to": to_name,
            "path": path_steps,
        }

    def get_book_characters(self, book: str) -> List[Dict]:
        """获取某本名著的人物列表"""
        if not self.is_ready():
            return []

        characters = self.client.get_book_characters(book)
        return [{"name": c["name"], "identity": c["identity"]} for c in characters]

    def get_graph_visualization_data(self, book: str = None, center_name: str = None) -> Dict:
        """
        获取可视化图谱数据
        :return: ECharts可用的数据格式
        """
        if not self.is_ready():
            return {"nodes": [], "links": [], "categories": []}

        return self.client.get_graph_data(book=book, center_name=center_name)

    def search_person(self, keyword: str) -> List[Dict]:
        """模糊搜索人物"""
        if not self.is_ready():
            return []

        cypher = """
        MATCH (p:Person)
        WHERE p.name CONTAINS $keyword OR ANY(alias IN p.aliases WHERE alias CONTAINS $keyword)
        RETURN p.name as name, p.identity as identity, p.book as book
        LIMIT 20
        """
        results = self.client.execute_query(cypher, {"keyword": keyword})
        return [{"name": r["name"], "identity": r["identity"], "book": r["book"]} for r in results]

    def event_causal_chain(self, event_name):
        from backend.service.graph_reasoning import GraphReasoningService
        return GraphReasoningService().event_causal_chain(event_name)

    def faction_analysis(self, faction):
        from backend.service.graph_reasoning import GraphReasoningService
        return GraphReasoningService().faction_analysis(faction)

    def story_timeline(self, book):
        from backend.service.graph_reasoning import GraphReasoningService
        return GraphReasoningService().story_timeline(book)

    async def deep_query(self, question: str):
        from backend.service.graph_reasoning import GraphReasoningService
        return await GraphReasoningService().deep_query(question)
