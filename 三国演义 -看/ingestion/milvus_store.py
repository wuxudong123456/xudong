"""
MilvusClient 封装：向量入库 + 检索（使用新版 MilvusClient API）
"""
from pymilvus import MilvusClient, DataType
from pymilvus.milvus_client import IndexParams
from config import (
    MILVUS_HOST, MILVUS_PORT, MILVUS_DB_NAME,
    FILE_CHUNKS_COLLECTION, QA_PAIRS_COLLECTION,
)
from embedding import encode, encode_batch, get_dim


class Store:
    def __init__(self):
        uri = f"http://{MILVUS_HOST}:{MILVUS_PORT}"
        self.client = MilvusClient(uri=uri, db_name=MILVUS_DB_NAME)

    # ---- 创建集合 ----

    def create_file_chunks_collection(self) -> None:
        if self.client.has_collection(FILE_CHUNKS_COLLECTION):
            self.client.drop_collection(FILE_CHUNKS_COLLECTION)

        schema = self.client.create_schema(
            auto_id=True,
            enable_dynamic_field=False,
        )
        schema.add_field("id", DataType.INT64, is_primary=True)
        schema.add_field("chapter_num", DataType.INT64)
        schema.add_field("title", DataType.VARCHAR, max_length=200)
        schema.add_field("chunk_index", DataType.INT64)
        schema.add_field("content", DataType.VARCHAR, max_length=65535)
        schema.add_field("embedding", DataType.FLOAT_VECTOR, dim=get_dim())

        self.client.create_collection(
            collection_name=FILE_CHUNKS_COLLECTION,
            schema=schema,
        )

        idx = IndexParams()
        idx.add_index(
            field_name="embedding",
            index_type="IVF_FLAT",
            index_name="idx_embedding",
            metric_type="IP",
            params={"nlist": 128},
        )
        self.client.create_index(
            collection_name=FILE_CHUNKS_COLLECTION,
            index_params=idx,
        )
        self.client.load_collection(FILE_CHUNKS_COLLECTION)
        print(f"集合 {FILE_CHUNKS_COLLECTION} 创建成功")

    def create_qa_pairs_collection(self) -> None:
        if self.client.has_collection(QA_PAIRS_COLLECTION):
            self.client.drop_collection(QA_PAIRS_COLLECTION)

        schema = self.client.create_schema(
            auto_id=True,
            enable_dynamic_field=False,
        )
        schema.add_field("id", DataType.INT64, is_primary=True)
        schema.add_field("question", DataType.VARCHAR, max_length=2000)
        schema.add_field("answer", DataType.VARCHAR, max_length=65535)
        schema.add_field("source_chapter", DataType.INT64)
        schema.add_field("source_chunk_id", DataType.INT64)
        schema.add_field("embedding", DataType.FLOAT_VECTOR, dim=get_dim())

        self.client.create_collection(
            collection_name=QA_PAIRS_COLLECTION,
            schema=schema,
        )

        idx = IndexParams()
        idx.add_index(
            field_name="embedding",
            index_type="IVF_FLAT",
            index_name="idx_embedding",
            metric_type="IP",
            params={"nlist": 128},
        )
        self.client.create_index(
            collection_name=QA_PAIRS_COLLECTION,
            index_params=idx,
        )
        self.client.load_collection(QA_PAIRS_COLLECTION)
        print(f"集合 {QA_PAIRS_COLLECTION} 创建成功")

    # ---- 数据插入 ----

    def insert_file_chunks(self, chunks: list[dict]) -> None:
        texts = [f"{c['title']} {c['content'][:300]}" for c in chunks]
        vectors = encode_batch(texts)

        data = []
        for i, chunk in enumerate(chunks):
            data.append({
                "chapter_num": chunk["chapter_num"],
                "title": chunk["title"],
                "chunk_index": chunk["chunk_index"],
                "content": chunk["content"],
                "embedding": vectors[i],
            })

        self.client.insert(FILE_CHUNKS_COLLECTION, data)
        print(f"插入 {len(data)} 条文件切片")

    def insert_qa_pairs(self, qa_pairs: list[dict]) -> None:
        questions = [qa["question"] for qa in qa_pairs]
        vectors = encode_batch(questions)

        data = []
        for i, qa in enumerate(qa_pairs):
            data.append({
                "question": qa["question"],
                "answer": qa["answer"],
                "source_chapter": qa.get("source_chapter", 0),
                "source_chunk_id": qa.get("source_chunk_id", 0),
                "embedding": vectors[i],
            })

        self.client.insert(QA_PAIRS_COLLECTION, data)
        print(f"插入 {len(data)} 条问答对")

    # ---- 检索 ----

    def search_file_chunks(self, query: str, top_k: int = 5) -> list[dict]:
        query_vec = encode(query)
        results = self.client.search(
            collection_name=FILE_CHUNKS_COLLECTION,
            data=[query_vec],
            limit=top_k,
            output_fields=["chapter_num", "title", "chunk_index", "content"],
        )
        return self._format_results(results, "file_chunk")

    def search_qa_pairs(self, query: str, top_k: int = 5) -> list[dict]:
        query_vec = encode(query)
        results = self.client.search(
            collection_name=QA_PAIRS_COLLECTION,
            data=[query_vec],
            limit=top_k,
            output_fields=["question", "answer", "source_chapter", "source_chunk_id"],
        )
        return self._format_results(results, "qa_pair")

    def hybrid_search(self, query: str, top_k: int = 5) -> list[dict]:
        """混合检索两张表，按相似度合并排序"""
        combined = self.search_file_chunks(query, top_k)
        try:
            qas = self.search_qa_pairs(query, top_k)
            combined.extend(qas)
        except Exception:
            pass  # qa_pairs 集合可能还不存在
        combined.sort(key=lambda x: x["score"], reverse=True)
        return combined[:top_k]

    def _format_results(self, results: list, source_type: str) -> list[dict]:
        """统一格式化搜索结果"""
        formatted = []
        if results and len(results) > 0:
            for item in results[0]:
                entry = {
                    "id": item["id"],
                    "score": float(item["distance"]),
                    "type": source_type,
                }
                if source_type == "file_chunk":
                    entry["chapter_num"] = item["entity"].get("chapter_num", 0)
                    entry["title"] = item["entity"].get("title", "")
                    entry["chunk_index"] = item["entity"].get("chunk_index", 0)
                    entry["content"] = item["entity"].get("content", "")
                elif source_type == "qa_pair":
                    entry["question"] = item["entity"].get("question", "")
                    entry["answer"] = item["entity"].get("answer", "")
                    entry["source_chapter"] = item["entity"].get("source_chapter", 0)
                    entry["source_chunk_id"] = item["entity"].get("source_chunk_id", 0)
                formatted.append(entry)
        return formatted
