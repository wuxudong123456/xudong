"""
Milvus 向量数据库工具
管理四大名著的 Milvus 集合：创建、数据插入、向量检索、跨集合搜索
每本名著使用独立的 Collection，保证语义隔离和精准匹配
"""
import logging
from typing import List, Dict, Optional
from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility,
)
from backend.config import settings

from backend.utils.embedding_util import VECTOR_DIM

logger = logging.getLogger("milvus")

# 四大名著集合名称
NOVEL_COLLECTIONS = {
    "xiyou": "novel_xiyou",       # 西游记
    "sanguo": "novel_sanguo",     # 三国演义
    "honglou": "novel_honglou",   # 红楼梦
    "shuihu": "novel_shuihu",     # 水浒传
}

# 集合对应的名著中文名
NOVEL_NAMES_CN = {
    "novel_xiyou": "西游记",
    "novel_sanguo": "三国演义",
    "novel_honglou": "红楼梦",
    "novel_shuihu": "水浒传",
}


def connect_milvus():
    """
    连接 Milvus 服务
    建立与 Milvus 服务器的连接
    """
    connections.connect(
        alias="default",
        host=settings.MILVUS_HOST,
        port=settings.MILVUS_PORT,
    )
    logger.info("已连接到 %s:%s", settings.MILVUS_HOST, settings.MILVUS_PORT)


def create_collection(collection_name: str, drop_if_exists: bool = False) -> Collection:
    """
    创建单个名著的向量集合
    :param collection_name: 集合名称 (如 novel_xiyou)
    :param drop_if_exists: 是否删除已存在的同名集合
    字段:
      - id: 主键 (自增)
      - chunk_id: 切片唯一标识 (如 xy_00001)
      - novel_name: 名著标识 (xiyou/sanguo/honglou/shuihu)
      - chapter_num: 章节编号
      - chapter_title: 章节标题
      - content: 原始文本内容
      - char_count: 中文字符数
      - embedding: 向量字段 (512维)
    """
    if drop_if_exists and utility.has_collection(collection_name):
        utility.drop_collection(collection_name)
        logger.info("已删除旧集合: %s", collection_name)

    if utility.has_collection(collection_name):
        logger.info("集合 %s 已存在，跳过创建", collection_name)
        return Collection(collection_name)

    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="chunk_id", dtype=DataType.VARCHAR, max_length=20),
        FieldSchema(name="novel_name", dtype=DataType.VARCHAR, max_length=20),
        FieldSchema(name="chapter_num", dtype=DataType.INT64),
        FieldSchema(name="chapter_title", dtype=DataType.VARCHAR, max_length=300),
        FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=5000),
        FieldSchema(name="char_count", dtype=DataType.INT64),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=VECTOR_DIM),
    ]

    novel_cn = NOVEL_NAMES_CN.get(collection_name, collection_name)
    schema = CollectionSchema(fields, description=f"《{novel_cn}》全文语义切片向量库")
    collection = Collection(collection_name, schema)
    logger.info("集合 %s（%s）创建成功", collection_name, novel_cn)
    return collection


def create_all_collections(drop_if_exists: bool = False) -> List[Collection]:
    """
    创建全部四大名著向量集合
    :param drop_if_exists: 是否删除已存在的集合
    :return: 集合对象列表
    """
    collections = []
    for novel_key, coll_name in NOVEL_COLLECTIONS.items():
        coll = create_collection(coll_name, drop_if_exists=drop_if_exists)
        collections.append(coll)
    return collections


def create_index(collection: Collection):
    """
    为向量字段创建 IVF_FLAT 索引
    使用余弦相似度 (COSINE) 度量，保证语义向量匹配的精准度
    """
    index_params = {
        "metric_type": "COSINE",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 128},
    }
    collection.create_index(field_name="embedding", index_params=index_params)
    logger.info("IVF_FLAT 索引创建成功 (nlist=128, metric=COSINE) → %s", collection.name)


def insert_chunks(collection: Collection, chunks: List[Dict], embeddings: List[List[float]]):
    """
    批量插入切片数据和对应向量到指定集合
    :param collection: Milvus集合对象
    :param chunks: 切片列表 [{chunk_id, novel_name, chapter_num, chapter_title, content, char_count}]
    :param embeddings: 对应向量列表
    """
    data = [
        [c["chunk_id"] for c in chunks],
        [c.get("novel_name", "") for c in chunks],
        [c["chapter_num"] for c in chunks],
        [c["chapter_title"] for c in chunks],
        [c["content"] for c in chunks],
        [c["char_count"] for c in chunks],
        embeddings,
    ]
    collection.insert(data)
    collection.flush()
    logger.info("%s: 成功插入 %d 条切片数据", collection.name, len(chunks))


def search_similar(collection: Collection, query_vector: List[float],
                   top_k: int = 5) -> List[Dict]:
    """
    单集合向量相似度检索
    :param collection: Milvus集合对象
    :param query_vector: 查询向量 (1536维)
    :param top_k: 返回最相似的K条结果
    :return: [{chunk_id, novel_name, chapter_num, chapter_title, content, score}, ...]
    """
    collection.load()
    search_params = {"metric_type": "COSINE", "params": {"nprobe": 16}}
    results = collection.search(
        data=[query_vector],
        anns_field="embedding",
        param=search_params,
        limit=top_k,
        output_fields=["chunk_id", "novel_name", "chapter_num", "chapter_title", "content", "char_count"],
    )

    novel_cn = NOVEL_NAMES_CN.get(collection.name, collection.name)
    hits = []
    for hit in results[0]:
        hits.append({
            "chunk_id": hit.entity.get("chunk_id"),
            "novel_name": hit.entity.get("novel_name"),
            "novel_name_cn": novel_cn,
            "chapter_num": hit.entity.get("chapter_num"),
            "chapter_title": hit.entity.get("chapter_title"),
            "content": hit.entity.get("content"),
            "char_count": hit.entity.get("char_count"),
            "score": hit.score,
            "collection": collection.name,
        })
    return hits


def search_all_novels(query_vector: List[float], top_k: int = 5) -> List[Dict]:
    """
    跨四大名著集合检索，汇总所有名著的相似文本块
    在每个集合中检索top_k条，然后按相似度分数合并排序
    :param query_vector: 查询向量 (1536维)
    :param top_k: 每个集合返回的最相似结果数
    :return: 按相似度降序排列的结果列表
    """
    all_hits = []
    for novel_key, coll_name in NOVEL_COLLECTIONS.items():
        if not utility.has_collection(coll_name):
            continue
        collection = Collection(coll_name)
        try:
            hits = search_similar(collection, query_vector, top_k=top_k)
            all_hits.extend(hits)
        except Exception as e:
            logger.error("检索 %s 失败: %s", coll_name, e)

    # 按余弦相似度降序排列（score越大越相似）
    all_hits.sort(key=lambda x: x["score"], reverse=True)
    return all_hits


def search_specific_novels(query_vector: List[float], novel_names: List[str], top_k: int = 5) -> List[Dict]:
    """
    指定集合检索
    :param query_vector: 查询向量
    :param novel_names: 集合名列表，如 ["novel_sanguo", "novel_honglou"]
    :param top_k: 每个集合返回的最相似结果数
    :return: 按相似度降序排列的结果列表
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


def get_collection(collection_name: str = None) -> Optional[Collection]:
    """获取已存在的集合对象"""
    if collection_name:
        if utility.has_collection(collection_name):
            return Collection(collection_name)
        return None
    # 默认返回西游记集合（向后兼容）
    default_name = NOVEL_COLLECTIONS["xiyou"]
    if utility.has_collection(default_name):
        return Collection(default_name)
    return None


def get_all_collections() -> Dict[str, Dict]:
    """获取所有名著集合的统计信息"""
    stats = {}
    for novel_key, coll_name in NOVEL_COLLECTIONS.items():
        if utility.has_collection(coll_name):
            collection = Collection(coll_name)
            stats[novel_key] = {
                "name": coll_name,
                "name_cn": NOVEL_NAMES_CN.get(coll_name, coll_name),
                "num_entities": collection.num_entities,
                "exists": True,
            }
        else:
            stats[novel_key] = {
                "name": coll_name,
                "name_cn": NOVEL_NAMES_CN.get(coll_name, coll_name),
                "num_entities": 0,
                "exists": False,
            }
    return stats
