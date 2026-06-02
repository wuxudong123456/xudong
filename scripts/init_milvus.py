"""
初始化 Milvus 向量数据库
创建四大名著（西游记/三国演义/红楼梦/水浒传）文本切片存储集合并建立索引
运行: python scripts/init_milvus.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.utils.milvus_util import (
    connect_milvus, create_all_collections, create_index, NOVEL_COLLECTIONS
)


def main():
    """
    初始化四大名著 Milvus 集合
    1. 连接到Milvus服务
    2. 为每本名著创建独立集合（如已存在则跳过）
    3. 为每个集合创建IVF_FLAT索引
    """
    print("=" * 60)
    print("  四大名著 Milvus 向量数据库初始化")
    print("=" * 60)

    # 1. 连接
    connect_milvus()

    # 2. 创建全部四个集合
    collections = create_all_collections(drop_if_exists=False)

    # 3. 为每个集合创建索引
    for collection in collections:
        create_index(collection)

    # 4. 输出状态
    print(f"\n[Milvus] 集合状态:")
    for novel_key, coll_name in NOVEL_COLLECTIONS.items():
        from pymilvus import utility
        if utility.has_collection(coll_name):
            from pymilvus import Collection
            c = Collection(coll_name)
            print(f"  ✓ {coll_name} ({novel_key}) — 实体数: {c.num_entities}")
        else:
            print(f"  ✗ {coll_name} ({novel_key}) — 未创建")

    print("\n下一步: 运行 python scripts/ingest_novel.py 导入四大名著全文")


if __name__ == "__main__":
    main()
