# 四大名著RAG增强 + Neo4j人物关系图谱 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现智能书籍路由的跨集合RAG检索、Neo4j人物关系图谱查询、RAG+图谱融合查询、前端ECharts可视化

**Architecture:** 基于现有Milvus四集合架构，增加BookRouter智能路由层；新增Neo4j图数据库存储人物关系；通过GraphService提供图谱查询；RAGService集成智能路由和融合查询能力；前端使用ECharts展示关系网络。

**Tech Stack:** FastAPI, Neo4j (neo4j-python-driver), Milvus, ECharts, Vue3

---

## 文件变更总览

| 操作 | 文件 | 说明 |
|------|------|------|
| 新建 | `backend/utils/book_router.py` | 智能书籍路由 |
| 新建 | `backend/utils/neo4j_util.py` | Neo4j客户端封装 |
| 新建 | `backend/service/graph_service.py` | 人物关系图谱服务 |
| 新建 | `backend/controller/graph_controller.py` | 图谱API接口 |
| 新建 | `frontend/src/components/GraphView.vue` | 关系图谱可视化 |
| 新建 | `frontend/src/api/graph.js` | 图谱API封装 |
| 修改 | `backend/config.py` | 添加Neo4j配置 |
| 修改 | `backend/service/rag_service.py` | 集成智能路由和融合查询 |
| 修改 | `backend/utils/milvus_util.py` | 支持指定集合检索 |
| 修改 | `backend/main.py` | 注册图谱路由 |
| 修改 | `frontend/src/views/bajie/KnowledgeQA.vue` | 增加图谱展示 |

---

## Phase 1: 基础设施

### Task 1: Neo4j配置扩展

**Files:**
- 修改: `backend/config.py`

**Step 1: 在Settings类中添加Neo4j配置**

```python
# backend/config.py 中 Settings 类增加

    # Neo4j 图数据库配置
    NEO4J_URI: str = Field(default="bolt://localhost:7687", alias="NEO4J_URI")
    NEO4J_USER: str = Field(default="neo4j", alias="NEO4J_USER")
    NEO4J_PASSWORD: str = Field(default="password", alias="NEO4J_PASSWORD")
```

**Step 2: 验证配置加载**

启动Python解释器验证：
```python
from backend.config import settings
print(settings.NEO4J_URI)
```

---

### Task 2: Neo4j客户端封装

**Files:**
- 新建: `backend/utils/neo4j_util.py`

**Step 1: 实现Neo4j连接和查询封装**

```python
"""
Neo4j 图数据库工具
管理四大名著人物关系图谱
"""
import logging
from typing import List, Dict, Optional
from neo4j import GraphDatabase, basic_auth
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
    """Neo4j图数据库客户端"""

    def __init__(self):
        self.driver = None
        self._connect()

    def _connect(self):
        """建立Neo4j连接"""
        try:
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=basic_auth(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            # 验证连接
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
        :param cypher: Cypher语句
        :param parameters: 查询参数
        :return: 结果列表
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
        查询人物的所有关系
        :return: [{person, relation, target, relation_type}, ...]
        """
        cypher = """
        MATCH (p:Person {name: $name})-[r:RELATIONSHIP]-(target:Person)
        RETURN p.name as person, r.type as relation_type, r.description as relation_desc,
               target.name as target_name, target.identity as target_identity,
               target.book as target_book
        """
        return self.execute_query(cypher, {"name": name})

    def find_path(self, from_name: str, to_name: str, max_depth: int = 4) -> List[Dict]:
        """
        查找两个人物之间的关系路径
        :return: 路径上的节点和关系列表
        """
        cypher = """
        MATCH path = shortestPath(
            (a:Person {name: $from_name})-[:RELATIONSHIP*1..""" + str(max_depth) + """]-(b:Person {name: $to_name})
        )
        RETURN [node in nodes(path) | node.name] as node_names,
               [rel in relationships(path) | {type: rel.type, description: rel.description}] as relations
        """
        results = self.execute_query(cypher, {"from_name": from_name, "to_name": to_name})
        return results

    def get_book_characters(self, book: str, limit: int = 100) -> List[Dict]:
        """获取某本名著的所有人物"""
        cypher = """
        MATCH (p:Person {book: $book})
        RETURN p.name as name, p.identity as identity, p.aliases as aliases
        LIMIT $limit
        """
        return self.execute_query(cypher, {"book": book, "limit": limit})

    def get_graph_data(self, book: str = None, center_name: str = None, depth: int = 1) -> Dict:
        """
        获取ECharts可用的图谱数据
        :param book: 筛选名著
        :param center_name: 中心人物（可选）
        :param depth: 关系深度
        :return: {nodes: [...], links: [...], categories: [...]}
        """
        nodes_map = {}
        links = []
        categories = set()

        if center_name:
            # 以某人物为中心查询
            cypher = """
            MATCH (center:Person {name: $center_name})-[r:RELATIONSHIP]-(related:Person)
            RETURN center, related, r
            """
            results = self.execute_query(cypher, {"center_name": center_name})

            for record in results:
                center = record["center"]
                related = record["related"]
                rel = record["r"]

                # 添加节点
                for person in [center, related]:
                    name = person["name"]
                    if name not in nodes_map:
                        book_name = person.get("book", "unknown")
                        categories.add(book_name)
                        nodes_map[name] = {
                            "id": name,
                            "name": name,
                            "category": book_name,
                            "symbolSize": 50 if name == center_name else 30,
                            "value": person.get("identity", ""),
                            "draggable": True,
                        }

                # 添加关系
                links.append({
                    "source": center["name"],
                    "target": related["name"],
                    "relation": RELATIONSHIP_TYPES.get(rel["type"], rel["type"]),
                    "relationType": rel["type"],
                })
        else:
            # 查询整本书的人物关系
            book_filter = "WHERE p1.book = $book AND p2.book = $book" if book else ""
            cypher = f"""
            MATCH (p1:Person)-[r:RELATIONSHIP]-(p2:Person)
            {book_filter}
            RETURN p1, p2, r
            LIMIT 200
            """
            params = {"book": book} if book else {}
            results = self.execute_query(cypher, params)

            for record in results:
                p1 = record["p1"]
                p2 = record["p2"]
                rel = record["r"]

                for person in [p1, p2]:
                    name = person["name"]
                    if name not in nodes_map:
                        book_name = person.get("book", "unknown")
                        categories.add(book_name)
                        nodes_map[name] = {
                            "id": name,
                            "name": name,
                            "category": book_name,
                            "symbolSize": 30,
                            "value": person.get("identity", ""),
                            "draggable": True,
                        }

                links.append({
                    "source": p1["name"],
                    "target": p2["name"],
                    "relation": RELATIONSHIP_TYPES.get(rel["type"], rel["type"]),
                    "relationType": rel["type"],
                })

        return {
            "nodes": list(nodes_map.values()),
            "links": links,
            "categories": [{"name": c} for c in categories],
        }


# 全局单例
neo4j_client = Neo4jClient()
```

---

### Task 3: 智能书籍路由

**Files:**
- 新建: `backend/utils/book_router.py`

**Step 1: 实现书籍路由逻辑**

```python
"""
智能书籍路由
根据用户问题判断涉及哪本名著
策略: 关键词匹配 + LLM兜底
"""
import logging
from typing import List
from backend.utils.llm_router import chat_completion

logger = logging.getLogger("book_router")

# 关键词路由表
BOOK_KEYWORDS = {
    "novel_xiyou": [
        "孙悟空", "唐僧", "八戒", "沙僧", "如来", "观音", "取经", "大闹天宫",
        "花果山", "紧箍咒", "白骨精", "火焰山", "西天", "佛祖", "菩萨", "妖怪",
        "猴哥", "师傅", "老孙", "贫僧", "施主", "玄奘", "悟空", "悟能", "悟净",
    ],
    "novel_sanguo": [
        "刘备", "关羽", "张飞", "曹操", "诸葛亮", "孙权", "三国", "赤壁",
        "赵云", "马超", "黄忠", "魏延", "姜维", "吕布", "貂蝉", "董卓",
        "袁绍", "袁术", "刘表", "孙策", "周瑜", "鲁肃", "吕蒙", "陆逊",
        "桃园结义", "三顾茅庐", "草船借箭", "火烧赤壁", "过五关斩六将",
        "魏", "蜀", "吴", "蜀汉", "曹魏", "东吴",
    ],
    "novel_shuihu": [
        "宋江", "林冲", "武松", "李逵", "鲁智深", "梁山", "好汉", "招安",
        "吴用", "公孙胜", "关胜", "秦明", "呼延灼", "花荣", "柴进", "李应",
        "朱仝", "戴宗", "燕青", "史进", "李俊", "阮小二", "阮小五", "阮小七",
        "晁盖", "王伦", "一百单八将", "替天行道", "水泊梁山", "聚义厅",
    ],
    "novel_honglou": [
        "贾宝玉", "林黛玉", "薛宝钗", "王熙凤", "贾母", "大观园", "金陵十二钗",
        "贾政", "王夫人", "贾琏", "贾珍", "贾蓉", "贾蔷", "贾芸", "贾环",
        "史湘云", "妙玉", "贾元春", "贾迎春", "贾探春", "贾惜春",
        "袭人", "晴雯", "平儿", "鸳鸯", "紫鹃", "雪雁", "莺儿",
        "刘姥姥", "甄士隐", "冷子兴", "贾府", "荣国府", "宁国府",
        "石头记", "情僧录", "风月宝鉴",
    ],
}

# 跨书比较关键词
CROSS_BOOK_KEYWORDS = [
    "比较", "对比", "vs", "VS", "和", "与", "跟", "区别", "差异",
    "谁更", "哪个", "有什么不同", "有什么不一样",
]


def _keyword_route(question: str) -> List[str]:
    """关键词匹配路由"""
    matched = []
    for coll, keywords in BOOK_KEYWORDS.items():
        if any(kw in question for kw in keywords):
            matched.append(coll)
    return matched


def _is_cross_book_question(question: str) -> bool:
    """判断是否是跨书比较问题"""
    return any(kw in question for kw in CROSS_BOOK_KEYWORDS)


async def _llm_route_book(question: str) -> List[str]:
    """LLM判断涉及哪些书"""
    prompt = f"""分析用户问题涉及中国四大名著中的哪些。只返回JSON数组，如["novel_sanguo"]或["all"]。

四大名著:
- novel_xiyou: 《西游记》（孙悟空、唐僧、神仙妖怪、取经）
- novel_sanguo: 《三国演义》（刘备、曹操、诸葛亮、战争、三国）
- novel_shuihu: 《水浒传》（宋江、梁山好汉、招安）
- novel_honglou: 《红楼梦》（贾宝玉、林黛玉、贾府、爱情）

如果涉及多本书或无法确定，返回["all"]。

用户问题: {question}

返回格式: ["novel_xxx"] 或 ["all"]"""

    try:
        response = await chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=50,
        )
        import json
        result = json.loads(response.strip())
        if isinstance(result, list) and len(result) > 0:
            if "all" in result:
                return ["novel_xiyou", "novel_sanguo", "novel_shuihu", "novel_honglou"]
            return [r for r in result if r in BOOK_KEYWORDS]
    except Exception as e:
        logger.error("LLM路由失败: %s", e)

    # 兜底：返回全部
    return ["novel_xiyou", "novel_sanguo", "novel_shuihu", "novel_honglou"]


async def route_book(question: str) -> List[str]:
    """
    智能书籍路由
    :param question: 用户问题
    :return: 涉及的集合名列表
    """
    # 1. 检查是否是跨书比较问题
    if _is_cross_book_question(question):
        logger.info("[路由] 跨书问题，查询全部: %s", question)
        return ["novel_xiyou", "novel_sanguo", "novel_shuihu", "novel_honglou"]

    # 2. 关键词匹配
    matched = _keyword_route(question)

    # 3. 如果匹配到1本，直接返回
    if len(matched) == 1:
        logger.info("[路由] 关键词匹配: %s -> %s", question, matched[0])
        return matched

    # 4. 如果匹配到多本或没匹配到，用LLM判断
    logger.info("[路由] LLM判断: %s", question)
    return await _llm_route_book(question)
```

---

## Phase 2: 后端服务

### Task 4: 人物关系图谱服务

**Files:**
- 新建: `backend/service/graph_service.py`

**Step 1: 实现GraphService**

```python
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
```

---

### Task 5: RAG服务改造（智能路由 + 融合查询）

**Files:**
- 修改: `backend/service/rag_service.py`
- 修改: `backend/utils/milvus_util.py`

**Step 1: 在milvus_util.py中添加指定集合检索**

```python
# backend/utils/milvus_util.py 中添加

def search_specific_novels(query_vector: List[float], novel_names: List[str], top_k: int = 5) -> List[Dict]:
    """
    指定集合检索
    :param novel_names: 集合名列表，如 ["novel_sanguo", "novel_honglou"]
    """
    all_hits = []
    for coll_name in novel_names:
        if not utility.has_collection(coll_name):
            continue
        collection = Collection(coll_name)
        try:
            hits = search_similar(collection, query_vector, top_k=top_k)
            all_hits.extend(hits)
        except Exception as e:
            logger.error("检索 %s 失败: %s", coll_name, e)

    all_hits.sort(key=lambda x: x["score"], reverse=True)
    return all_hits
```

**Step 2: 改造RAGService**

```python
# backend/service/rag_service.py 改造

# 新增导入
from backend.utils.book_router import route_book
from backend.service.graph_service import GraphService

# RAG系统提示词更新
RAG_SYSTEM_PROMPT = """你是知识渊博的猪八戒，前世为天蓬元帅，对中国四大名著（《西游记》《三国演义》《红楼梦》《水浒传》）了如指掌。
请根据提供的原文片段和人物关系信息回答用户的问题。

要求：
1. 用猪八戒的口吻回答，自称"俺老猪"，语气憨厚诙谐
2. 回答要准确有据，基于提供的原文片段和人物关系
3. 如果检索到的信息来自多本名著，请综合回答并分别注明出处
4. 如果信息不足以回答问题，诚实告诉用户"这个俺老猪不太清楚"
5. 回答末尾注明引用的名著名称和章节出处
6. 回答控制在300-600字以内
"""

# 在RAGService类中添加新方法

    def __init__(self):
        self.graph_service = GraphService()

    async def answer_question_async(self, question: str,
                                    top_k: int = 5,
                                    history: List[Dict[str, str]] = None,
                                    mode: str = "auto") -> Dict:
        """
        增强版RAG问答
        :param mode: auto自动, rag仅原文, graph仅图谱, hybrid融合
        """
        # 判断查询模式
        if mode == "auto":
            mode = await self._detect_query_mode(question)

        if mode == "graph":
            return await self._graph_only_query(question)
        elif mode == "hybrid":
            return await self._hybrid_query(question, top_k, history)
        else:
            return await self._rag_only_query(question, top_k, history)

    async def _detect_query_mode(self, question: str) -> str:
        """自动检测查询模式"""
        # 关系类问题 → 图谱
        relation_keywords = ["关系", "谁", "什么关系", "认识", "朋友", "兄弟", "夫妻", "父子", "主仆"]
        if any(kw in question for kw in relation_keywords):
            # 检查是否同时涉及原文内容
            content_keywords = ["哪一回", "第几章", "原文", "怎么写", "描写"]
            if any(kw in question for kw in content_keywords):
                return "hybrid"
            return "graph"
        return "rag"

    async def _rag_only_query(self, question: str, top_k: int, history: List[Dict]) -> Dict:
        """纯RAG查询（带智能路由）"""
        # 智能路由：判断查哪本书
        target_books = await route_book(question)

        query_vector = await get_embedding(question)

        # 指定集合检索
        from backend.utils.milvus_util import search_specific_novels
        all_hits = search_specific_novels(query_vector, target_books, top_k=top_k)

        if not all_hits:
            return {
                "answer": "哼哼～俺老猪的知识库还没准备好呢！",
                "sources": [],
                "references": [],
                "mode": "rag",
            }

        # 构建上下文（原有逻辑）
        top_results = all_hits[:top_k * 2]
        novel_groups = {}
        references = []
        for hit in top_results:
            novel_cn = hit.get("novel_name_cn", "未知")
            if novel_cn not in novel_groups:
                novel_groups[novel_cn] = []
            novel_groups[novel_cn].append(
                f"【第{hit['chapter_num']}回：{hit['chapter_title']}】\n{hit['content']}"
            )
            references.append({...})  # 原有逻辑

        context = "\n\n".join([
            f"## 《{novel_cn}》原文参考：\n" + "\n\n---\n\n".join(parts)
            for novel_cn, parts in novel_groups.items()
        ])

        # 生成答案
        user_message = f"""请根据以下原文片段回答问题：

## 原文参考：
{context}

## 用户问题：
{question}

请用猪八戒口吻回答，并注明出处。"""

        messages = [{"role": "user", "content": user_message}]
        if history:
            messages = history[-6:] + messages

        answer = await chat_completion(
            messages=messages,
            system_prompt=RAG_SYSTEM_PROMPT,
            temperature=0.7,
            max_tokens=800,
        )

        return {
            "answer": answer,
            "sources": [ref["content"] for ref in references],
            "references": references,
            "mode": "rag",
            "target_books": target_books,
        }

    async def _graph_only_query(self, question: str) -> Dict:
        """纯图谱查询"""
        # 从问题中提取人物名（简化版：用关键词匹配）
        # 实际可用NER，这里先用关键词
        all_names = []
        for keywords in BOOK_KEYWORDS.values():
            all_names.extend(keywords)

        found_names = [name for name in all_names if name in question]

        if len(found_names) >= 2:
            # 查关系路径
            result = self.graph_service.find_relation_path(found_names[0], found_names[1])
            context = f"人物关系：{found_names[0]} 和 {found_names[1]}\n"
            if result.get("path"):
                path_str = " → ".join([
                    f"{step['from']}({step['relation']})"
                    for step in result["path"]
                ]) + f" → {found_names[1]}"
                context += f"关系路径：{path_str}\n"
            else:
                context += "两人没有直接关系记录。\n"
        elif len(found_names) == 1:
            # 查人物关系网络
            result = self.graph_service.get_person_relations(found_names[0])
            context = f"{found_names[0]}的关系网络：\n"
            for rel in result.get("relations", [])[:10]:
                context += f"- {rel['relation_type']}：{rel['target_name']}（{rel['target_identity']}）\n"
        else:
            context = "未识别到具体人物。"

        # 用LLM生成回复
        prompt = f"""你是猪八戒，正在回答关于四大名著人物关系的问题。

## 人物关系信息：
{context}

## 用户问题：
{question}

请用猪八戒口吻回答，语气憨厚。"""

        answer = await chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500,
        )

        return {
            "answer": answer,
            "sources": [context],
            "references": [],
            "mode": "graph",
        }

    async def _hybrid_query(self, question: str, top_k: int, history: List[Dict]) -> Dict:
        """融合查询：RAG + 图谱并行"""
        import asyncio

        # 并行执行
        rag_task = self._rag_only_query(question, top_k, history)
        graph_task = self._graph_only_query(question)

        rag_result, graph_result = await asyncio.gather(rag_task, graph_task)

        # 合并上下文
        combined_context = f"""## 原文信息
{rag_result['answer']}

## 人物关系信息
{graph_result['answer']}"""

        # 生成综合回复
        prompt = f"""你是猪八戒，综合以下信息回答用户问题。

## 原文参考：
{rag_result['answer']}

## 人物关系：
{graph_result['answer']}

## 用户问题：
{question}

请用猪八戒口吻，综合原文和人物关系给出一个完整的回答。"""

        answer = await chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800,
        )

        return {
            "answer": answer,
            "sources": rag_result.get("sources", []) + graph_result.get("sources", []),
            "references": rag_result.get("references", []),
            "mode": "hybrid",
        }
```

---

### Task 6: 图谱API控制器

**Files:**
- 新建: `backend/controller/graph_controller.py`

**Step 1: 实现GraphController**

```python
"""
人物关系图谱API控制器
提供人物关系查询、图谱可视化数据
"""
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from backend.service.graph_service import GraphService
from backend.utils.logger import get_logger

router = APIRouter()
logger = get_logger("graph_controller")


@router.get("/person/{name}", summary="查询人物信息")
async def get_person_info(name: str):
    """获取人物详细信息和关系网络"""
    service = GraphService()
    if not service.is_ready():
        return {"code": 503, "message": "图谱服务未就绪", "data": None}

    result = service.get_person_relations(name)
    if result.get("error"):
        return {"code": 404, "message": result["error"], "data": None}

    return {"code": 200, "message": "success", "data": result}


@router.get("/path", summary="查询人物关系路径")
async def find_relation_path(
    from_name: str = Query(..., description="起始人物"),
    to_name: str = Query(..., description="目标人物"),
):
    """查找两个人物之间的关系路径"""
    service = GraphService()
    if not service.is_ready():
        return {"code": 503, "message": "图谱服务未就绪", "data": None}

    result = service.find_relation_path(from_name, to_name)
    return {"code": 200, "message": "success", "data": result}


@router.get("/book/{book_name}", summary="获取名著人物列表")
async def get_book_characters(book_name: str):
    """获取某本名著的所有人物"""
    service = GraphService()
    if not service.is_ready():
        return {"code": 503, "message": "图谱服务未就绪", "data": None}

    characters = service.get_book_characters(book_name)
    return {"code": 200, "message": "success", "data": characters}


@router.get("/visualization", summary="获取图谱可视化数据")
async def get_graph_visualization(
    book: Optional[str] = Query(None, description="筛选名著，如 novel_sanguo"),
    center: Optional[str] = Query(None, description="中心人物"),
):
    """获取ECharts可用的图谱数据"""
    service = GraphService()
    if not service.is_ready():
        return {"code": 503, "message": "图谱服务未就绪", "data": None}

    data = service.get_graph_visualization_data(book=book, center_name=center)
    return {"code": 200, "message": "success", "data": data}


@router.get("/search", summary="搜索人物")
async def search_person(keyword: str = Query(..., description="搜索关键词")):
    """模糊搜索人物"""
    service = GraphService()
    if not service.is_ready():
        return {"code": 503, "message": "图谱服务未就绪", "data": None}

    results = service.search_person(keyword)
    return {"code": 200, "message": "success", "data": results}
```

---

## Phase 3: 前端实现

### Task 7: 图谱API封装

**Files:**
- 新建: `frontend/src/api/graph.js`

**Step 1: 实现Graph API**

```javascript
/**
 * 人物关系图谱API封装
 */
import request from './request'

/**
 * 查询人物信息
 * @param {string} name - 人物姓名
 */
export function getPersonInfo(name) {
  return request.get(`/graph/person/${encodeURIComponent(name)}`)
}

/**
 * 查询人物关系路径
 * @param {string} fromName - 起始人物
 * @param {string} toName - 目标人物
 */
export function findRelationPath(fromName, toName) {
  return request.get('/graph/path', {
    params: { from_name: fromName, to_name: toName }
  })
}

/**
 * 获取名著人物列表
 * @param {string} bookName - 名著标识
 */
export function getBookCharacters(bookName) {
  return request.get(`/graph/book/${bookName}`)
}

/**
 * 获取图谱可视化数据
 * @param {Object} params - {book, center}
 */
export function getGraphVisualization(params = {}) {
  return request.get('/graph/visualization', { params })
}

/**
 * 搜索人物
 * @param {string} keyword - 搜索关键词
 */
export function searchPerson(keyword) {
  return request.get('/graph/search', { params: { keyword } })
}
```

---

### Task 8: 图谱可视化组件

**Files:**
- 新建: `frontend/src/components/GraphView.vue`

**Step 1: 实现GraphView组件**

```vue
<template>
  <div class="graph-container">
    <div ref="chartRef" class="graph-chart"></div>
    <div v-if="selectedNode" class="node-info">
      <h4>{{ selectedNode.name }}</h4>
      <p>{{ selectedNode.value }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: {
    type: Object,
    default: () => ({ nodes: [], links: [], categories: [] })
  }
})

const chartRef = ref(null)
const selectedNode = ref(null)
let chart = null

const initChart = () => {
  if (!chartRef.value) return

  chart = echarts.init(chartRef.value)

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        if (params.dataType === 'node') {
          return `${params.data.name}<br/>${params.data.value || ''}`
        }
        return `${params.data.relation}`
      }
    },
    legend: {
      data: props.data.categories.map(c => c.name),
      top: 10,
      left: 10
    },
    series: [
      {
        type: 'graph',
        layout: 'force',
        data: props.data.nodes,
        links: props.data.links,
        categories: props.data.categories,
        roam: true,
        label: {
          show: true,
          position: 'right',
          formatter: '{b}'
        },
        force: {
          repulsion: 300,
          edgeLength: 100,
          gravity: 0.1
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: 4
          }
        },
        lineStyle: {
          color: 'source',
          curveness: 0.3
        },
        edgeLabel: {
          show: true,
          formatter: (x) => x.data.relation,
          fontSize: 10
        }
      }
    ]
  }

  chart.setOption(option)

  // 点击事件
  chart.on('click', (params) => {
    if (params.dataType === 'node') {
      selectedNode.value = params.data
    }
  })
}

const handleResize = () => {
  chart?.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
})

watch(() => props.data, () => {
  if (chart) {
    chart.dispose()
    initChart()
  }
}, { deep: true })
</script>

<style scoped>
.graph-container {
  width: 100%;
  height: 600px;
  position: relative;
}

.graph-chart {
  width: 100%;
  height: 100%;
}

.node-info {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(255, 255, 255, 0.9);
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  max-width: 250px;
}

.node-info h4 {
  margin: 0 0 8px 0;
  color: #333;
}

.node-info p {
  margin: 0;
  color: #666;
  font-size: 14px;
}
</style>
```

---

### Task 9: 改造KnowledgeQA页面

**Files:**
- 修改: `frontend/src/views/bajie/KnowledgeQA.vue`

**Step 1: 集成图谱展示和模式切换**

在页面中添加：
1. 查询模式选择器（RAG / 图谱 / 融合 / 自动）
2. 人物关系图谱展示区域
3. 人物搜索功能

---

## Phase 4: 注册路由

### Task 10: 注册图谱路由

**Files:**
- 修改: `backend/main.py`

**Step 1: 在main.py中添加图谱路由**

```python
# backend/main.py 路由注册区域添加

# 人物关系图谱
from backend.controller.graph_controller import router as graph_router
app.include_router(graph_router, prefix="/api/v1/graph", tags=["人物关系图谱"])
```

---

## 依赖安装

```bash
# 后端依赖
pip install neo4j-python-driver

# 前端依赖（ECharts）
cd frontend
npm install echarts
```

---

## 测试验证清单

- [ ] Neo4j连接成功
- [ ] 智能路由："孙悟空" → novel_xiyou
- [ ] 智能路由："刘备" → novel_sanguo
- [ ] 智能路由："比较刘备和宋江" → 全部
- [ ] 图谱查询：GET /api/v1/graph/person/刘备
- [ ] 路径查询：GET /api/v1/graph/path?from=刘备&to=关羽
- [ ] 可视化数据：GET /api/v1/graph/visualization?book=novel_sanguo
- [ ] 融合查询："曹操为什么败走华容道" → 同时返回原文+关系
- [ ] 前端图谱正常展示
- [ ] 点击节点显示详情
