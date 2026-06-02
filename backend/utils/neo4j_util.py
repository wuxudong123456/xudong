"""
Neo4j 图数据库工具
管理四大名著人物关系图谱
支持懒加载（未安装neo4j驱动时不影响系统启动）
"""
import logging
from typing import List, Dict, Optional
from backend.config import settings

logger = logging.getLogger("neo4j")

# 关系类型中文映射
RELATIONSHIP_TYPES = {
    "SWORN_BROTHER": "结义兄弟",
    "SPOUSE": "夫妻",
    "FATHER_OF": "父子",
    "MOTHER_OF": "母子",
    "MASTER_OF": "主仆",
    "SUBORDINATE": "上下级",
    "ENEMY": "敌对",
    "FRIEND": "朋友",
    "SIBLING": "兄弟姐妹",
}


class Neo4jClient:
    """Neo4j图数据库客户端（懒加载）"""

    def __init__(self):
        self.driver = None
        self._neo4j_module = None
        self._connect()

    def _get_neo4j(self):
        """懒加载neo4j模块"""
        if self._neo4j_module is None:
            try:
                from neo4j import GraphDatabase, basic_auth
                self._neo4j_module = {"GraphDatabase": GraphDatabase, "basic_auth": basic_auth}
            except ImportError:
                logger.warning("neo4j驱动未安装，图谱功能不可用。请运行: pip install neo4j")
                return None
        return self._neo4j_module

    def _connect(self):
        """建立Neo4j连接"""
        neo4j_mod = self._get_neo4j()
        if not neo4j_mod:
            self.driver = None
            return

        try:
            self.driver = neo4j_mod["GraphDatabase"].driver(
                settings.NEO4J_URI,
                auth=neo4j_mod["basic_auth"](settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("Neo4j连接成功: %s", settings.NEO4J_URI)
        except Exception as e:
            logger.error("Neo4j连接失败: %s", e)
            self.driver = None

    def close(self):
        """关闭连接"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j连接已关闭")

    def is_connected(self) -> bool:
        """检查连接状态"""
        if not self.driver:
            return False
        try:
            with self.driver.session() as session:
                session.run("RETURN 1")
            return True
        except Exception:
            return False

    def execute_query(self, cypher: str, parameters: Dict = None) -> List[Dict]:
        """
        执行Cypher查询
        """
        if not self.driver:
            logger.error("Neo4j未连接")
            return []

        parameters = parameters or {}
        try:
            with self.driver.session() as session:
                result = session.run(cypher, parameters)
                records = []
                for record in result:
                    records.append(dict(record))
                return records
        except Exception as e:
            logger.error("Cypher查询失败: %s | %s", cypher, e)
            return []

    # ==================== 人物查询 ====================

    def get_person(self, name: str) -> Optional[Dict]:
        """查询单个人物信息"""
        cypher = """
        MATCH (p:Person {name: $name})
        RETURN p {
            .name, .book, .aliases, .identity, .description
        } as person
        """
        results = self.execute_query(cypher, {"name": name})
        return results[0]["person"] if results else None

    def get_person_relations(self, name: str) -> List[Dict]:
        """
        查询人物直接关系
        """
        cypher = """
        MATCH (p:Person {name: $name})-[r:RELATIONSHIP]-(target:Person)
        RETURN p.name as person, r.type as relation_type, r.description as relation_desc,
               target.name as target_name, target.identity as target_identity,
               target.book as target_book
        """
        return self.execute_query(cypher, {"name": name})

    def find_path(self, from_name: str, to_name: str, max_depth: int = 5) -> List[Dict]:
        """
        查找两个人物之间的关系路径
        """
        cypher = """
        MATCH path = shortestPath(
            (a:Person {name: $from_name})-[:RELATIONSHIP*1..""" + str(max_depth) + """]-(b:Person {name: $to_name})
        )
        RETURN [node in nodes(path) | node.name] as node_names,
               [rel in relationships(path) | {type: rel.type, description: rel.description}] as relations
        """
        return self.execute_query(cypher, {"from_name": from_name, "to_name": to_name})

    def get_book_characters(self, book: str) -> List[Dict]:
        """获取某本名著的所有人物"""
        cypher = """
        MATCH (p:Person {book: $book})
        RETURN p.name as name, p.identity as identity
        ORDER BY p.name
        """
        return self.execute_query(cypher, {"book": book})

    def get_graph_data(self, book: str = None, center_name: str = None) -> Dict:
        """
        获取ECharts可用的图谱数据
        """
        if center_name:
            # 以某人物为中心，查询其关系网络
            cypher = """
            MATCH (center:Person {name: $center_name})-[r:RELATIONSHIP]-(related:Person)
            RETURN center, related, r
            UNION
            MATCH (center:Person {name: $center_name})-[r1:RELATIONSHIP]-(mid:Person)-[r2:RELATIONSHIP]-(related:Person)
            WHERE related <> center
            RETURN center, related, r1 as r
            LIMIT 50
            """
            results = self.execute_query(cypher, {"center_name": center_name})
        elif book:
            cypher = """
            MATCH (p:Person {book: $book})-[r:RELATIONSHIP]-(target:Person {book: $book})
            RETURN p, target, r
            LIMIT 100
            """
            results = self.execute_query(cypher, {"book": book})
        else:
            cypher = """
            MATCH (p:Person)-[r:RELATIONSHIP]-(target:Person)
            RETURN p, target, r
            LIMIT 200
            """
            results = self.execute_query(cypher)

        nodes_map = {}
        links = []
        categories = [
            {"name": "西游记"},
            {"name": "三国演义"},
            {"name": "水浒传"},
            {"name": "红楼梦"},
        ]
        book_index = {"novel_xiyou": 0, "novel_sanguo": 1, "novel_shuihu": 2, "novel_honglou": 3}

        for record in results:
            for node_key in ["p", "center", "related"]:
                node = record.get(node_key)
                if node and hasattr(node, "get"):
                    node_id = node.get("name")
                    if node_id and node_id not in nodes_map:
                        nodes_map[node_id] = {
                            "id": node_id,
                            "name": node_id,
                            "value": node.get("identity", ""),
                            "category": book_index.get(node.get("book"), 0),
                        }

            rel = record.get("r")
            if rel:
                # 从record中推断source和target
                source = record.get("p") or record.get("center")
                target = record.get("target") or record.get("related")
                if source and target:
                    links.append({
                        "source": source.get("name"),
                        "target": target.get("name"),
                        "relation": RELATIONSHIP_TYPES.get(rel.get("type"), rel.get("type", "")),
                    })

        return {
            "nodes": list(nodes_map.values()),
            "links": links,
            "categories": categories,
        }


    # ===== 扩展：Event 节点 + 深度推理 =====

    def create_event_node(self, name: str, book: str, chapter: int,
                          description: str, event_type: str) -> bool:
        """创建 Event 节点: event_type = major_event / scene / battle"""
        try:
            if not self.driver:
                return False
            with self.driver.session() as session:
                session.run("""
                    MERGE (e:Event {name: $name})
                    SET e.book = $book, e.chapter = $chapter,
                        e.description = $description, e.event_type = $event_type
                """, name=name, book=book, chapter=chapter,
                    description=description, event_type=event_type)
            return True
        except Exception as e:
            logger.error("create_event_node failed: %s", e)
            return False

    def create_causal_relation(self, from_event: str, to_event: str,
                               description: str = "") -> bool:
        """创建 CAUSES 关系: Event A → Event B"""
        try:
            if not self.driver:
                return False
            with self.driver.session() as session:
                session.run("""
                    MATCH (a:Event {name: $from_event}), (b:Event {name: $to_event})
                    MERGE (a)-[r:CAUSES]->(b)
                    SET r.description = $description
                """, from_event=from_event, to_event=to_event, description=description)
            return True
        except Exception as e:
            logger.error("create_causal_relation failed: %s", e)
            return False

    def add_person_faction(self, name: str, faction: str) -> bool:
        """给 Person 添加 faction 属性（蜀/魏/吴/取经队伍/天庭/妖怪等）"""
        try:
            if not self.driver:
                return False
            with self.driver.session() as session:
                session.run("""
                    MATCH (p:Person {name: $name})
                    SET p.faction = $faction
                """, name=name, faction=faction)
            return True
        except Exception as e:
            logger.error("add_person_faction failed: %s", e)
            return False

    def add_person_chapter_relations(self, name: str, chapters: list) -> bool:
        """给 Person 添加 appears_in_chapter 属性"""
        try:
            if not self.driver:
                return False
            with self.driver.session() as session:
                session.run("""
                    MATCH (p:Person {name: $name})
                    SET p.appears_in_chapter = $chapters
                """, name=name, chapters=chapters)
            return True
        except Exception as e:
            logger.error("add_person_chapter_relations failed: %s", e)
            return False

    # ===== 深度查询 =====

    def query_event_chain(self, event_name: str) -> list:
        """查询事件因果链"""
        try:
            return self.execute_query("""
                MATCH path = (e:Event {name: $event_name})-[:CAUSES*1..5]->(end:Event)
                RETURN [node in nodes(path) | node.name] as chain,
                       [rel in relationships(path) | rel.description] as reasons
            """, {"event_name": event_name})
        except Exception as e:
            logger.error("query_event_chain failed: %s", e)
            return []

    def query_faction_members(self, faction: str) -> list:
        """查询阵营成员"""
        try:
            return self.execute_query("""
                MATCH (p:Person) WHERE p.faction = $faction
                RETURN p.name as name, p.identity as identity
            """, {"faction": faction})
        except Exception as e:
            logger.error("query_faction_members failed: %s", e)
            return []

    def query_story_timeline(self, book: str) -> list:
        """查询事件时间线"""
        try:
            return self.execute_query("""
                MATCH (e:Event) WHERE e.book = $book
                RETURN e.chapter as chapter, e.name as name,
                       e.description as description, e.event_type as type
                ORDER BY e.chapter
            """, {"book": book})
        except Exception as e:
            logger.error("query_story_timeline failed: %s", e)
            return []


# 全局单例
neo4j_client = Neo4jClient()
