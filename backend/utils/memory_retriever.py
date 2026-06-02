"""
记忆检索器 — 语义搜索 + 结构化排序，构建记忆提示词注入 system prompt
"""
import math
import logging
from typing import List, Dict
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class MemoryRetriever:

    def __init__(self, db: Session):
        self.db = db

    def retrieve(self, user_id: int, query: str, top_k: int = 5) -> List[Dict]:
        """检索相关记忆：Milvus 语义搜索 + MySQL 补充"""
        results = []
        seen = set()

        # Step 1: Milvus 语义搜索
        try:
            from backend.utils.embedding_util import get_embedding
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
            vec = loop.run_until_complete(get_embedding(query))

            milvus_results = self._search_milvus(user_id, vec, top_k=10)
            for r in milvus_results:
                cid = r.get("chunk_id", "")
                if cid and cid not in seen:
                    seen.add(cid)
                    results.append({
                        "content": r.get("content", ""),
                        "importance": 0.5,
                        "score": r.get("score", 0),
                        "source": "milvus",
                    })
        except Exception as e:
            logger.warning("Milvus search failed: %s", e)

        # Step 2: MySQL 补充检索
        try:
            mysql_results = self._search_mysql(user_id, limit=5)
            for r in mysql_results:
                if r["id"] not in seen:
                    seen.add(r["id"])
                    results.append({**r, "source": "mysql", "score": r["importance"] * 0.3})
        except Exception as e:
            logger.warning("MySQL search failed: %s", e)

        # Step 3: 排序
        now_days = (__import__("datetime").datetime.now() -
                     __import__("datetime").datetime(2026, 1, 1)).days
        for r in results:
            created = r.get("created_at")
            if created and hasattr(created, "days"):
                pass
            bonus = 0.3 if r.get("source") == "milvus" else 0
            r["final_score"] = r.get("score", 0) * 0.6 + r.get("importance", 0.5) * 0.3 + bonus * 0.1

        results.sort(key=lambda x: x["final_score"], reverse=True)
        top = results[:top_k]

        # Step 4: 更新访问计数
        from backend.entity.memory_fragment import MemoryFragment
        from datetime import datetime
        for r in top:
            frag_id = r.get("id")
            if frag_id:
                try:
                    self.db.query(MemoryFragment).filter(
                        MemoryFragment.id == frag_id
                    ).update({
                        "access_count": MemoryFragment.access_count + 1,
                        "last_accessed_at": datetime.now(),
                    }, synchronize_session=False)
                    self.db.commit()
                except Exception:
                    pass

        return top

    def _search_milvus(self, user_id: int, vec: List[float], top_k: int = 10) -> List[Dict]:
        from pymilvus import Collection
        coll = Collection("memory_vectors")
        coll.load()
        results = coll.search(
            data=[vec], anns_field="embedding",
            param={"metric_type": "COSINE", "params": {"nprobe": 16}},
            limit=top_k,
            expr=f"user_id == {user_id}",
            output_fields=["chunk_id", "content"],
        )
        hits = []
        for hit in results[0]:
            hits.append({
                "chunk_id": hit.entity.get("chunk_id"),
                "content": hit.entity.get("content"),
                "score": hit.score,
            })
        return hits

    def _search_mysql(self, user_id: int, limit: int = 5) -> List[Dict]:
        from backend.entity.memory_fragment import MemoryFragment
        rows = self.db.query(MemoryFragment).filter(
            MemoryFragment.user_id == user_id
        ).order_by(MemoryFragment.importance.desc()).limit(limit).all()
        return [{
            "id": r.id, "content": r.content,
            "importance": r.importance,
            "memory_type": r.memory_type,
        } for r in rows]

    def build_memory_prompt(self, user_id: int, query: str) -> str:
        """构建记忆提示词，注入 system prompt"""
        memories = self.retrieve(user_id, query)
        if not memories:
            return ""

        lines = ["[关于用户的已知信息]"]
        for m in memories[:5]:
            lines.append(f"- {m['content']}")
        lines.append("请自然地在回答中运用这些信息，不要刻意罗列。")
        return "\n".join(lines)
