# 四大名著RAG增强 + Neo4j人物关系图谱 设计文档

> **项目**: 学生管理系统 + 猪八戒多智能体AI问答
> **日期**: 2026-05-27
> **目标**: 实现智能书籍路由的跨集合RAG检索、Neo4j人物关系图谱、RAG+图谱融合查询、前端可视化

---

## 一、需求确认

基于用户选择：
- **RAG路由策略**: C（两者结合）— 先智能判断书籍，跨书问题再查全部
- **Neo4j数据**: C（先架构后数据）— 先实现图谱架构和查询接口，数据后续补充
- **图谱可视化**: A（需要前端可视化）— 使用ECharts展示人物关系图
- **RAG+图谱融合**: B（直接做融合）— 混合查询同时利用原文检索和人物关系

---

## 二、架构设计

### 2.1 整体架构

```
用户问题
    ↓
[意图判断层] —— 问题类型: 事实型 / 关系型 / 混合型
    ↓
    ├─ 事实型 → [智能书籍路由] → [Milvus RAG检索] → [LLM生成回复]
    ├─ 关系型 → [Neo4j图谱查询] → [LLM生成回复]
    └─ 混合型 → [RAG + 图谱并行查询] → [合并上下文] → [LLM生成回复]
```

### 2.2 组件划分

| 组件 | 职责 | 文件 |
|------|------|------|
| BookRouter | 根据问题判断涉及哪本名著 | `backend/utils/book_router.py` |
| Neo4jClient | 连接Neo4j，执行Cypher查询 | `backend/utils/neo4j_util.py` |
| GraphService | 人物关系查询服务 | `backend/service/graph_service.py` |
| GraphController | 图谱API接口 | `backend/controller/graph_controller.py` |
| RAGService(改造) | 支持智能路由和融合查询 | `backend/service/rag_service.py` |
| GraphVisualization | 前端关系图谱组件 | `frontend/src/components/GraphView.vue` |

---

## 三、详细设计

### 3.1 智能书籍路由 (BookRouter)

**策略**: 关键词匹配 + LLM兜底

```python
# 关键词路由表
BOOK_KEYWORDS = {
    "novel_xiyou": ["孙悟空", "唐僧", "八戒", "沙僧", "如来", "观音", "取经", "大闹天宫"],
    "novel_sanguo": ["刘备", "关羽", "张飞", "曹操", "诸葛亮", "孙权", "三国", "赤壁"],
    "novel_shuihu": ["宋江", "林冲", "武松", "李逵", "鲁智深", "梁山", "好汉", "招安"],
    "novel_honglou": ["贾宝玉", "林黛玉", "薛宝钗", "王熙凤", "贾母", "大观园", "金陵十二钗"],
}

async def route_book(question: str) -> List[str]:
    """
    判断问题涉及哪些名著
    返回: ["novel_xiyou", "novel_sanguo"] 或 ["all"]
    """
    # 1. 关键词匹配
    matched = []
    for coll, keywords in BOOK_KEYWORDS.items():
        if any(kw in question for kw in keywords):
            matched.append(coll)
    
    # 2. 如果匹配到2本以上，或没匹配到，用LLM判断
    if len(matched) >= 2 or not matched:
        return await _llm_route_book(question)
    
    return matched
```

**LLM路由提示词**:
```
分析用户问题涉及中国四大名著中的哪些。只返回JSON数组，如["novel_sanguo"]或["all"]。

四大名著:
- novel_xiyou: 《西游记》（孙悟空、唐僧、神仙妖怪）
- novel_sanguo: 《三国演义》（刘备、曹操、诸葛亮、战争）
- novel_shuihu: 《水浒传》（宋江、梁山好汉、招安）
- novel_honglou: 《红楼梦》（贾宝玉、林黛玉、贾府、爱情）

如果涉及多本书或无法确定，返回["all"]。

用户问题: {question}
```

### 3.2 Neo4j人物关系图谱

**数据模型**:

```cypher
// 人物节点
(:Person {
    name: "刘备",           // 姓名
    book: "novel_sanguo",   // 所属名著
    aliases: ["玄德", "刘皇叔"],  // 别名
    identity: "蜀汉开国皇帝",      // 身份
    description: "..."      // 简介
})

// 关系边
(:Person)-[:RELATIONSHIP {
    type: "SWORN_BROTHER",  // 关系类型
    description: "桃园结义", // 关系描述
    book: "novel_sanguo"    // 所属名著
}]->(:Person)

// 关系类型枚举
SWORN_BROTHER  // 结义兄弟
SPOUSE         // 夫妻
FATHER_OF      // 父子
MOTHER_OF      // 母子
MASTER_OF      // 主仆
SUBORDINATE    // 上下级
ENEMY          // 敌对
FRIEND         // 朋友
SIBLING        // 兄弟姐妹
```

**核心查询**:
```cypher
// 查询某人的直接关系
MATCH (p:Person {name: $name})-[r]-(related)
RETURN p, r, related

// 查询两人之间的路径
MATCH path = shortestPath(
    (a:Person {name: $name1})-[:RELATIONSHIP*1..4]-(b:Person {name: $name2})
)
RETURN path

// 查询某人的所有下属
MATCH (p:Person {name: $name})-[:MASTER_OF|SUBORDINATE]->(sub)
RETURN sub

// 按名著查询所有人物
MATCH (p:Person {book: $book})
RETURN p
```

### 3.3 RAG + 图谱融合查询

**融合策略**:

```python
async def hybrid_query(question: str) -> Dict:
    """
    混合查询：同时执行RAG检索和图谱查询
    """
    # 并行执行
    rag_task = rag_search(question)
    graph_task = graph_query(question)
    
    rag_results, graph_results = await asyncio.gather(rag_task, graph_task)
    
    # 合并上下文
    context = {
        "rag": rag_results,      # 原文片段
        "graph": graph_results,   # 人物关系
    }
    
    # 生成回复
    return await generate_hybrid_answer(question, context)
```

**融合提示词**:
```
请根据以下信息回答用户问题：

## 原文参考
{rag_context}

## 人物关系
{graph_context}

## 用户问题
{question}

要求：
1. 综合原文和人物关系回答
2. 用猪八戒口吻，自称"俺老猪"
3. 注明信息来源（原文/图谱）
```

### 3.4 前端可视化 (ECharts)

**GraphView组件**:
```vue
<template>
  <div ref="chartRef" class="graph-chart"></div>
</template>

<script setup>
// 使用ECharts Graph类型
// 节点: 人物（大小根据关系数量）
// 边: 关系（颜色根据关系类型）
// 交互: 点击节点显示详情，拖拽缩放
</script>
```

**数据格式**:
```json
{
  "nodes": [
    {"id": "刘备", "name": "刘备", "category": 0, "symbolSize": 50},
    {"id": "关羽", "name": "关羽", "category": 0, "symbolSize": 45}
  ],
  "links": [
    {"source": "刘备", "target": "关羽", "relation": "SWORN_BROTHER"}
  ],
  "categories": [
    {"name": "蜀汉"},
    {"name": "曹魏"},
    {"name": "东吴"}
  ]
}
```

---

## 四、文件变更清单

### 新建文件
| 文件 | 说明 |
|------|------|
| `backend/utils/book_router.py` | 智能书籍路由 |
| `backend/utils/neo4j_util.py` | Neo4j连接和查询封装 |
| `backend/service/graph_service.py` | 人物关系图谱服务 |
| `backend/controller/graph_controller.py` | 图谱API接口 |
| `frontend/src/components/GraphView.vue` | 关系图谱可视化组件 |
| `frontend/src/api/graph.js` | 图谱API封装 |

### 修改文件
| 文件 | 修改内容 |
|------|----------|
| `backend/config.py` | 添加Neo4j配置 |
| `backend/service/rag_service.py` | 集成智能路由和融合查询 |
| `backend/utils/milvus_util.py` | 支持指定集合检索 |
| `backend/main.py` | 注册图谱路由 |
| `frontend/src/views/bajie/KnowledgeQA.vue` | 增加图谱展示和融合查询 |

---

## 五、API设计

### 5.1 图谱查询接口

```
GET /api/v1/graph/person/{name}
返回某人物的关系网络

GET /api/v1/graph/path?from=刘备&to=关羽
返回两人之间的关系路径

GET /api/v1/graph/book/{book_name}
返回某名著的所有人物关系

POST /api/v1/graph/query
通用Cypher查询（受限）
```

### 5.2 RAG增强接口

```
POST /api/v1/rag/query
Body: {question, history, mode: "auto|rag|graph|hybrid"}
mode参数: auto自动选择, rag仅原文, graph仅图谱, hybrid融合
```

---

## 六、实施计划概要

### Phase 1: 基础设施（1天）
- 添加Neo4j配置
- 封装Neo4j客户端
- 实现BookRouter

### Phase 2: 后端服务（2天）
- 实现GraphService
- 改造RAGService（智能路由+融合）
- 实现GraphController

### Phase 3: 前端可视化（2天）
- 封装图谱API
- 实现GraphView组件
- 改造KnowledgeQA页面

### Phase 4: 数据导入（后续）
- 用LLM抽取人物关系
- 导入Neo4j
- 验证查询

---

## 七、风险与应对

| 风险 | 应对 |
|------|------|
| Neo4j未安装 | 提供Docker启动命令 |
| 人物关系数据缺失 | 先实现架构，用模拟数据演示 |
| 融合查询延迟高 | RAG和图谱查询并行执行 |
| ECharts性能问题 | 限制节点数量，启用懒加载 |

---

## 八、验收标准

- [ ] 问"孙悟空是谁" → 只查西游记集合
- [ ] 问"诸葛亮和周瑜" → 只查三国演义集合
- [ ] 问"比较刘备和宋江" → 查三国+水浒，融合回答
- [ ] 问"刘备和关羽什么关系" → 返回图谱关系+原文佐证
- [ ] 前端能展示人物关系网络图
- [ ] 点击节点可查看人物详情
