"""
RAG 知识问答服务
基于四大名著（西游记/三国演义/红楼梦/水浒传）Milvus向量库的检索增强生成问答
流程: 用户问题 → Embedding → Milvus跨集合检索Top-K → 拼接上下文 → DeepSeek生成答案
支持多集合联合检索，按向量相似度精准匹配完整语义内容
支持智能书籍路由、图谱查询、融合查询
"""
import asyncio
from typing import List, Dict, Optional
from backend.utils.embedding_util import get_embedding
from backend.utils.milvus_util import search_all_novels, search_specific_novels, get_all_collections
from backend.utils.deepseek_util import chat_completion, chat_completion_stream
from backend.utils.book_router import route_book, BOOK_KEYWORDS
from backend.service.graph_service import GraphService

# RAG系统提示词 - 基于四大名著原文的知识问答
RAG_SYSTEM_PROMPT = """你是知识渊博的猪八戒，前世为天蓬元帅，对中国四大名著（《西游记》《三国演义》《红楼梦》《水浒传》）了如指掌。
请根据提供的原文片段和人物关系信息回答用户的问题。

要求：
1. 用猪八戒的口吻回答，自称"俺老猪"，语气憨厚诙谐，偶尔加入"嘿嘿"、"哼哼"
2. 回答要准确有据，基于提供的原文片段和人物关系，不要编造原文中没有的信息
3. 如果检索到的信息来自多本名著，请综合回答并分别注明出处
4. 如果信息不足以回答问题，诚实告诉用户"这个俺老猪不太清楚，书里没细说"
5. 回答末尾注明引用的名著名称和章节出处
6. 回答控制在300-600字以内，简洁明了
"""


class RAGService:
    """四大名著RAG知识问答服务，支持智能路由、跨集合联合检索、图谱融合查询"""

    def __init__(self):
        self.graph_service = GraphService()

    @staticmethod
    def _ensure_milvus():
        """确保 Milvus 连接存活"""
        try:
            from pymilvus import connections
            if not connections.has_connection("default"):
                from backend.utils.milvus_util import connect_milvus
                connect_milvus()
        except Exception:
            pass

    def answer_question(self, question: str,
                        top_k: int = 5,
                        history: List[Dict[str, str]] = None) -> Dict:
        """
        基于RAG回答用户关于四大名著的问题（同步包装）
        注意：此方法不能在已运行的 async 上下文中调用，请使用 answer_question_async
        :param question: 用户问题
        :param top_k: 每个名著集合检索的相似文本块数量
        :param history: 历史对话记录
        :return: {answer, sources, references}
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                raise RuntimeError("answer_question cannot be called from running async context, use answer_question_async")
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(
            self.answer_question_async(question, top_k, history)
        )

    async def answer_question_async(self, question: str,
                                    top_k: int = 5,
                                    history: List[Dict[str, str]] = None,
                                    mode: str = "auto") -> Dict:
        """
        增强版异步RAG问答
        :param question: 用户问题
        :param top_k: 每个集合检索的相似文本块数量
        :param history: 历史对话记录
        :param mode: auto自动, rag仅原文, graph仅图谱, hybrid融合
        :return: {answer, sources, references, mode}
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
        self._ensure_milvus()
        target_books = await route_book(question)

        query_vector = await get_embedding(question)
        self._ensure_milvus()
        all_hits = search_specific_novels(query_vector, target_books, top_k=top_k)

        if not all_hits:
            return {
                "answer": "哼哼～俺老猪的知识库还没准备好呢！",
                "sources": [],
                "references": [],
                "mode": "rag",
                "target_books": target_books,
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
            references.append({
                "chunk_id": hit["chunk_id"],
                "novel_name": hit.get("novel_name", ""),
                "novel_name_cn": novel_cn,
                "chapter_num": hit["chapter_num"],
                "chapter_title": hit["chapter_title"],
                "content": hit["content"][:200] + "..." if len(hit["content"]) > 200 else hit["content"],
                "score": round(hit["score"], 4),
            })

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
        # 并行执行
        rag_task = self._rag_only_query(question, top_k, history)
        graph_task = self._graph_only_query(question)

        rag_result, graph_result = await asyncio.gather(rag_task, graph_task)

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

    async def answer_question_stream(self, question: str,
                                     top_k: int = 5,
                                     history: List[Dict[str, str]] = None,
                                     mode: str = "auto"):
        """
        流式RAG问答 - 支持智能路由、图谱查询、融合查询
        :param question: 用户问题
        :param top_k: 每个集合检索数量
        :param history: 历史对话
        :param mode: auto自动, rag原文, graph图谱, hybrid融合
        :yield: 逐步返回文本片段
        """
        # 判断查询模式
        if mode == "auto":
            mode = await self._detect_query_mode(question)

        if mode == "graph":
            async for chunk in self._graph_stream_query(question):
                yield chunk
            return
        elif mode == "hybrid":
            async for chunk in self._hybrid_stream_query(question, top_k, history):
                yield chunk
            return
        else:
            # RAG模式：智能路由 + 多集合检索 + 流式生成
            target_books = await route_book(question)
            query_vector = await get_embedding(question)
            self._ensure_milvus()
            all_hits = search_specific_novels(query_vector, target_books, top_k=top_k)

            if not all_hits:
                yield "哼哼～俺老猪的知识库还没准备好呢！请先导入四大名著全文。"
                return

            top_results = all_hits[:top_k * 2]
            novel_groups = {}
            for hit in top_results:
                novel_cn = hit.get("novel_name_cn", "未知")
                if novel_cn not in novel_groups:
                    novel_groups[novel_cn] = []
                novel_groups[novel_cn].append(
                    f"【第{hit['chapter_num']}回：{hit['chapter_title']}】\n{hit['content']}"
                )

            context_parts = []
            for novel_cn, parts in novel_groups.items():
                context_parts.append(f"## 《{novel_cn}》原文参考：\n" + "\n\n---\n\n".join(parts))
            context = "\n\n".join(context_parts)

            user_message = f"""请根据以下原文片段回答问题：

## 原文参考：
{context}

## 用户问题：
{question}

请用猪八戒口吻回答，并注明出处。"""

            messages = [{"role": "user", "content": user_message}]
            if history:
                messages = history[-6:] + messages

            async for chunk in chat_completion_stream(
                messages=messages,
                system_prompt=RAG_SYSTEM_PROMPT,
                temperature=0.7,
                max_tokens=800,
            ):
                yield chunk

    async def _graph_stream_query(self, question: str):
        """图谱查询的流式版本"""
        all_names = []
        for keywords in BOOK_KEYWORDS.values():
            all_names.extend(keywords)
        found_names = [name for name in all_names if name in question]

        if len(found_names) >= 2:
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
            result = self.graph_service.get_person_relations(found_names[0])
            context = f"{found_names[0]}的关系网络：\n"
            for rel in result.get("relations", [])[:10]:
                context += f"- {rel['relation_type']}：{rel['target_name']}（{rel['target_identity']}）\n"
        else:
            context = "未识别到具体人物。"

        prompt = f"""你是猪八戒，正在回答关于四大名著人物关系的问题。

## 人物关系信息：
{context}

## 用户问题：
{question}

请用猪八戒口吻回答，语气憨厚。"""

        async for chunk in chat_completion_stream(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500,
        ):
            yield chunk

    async def _hybrid_stream_query(self, question: str, top_k: int, history: List[Dict]):
        """融合查询的流式版本：先收集RAG和图谱上下文，再流式生成综合回复"""
        # 并行收集上下文
        rag_ctx_task = self._build_rag_context(question, top_k)
        graph_ctx_task = self._build_graph_context(question)

        rag_context, graph_context = await asyncio.gather(rag_ctx_task, graph_ctx_task)

        prompt = f"""你是猪八戒，综合以下信息回答用户问题。

## 原文参考：
{rag_context}

## 人物关系：
{graph_context}

## 用户问题：
{question}

请用猪八戒口吻，综合原文和人物关系给出一个完整的回答。"""

        async for chunk in chat_completion_stream(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800,
        ):
            yield chunk

    async def _build_rag_context(self, question: str, top_k: int) -> str:
        """构建RAG检索上下文（用于hybrid模式）"""
        target_books = await route_book(question)
        query_vector = await get_embedding(question)
        self._ensure_milvus()
        all_hits = search_specific_novels(query_vector, target_books, top_k=top_k)

        if not all_hits:
            return "知识库暂无相关数据。"

        top_results = all_hits[:top_k * 2]
        novel_groups = {}
        for hit in top_results:
            novel_cn = hit.get("novel_name_cn", "未知")
            if novel_cn not in novel_groups:
                novel_groups[novel_cn] = []
            novel_groups[novel_cn].append(
                f"【第{hit['chapter_num']}回：{hit['chapter_title']}】\n{hit['content']}"
            )

        parts = []
        for novel_cn, chunks in novel_groups.items():
            parts.append(f"## 《{novel_cn}》原文参考：\n" + "\n\n---\n\n".join(chunks))
        return "\n\n".join(parts)

    async def _build_graph_context(self, question: str) -> str:
        """构建图谱查询上下文（用于hybrid模式）"""
        all_names = []
        for keywords in BOOK_KEYWORDS.values():
            all_names.extend(keywords)
        found_names = [name for name in all_names if name in question]

        if len(found_names) >= 2:
            result = self.graph_service.find_relation_path(found_names[0], found_names[1])
            ctx = f"人物关系：{found_names[0]} 和 {found_names[1]}\n"
            if result.get("path"):
                path_str = " → ".join([
                    f"{step['from']}({step['relation']})"
                    for step in result["path"]
                ]) + f" → {found_names[1]}"
                ctx += f"关系路径：{path_str}\n"
            else:
                ctx += "两人没有直接关系记录。\n"
            return ctx
        elif len(found_names) == 1:
            result = self.graph_service.get_person_relations(found_names[0])
            ctx = f"{found_names[0]}的关系网络：\n"
            for rel in result.get("relations", [])[:10]:
                ctx += f"- {rel['relation_type']}：{rel['target_name']}（{rel['target_identity']}）\n"
            return ctx
        return "未识别到具体人物。"

    def get_collection_info(self) -> Dict:
        """获取全部四大名著向量库状态"""
        stats = get_all_collections()
        total_entities = sum(s["num_entities"] for s in stats.values())
        ready_count = sum(1 for s in stats.values() if s["exists"] and s["num_entities"] > 0)
        return {
            "status": "ready" if ready_count > 0 else "not_initialized",
            "total_novels": len(stats),
            "ready_novels": ready_count,
            "total_entities": total_entities,
            "collections": stats,
        }
